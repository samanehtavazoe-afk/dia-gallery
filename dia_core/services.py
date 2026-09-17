from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum

from .models import (
    Account,
    AccountEntry,
    AppSetting,
    BusinessTransfer,
    InventoryMovement,
    ProductVariant,
    PurchaseLine,
    ReturnRecord,
    SaleLine,
    StockBalance,
    StockLocation,
)


def _setting_decimal(key, default=0):
    raw = AppSetting.objects.filter(key=key).values_list("value", flat=True).first()
    try:
        return Decimal(str(default if raw in (None, "") else raw))
    except Exception:
        return Decimal(str(default))


def _round_toman(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def digikala_fee_for_unit(sale_price):
    """Same internal Digikala commission formula used by the reference panel.

    This function performs no network/API call. Values are local AppSetting rows and
    can later be changed from Dia Gallery settings.
    """
    price = Decimal(sale_price or 0)
    commission_rate = _setting_decimal("digikala_commission_percent", 24) / Decimal(100)
    processing_rate = _setting_decimal("digikala_processing_percent", 7) / Decimal(100)
    processing_floor = _setting_decimal("digikala_processing_floor", 36000)
    vat_rate = _setting_decimal("digikala_vat_percent", 10) / Decimal(100)
    floor_taxable = _setting_decimal("digikala_floor_taxable_part", 18000)

    commission = price * commission_rate
    raw_processing = price * processing_rate
    if raw_processing < processing_floor:
        processing = processing_floor
        taxable_processing = floor_taxable
    else:
        processing = raw_processing
        taxable_processing = processing / Decimal(2)
    vat = (commission + taxable_processing) * vat_rate
    return _round_toman(commission + processing + vat)


def _setting_text(key, default=""):
    raw = AppSetting.objects.filter(key=key).values_list("value", flat=True).first()
    return str(default if raw in (None, "") else raw).strip().lower()


def percent_fee_for_unit(sale_price, percent):
    price = Decimal(sale_price or 0)
    rate = Decimal(str(percent or 0)) / Decimal(100)
    return _round_toman(price * rate)


def sale_cost_snapshots(*, sale_price, variant, sales_channel=None, payment_provider=None):
    digikala_fee = 0
    channel_fee = 0
    channel_tax = 0
    provider_fee = 0
    provider_tax = 0

    channel_code = getattr(sales_channel, "code", "") or ""
    provider_code = getattr(payment_provider, "code", "") or ""

    if channel_code == "digikala":
        digikala_fee = digikala_fee_for_unit(sale_price)

    elif channel_code == "basalam":
        business = getattr(variant.product, "business", None)
        if business is None:
            raise ValueError("برای محاسبه کارمزد باسلام، بیزنس محصول باید مشخص باشد.")

        if business.code == "holder":
            rate = _setting_decimal("basalam_holder_commission_percent", Decimal("10.5"))
        else:
            rate = _setting_decimal("basalam_underwear_commission_percent", Decimal("14"))

        channel_fee = percent_fee_for_unit(sale_price, rate)

    if provider_code == "snapp":
        rate = _setting_decimal("snapp_commission_percent", Decimal("13"))
        tax_rate = _setting_decimal("snapp_tax_percent", Decimal("10"))
        provider_fee = percent_fee_for_unit(sale_price, rate)

        tax_base = _setting_text("snapp_tax_base", "")
        if tax_base == "fee":
            provider_tax = percent_fee_for_unit(provider_fee, tax_rate)
        elif tax_base == "gross":
            provider_tax = percent_fee_for_unit(sale_price, tax_rate)

    elif provider_code == "digipay":
        rate = _setting_decimal("digipay_commission_percent", Decimal("12"))
        provider_fee = percent_fee_for_unit(sale_price, rate)

    elif provider_code == "torobpay":
        rate = _setting_decimal("torobpay_commission_percent", Decimal("6"))
        provider_fee = percent_fee_for_unit(sale_price, rate)

    return {
        "digikala_fee_unit": digikala_fee,
        "channel_fee_unit_snapshot": channel_fee,
        "channel_tax_unit_snapshot": channel_tax,
        "provider_fee_unit_snapshot": provider_fee,
        "provider_tax_unit_snapshot": provider_tax,
    }



def main_location():
    return StockLocation.objects.get(key="main")


def stock_for(variant, location=None, *, lock=False):
    location = location or main_location()
    obj, _ = StockBalance.objects.get_or_create(
        variant=variant,
        location=location,
        defaults={"qty": 0},
    )
    if lock:
        return StockBalance.objects.select_for_update().get(pk=obj.pk)
    return obj


def sale_metrics(line):
    qty = int(line.quantity or 0)
    gross = qty * int(line.sale_price or 0)

    digikala_fee = qty * int(line.digikala_fee_unit or 0)
    channel_fee = qty * int(line.channel_fee_unit_snapshot or 0)
    channel_tax = qty * int(line.channel_tax_unit_snapshot or 0)
    provider_fee = qty * int(line.provider_fee_unit_snapshot or 0)
    provider_tax = qty * int(line.provider_tax_unit_snapshot or 0)
    cogs = qty * int(line.unit_cost_snapshot or 0)

    total_fees = (
        digikala_fee
        + channel_fee
        + channel_tax
        + provider_fee
        + provider_tax
    )

    profit = gross - total_fees - cogs

    return {
        "gross": gross,
        "digikala_fee": digikala_fee,
        "channel_fee": channel_fee,
        "channel_tax": channel_tax,
        "provider_fee": provider_fee,
        "provider_tax": provider_tax,
        "total_fees": total_fees,
        "cogs": cogs,
        "profit": profit,
        "quantity": qty,
        "margin": (profit * 100 / gross) if gross else 0,
    }


@transaction.atomic
def sync_sale_inventory(line):
    line = SaleLine.objects.select_for_update().select_related("variant", "day").get(pk=line.pk)
    target = max(0, int(line.quantity or 0))
    applied = max(0, int(line.inventory_applied_quantity or 0))
    delta = target - applied
    if not delta:
        return 0

    location = main_location()
    balance = stock_for(line.variant, location, lock=True)
    balance.qty = int(balance.qty or 0) - delta
    balance.save(update_fields=["qty"])
    InventoryMovement.objects.create(
        date=line.day.date,
        movement_type=InventoryMovement.SALE,
        variant=line.variant,
        location=location,
        delta=-delta,
        reference=f"sale:{line.id}",
    )
    line.inventory_applied_quantity = target
    line.save(update_fields=["inventory_applied_quantity", "updated_at"])
    return delta


@transaction.atomic
def sync_purchase_inventory(line):
    line = PurchaseLine.objects.select_for_update().select_related("variant").get(pk=line.pk)
    target = max(0, int(line.quantity or 0))
    applied = max(0, int(line.inventory_applied_quantity or 0))
    delta = target - applied
    if not delta:
        return 0

    location = main_location()
    balance = stock_for(line.variant, location, lock=True)
    balance.qty = int(balance.qty or 0) + delta
    balance.save(update_fields=["qty"])
    InventoryMovement.objects.create(
        date=line.date,
        movement_type=InventoryMovement.PURCHASE,
        variant=line.variant,
        location=location,
        delta=delta,
        reference=f"purchase:{line.id}",
        note=line.note,
    )
    line.inventory_applied_quantity = target
    line.save(update_fields=["inventory_applied_quantity", "updated_at"])
    return delta


@transaction.atomic
def create_return(*, date, variant, quantity, note=""):
    qty = max(0, int(quantity or 0))
    if qty <= 0:
        raise ValueError("تعداد مرجوعی باید بیشتر از صفر باشد.")
    row = ReturnRecord.objects.create(date=date, variant=variant, quantity=qty, note=note or "")
    location = main_location()
    balance = stock_for(variant, location, lock=True)
    balance.qty = int(balance.qty or 0) + qty
    balance.save(update_fields=["qty"])
    InventoryMovement.objects.create(
        date=date,
        movement_type=InventoryMovement.RETURN,
        variant=variant,
        location=location,
        delta=qty,
        reference=f"return:{row.id}",
        note=note or "",
    )
    return row


@transaction.atomic
def create_adjustment(*, date, variant, location, delta, note=""):
    delta = int(delta or 0)
    if delta == 0:
        raise ValueError("مقدار اصلاح نمی‌تواند صفر باشد.")
    from .models import InventoryAdjustment

    row = InventoryAdjustment.objects.create(
        date=date,
        variant=variant,
        location=location,
        delta=delta,
        note=note or "",
    )
    balance = stock_for(variant, location, lock=True)
    balance.qty = int(balance.qty or 0) + delta
    balance.save(update_fields=["qty"])
    InventoryMovement.objects.create(
        date=date,
        movement_type=InventoryMovement.ADJUST,
        variant=variant,
        location=location,
        delta=delta,
        reference=f"adjust:{row.id}",
        note=note or "",
    )
    return row


def account_balance(account):
    entries = account.entries.aggregate(v=Sum("delta"))["v"] or 0
    return int(account.opening_balance or 0) + int(entries)


def create_account_entry(*, account, date, delta, title, reference="", note=""):
    return AccountEntry.objects.create(
        account=account,
        date=date,
        delta=int(delta),
        title=title,
        reference=reference,
        note=note or "",
    )


def business_transfer_position(business):
    given = (
        BusinessTransfer.objects
        .filter(from_business=business)
        .aggregate(v=Sum("amount"))["v"]
        or 0
    )
    received = (
        BusinessTransfer.objects
        .filter(to_business=business)
        .aggregate(v=Sum("amount"))["v"]
        or 0
    )

    net = int(given) - int(received)

    return {
        "receivable": max(net, 0),
        "payable": max(-net, 0),
        "net": net,
    }


def counterparty_position(counterparty):
    payable = 0
    receivable = 0

    for account in counterparty.accounts.filter(active=True):
        balance = account_balance(account)

        if account.kind == Account.Kind.PAYABLE:
            payable += balance
        elif account.kind == Account.Kind.RECEIVABLE:
            receivable += balance

    return {
        "payable": payable,
        "receivable": receivable,
        "net": receivable - payable,
    }

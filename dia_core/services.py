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
    SaleOrder,
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



def basalam_installment_plan(amount):
    amount = Decimal(amount or 0)

    down_percent = _setting_decimal(
        "basalam_installment_down_payment_percent",
        Decimal("25"),
    )
    monthly_percent = _setting_decimal(
        "basalam_installment_monthly_percent",
        Decimal("3.5"),
    )
    installment_count = int(
        _setting_decimal(
            "basalam_installment_count",
            Decimal("2"),
        )
    )

    down_payment = _round_toman(
        amount * down_percent / Decimal("100")
    )
    financed_amount = int(amount) - down_payment

    if installment_count <= 0:
        raise ValueError("تعداد اقساط باسلام باید بیشتر از صفر باشد.")

    monthly_rate = monthly_percent / Decimal("100")

    if monthly_rate == 0:
        installment_amount = _round_toman(
            Decimal(financed_amount) / installment_count
        )
    else:
        factor = (Decimal("1") + monthly_rate) ** installment_count
        installment_amount = _round_toman(
            Decimal(financed_amount)
            * monthly_rate
            * factor
            / (factor - Decimal("1"))
        )

    installments_total = installment_amount * installment_count
    total_payable = down_payment + installments_total

    return {
        "down_payment": down_payment,
        "financed_amount": financed_amount,
        "installment_count": installment_count,
        "installment_amount": installment_amount,
        "installments_total": installments_total,
        "total_payable": total_payable,
        "price_increase": total_payable - int(amount),
    }



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


def sale_payment_mode(*, sales_channel=None, payment_provider=None):
    channel_code = (getattr(sales_channel, "code", "") or "").strip().lower()
    provider_code = (getattr(payment_provider, "code", "") or "").strip().lower()

    if channel_code in {"digikala", "basalam"}:
        return "platform_receivable"
    if provider_code in {"snapp", "digipay", "torobpay"}:
        return "platform_receivable"
    return "cash"


def default_sale_payment_status(*, sales_channel=None, payment_provider=None):
    if sale_payment_mode(
        sales_channel=sales_channel,
        payment_provider=payment_provider,
    ) == "platform_receivable":
        return SaleOrder.PaymentStatus.PENDING
    return SaleOrder.PaymentStatus.RECEIVED


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
    gross = qty * int(line.sale_price or 0) + int(line.basalam_installment_increase or 0)

    digikala_fee = qty * int(line.digikala_fee_unit or 0)
    channel_fee = int(line.channel_fee_total_snapshot or 0) or qty * int(line.channel_fee_unit_snapshot or 0)
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



def _holder_variant_for_bucket(bucket):
    aliases = {
        "small": {"s", "small", "کوچک"},
        "medium": {"m", "medium", "متوسط"},
        "large": {"l", "large", "بزرگ"},
    }
    wanted = aliases[bucket]

    candidates = list(
        ProductVariant.objects.filter(
            active=True,
            product__active=True,
            product__business__code="holder",
            size__active=True,
        )
        .select_related("product", "size", "color")
        .order_by("id")
    )

    matches = [
        row
        for row in candidates
        if (row.size.name or "").strip().lower() in wanted
    ]

    if len(matches) != 1:
        raise ValueError(
            f"برای سایز {bucket} هولدر باید دقیقاً یک واریانت فعال تعریف شده باشد."
        )

    return matches[0]


@transaction.atomic
def sync_holder_direct_inventory(order):
    from .models import HolderDirectOrder

    order = HolderDirectOrder.objects.select_for_update().get(pk=order.pk)
    location = main_location()
    result = {}

    for bucket in ("small", "medium", "large"):
        target = max(
            0,
            int(getattr(order, f"quantity_{bucket}") or 0),
        )

        variant = _holder_variant_for_bucket(bucket)
        reference = f"holder-order:{order.id}:{bucket}"

        moved_total = (
            InventoryMovement.objects.filter(
                movement_type=InventoryMovement.SALE,
                reference=reference,
            )
            .aggregate(total=Sum("delta"))["total"]
            or 0
        )

        applied = max(0, -int(moved_total))
        delta = target - applied

        if delta:
            balance = stock_for(variant, location, lock=True)
            balance.qty = int(balance.qty or 0) - delta
            balance.save(update_fields=["qty"])

            InventoryMovement.objects.create(
                date=order.date,
                movement_type=InventoryMovement.SALE,
                variant=variant,
                location=location,
                delta=-delta,
                reference=reference,
                note=f"فروش مستقیم هولدر - {order.customer_name}",
            )

        result[bucket] = delta

    return result


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

    available = int(balance.qty or 0)
    if delta > 0 and delta > available:
        raise ValueError(
            f"موجودی کافی برای {line.variant} نیست. "
            f"موجودی فعلی: {available}"
        )

    balance.qty = available - delta
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


def _counterparty_receivable_account(counterparty):
    account = (
        Account.objects
        .filter(
            counterparty=counterparty,
            kind=Account.Kind.RECEIVABLE,
            active=True,
        )
        .first()
    )
    if account:
        return account

    title = f"طلب از {counterparty.title}"
    if Account.objects.filter(title=title).exists():
        title = f"طلب از {counterparty.title} - {counterparty.business.title}"

    return Account.objects.create(
        title=title,
        kind=Account.Kind.RECEIVABLE,
        business=counterparty.business,
        counterparty=counterparty,
        opening_balance=0,
    )


@transaction.atomic
def create_counterparty_receivable(
    *,
    counterparty,
    date,
    amount,
    note="",
):
    amount = int(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ طلب باید بیشتر از صفر باشد.")

    if not counterparty.receivable_enabled:
        raise ValueError("ثبت طلب برای این طرف حساب فعال نیست.")

    account = _counterparty_receivable_account(counterparty)

    create_account_entry(
        account=account,
        date=date,
        delta=amount,
        title=f"ثبت طلب از {counterparty.title}",
        reference=f"counterparty-receivable:{counterparty.id}",
        note=note,
    )

    return account


@transaction.atomic
def settle_counterparty_receivable(
    *,
    counterparty,
    bank_account,
    date,
    amount,
    note="",
):
    amount = int(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ تسویه باید بیشتر از صفر باشد.")

    if not counterparty.receivable_enabled:
        raise ValueError("تسویه طلب برای این طرف حساب فعال نیست.")

    if bank_account.kind != Account.Kind.CASH:
        raise ValueError("حساب مقصد باید حساب بانکی یا نقد باشد.")

    account = _counterparty_receivable_account(counterparty)

    account = Account.objects.select_for_update().get(pk=account.pk)
    bank_account = Account.objects.select_for_update().get(
        pk=bank_account.pk
    )

    current_receivable = account_balance(account)

    if amount > current_receivable:
        raise ValueError("مبلغ تسویه از مانده طلب بیشتر است.")

    create_account_entry(
        account=account,
        date=date,
        delta=-amount,
        title=f"تسویه طلب از {counterparty.title}",
        reference=f"counterparty-settlement:{counterparty.id}",
        note=note,
    )

    create_account_entry(
        account=bank_account,
        date=date,
        delta=amount,
        title=f"دریافت از {counterparty.title}",
        reference=f"counterparty-settlement:{counterparty.id}",
        note=note,
    )

    return account

def platform_receivable_totals():
    totals = {
        "digikala": 0,
        "basalam": 0,
        "snapp": 0,
        "digipay": 0,
        "torobpay": 0,
    }

    orders = (
        SaleOrder.objects
        .filter(payment_status=SaleOrder.PaymentStatus.PENDING)
        .select_related("sales_channel", "payment_provider")
        .prefetch_related("lines")
    )

    for order in orders:
        channel_code = (order.sales_channel.code or "").strip().lower()
        provider_code = (
            (order.payment_provider.code or "").strip().lower()
            if order.payment_provider
            else ""
        )

        if channel_code in {"digikala", "basalam"}:
            bucket = channel_code
        elif provider_code in {"snapp", "digipay", "torobpay"}:
            bucket = provider_code
        else:
            continue

        amount = (
            int(order.shipping_collected or 0)
            + int(order.provider_fee_collected or 0)
        )

        for line in order.lines.all():
            qty = int(line.quantity or 0)

            amount += qty * int(line.sale_price or 0) + int(line.basalam_installment_increase or 0)
            amount -= qty * int(line.digikala_fee_unit or 0)
            amount -= int(line.channel_fee_total_snapshot or 0) or qty * int(line.channel_fee_unit_snapshot or 0)
            amount -= qty * int(line.channel_tax_unit_snapshot or 0)
            amount -= qty * int(line.provider_fee_unit_snapshot or 0)
            amount -= qty * int(line.provider_tax_unit_snapshot or 0)

        totals[bucket] += amount

    return totals



@transaction.atomic
def record_holder_receipt(
    *,
    order,
    amount,
    receipt_type,
    recipient,
    date,
    note="",
):
    from .models import HolderDirectOrder, HolderDirectReceipt

    amount = int(amount or 0)
    if amount <= 0:
        raise ValueError("مبلغ دریافت باید بیشتر از صفر باشد.")

    if receipt_type not in HolderDirectReceipt.ReceiptType.values:
        raise ValueError("نوع دریافت نامعتبر است.")

    if recipient not in HolderDirectReceipt.Recipient.values:
        raise ValueError("دریافت‌کننده نامعتبر است.")

    order = HolderDirectOrder.objects.select_for_update().get(pk=order.pk)

    if amount > order.remaining_balance:
        raise ValueError("مبلغ دریافت از مانده مشتری بیشتر است.")

    receipt = HolderDirectReceipt.objects.create(
        order=order,
        amount=amount,
        receipt_type=receipt_type,
        recipient=recipient,
        date=date,
        note=note or "",
    )

    if recipient == HolderDirectReceipt.Recipient.SAMANEH:
        bank_account = (
            Account.objects
            .filter(kind=Account.Kind.CASH, active=True)
            .order_by("id")
            .first()
        )
        if bank_account is None:
            raise ValueError("حساب بانکی فعالی تعریف نشده است.")

        bank_account = Account.objects.select_for_update().get(
            pk=bank_account.pk
        )

        create_account_entry(
            account=bank_account,
            date=date,
            delta=amount,
            title="دریافت فروش هولدر",
            reference=f"holder-receipt:{receipt.id}",
            note=note,
        )

    return receipt

def apply_basalam_installment_pricing(order):
    channel_code = (
        (order.sales_channel.code or "").strip().lower()
        if order.sales_channel
        else ""
    )

    if channel_code != "basalam":
        return

    lines = list(
        order.lines.select_related(
            "variant__product__business",
            "sales_channel",
            "payment_provider",
        ).order_by("id")
    )

    if order.basalam_payment_type != "installment":
        order.basalam_down_payment = 0
        order.basalam_installment_count = 0
        order.basalam_installment_amount = 0
        order.basalam_price_increase = 0
        order.basalam_total_payable = 0
        order.save(update_fields=[
            "basalam_down_payment",
            "basalam_installment_count",
            "basalam_installment_amount",
            "basalam_price_increase",
            "basalam_total_payable",
            "updated_at",
        ])
        for line in lines:
            qty = int(line.quantity or 0)
            base_price = int(line.base_sale_price or line.sale_price or 0)

            line.basalam_installment_increase = 0

            snapshots = sale_cost_snapshots(
                sale_price=base_price,
                variant=line.variant,
                sales_channel=line.sales_channel,
                payment_provider=line.payment_provider,
            )
            for key, value in snapshots.items():
                setattr(line, key, value)

            total_snapshots = sale_cost_snapshots(
                sale_price=qty * base_price,
                variant=line.variant,
                sales_channel=line.sales_channel,
                payment_provider=line.payment_provider,
            )
            line.channel_fee_total_snapshot = total_snapshots["channel_fee_unit_snapshot"]

            line.save(update_fields=[
                "basalam_installment_increase",
                "digikala_fee_unit",
                "channel_fee_unit_snapshot",
                "channel_fee_total_snapshot",
                "channel_tax_unit_snapshot",
                "provider_fee_unit_snapshot",
                "provider_tax_unit_snapshot",
                "updated_at",
            ])

        return

    base_total = sum(
        int(line.quantity or 0)
        * int(line.base_sale_price or line.sale_price or 0)
        for line in lines
    )

    plan = basalam_installment_plan(base_total)

    order.basalam_down_payment = plan["down_payment"]
    order.basalam_installment_count = plan["installment_count"]
    order.basalam_installment_amount = plan["installment_amount"]
    order.basalam_price_increase = plan["price_increase"]
    order.basalam_total_payable = plan["total_payable"]
    order.save(update_fields=[
        "basalam_down_payment",
        "basalam_installment_count",
        "basalam_installment_amount",
        "basalam_price_increase",
        "basalam_total_payable",
        "updated_at",
    ])

    remaining = plan["price_increase"]

    for index, line in enumerate(lines):
        qty = int(line.quantity or 0)
        base_line_total = qty * int(
            line.base_sale_price or line.sale_price or 0
        )

        if index == len(lines) - 1:
            increase = remaining
        elif base_total > 0:
            increase = _round_toman(
                Decimal(plan["price_increase"])
                * Decimal(base_line_total)
                / Decimal(base_total)
            )
            remaining -= increase
        else:
            increase = 0

        line.basalam_installment_increase = max(0, increase)

        final_line_total = (
            base_line_total
            + line.basalam_installment_increase
        )

        if qty > 0:
            effective_unit_price = (
                Decimal(final_line_total) / Decimal(qty)
            )
            snapshots = sale_cost_snapshots(
                sale_price=effective_unit_price,
                variant=line.variant,
                sales_channel=line.sales_channel,
                payment_provider=line.payment_provider,
            )

            for key, value in snapshots.items():
                setattr(line, key, value)
        total_snapshots = sale_cost_snapshots(
            sale_price=final_line_total,
            variant=line.variant,
            sales_channel=line.sales_channel,
            payment_provider=line.payment_provider,
        )
        line.channel_fee_total_snapshot = total_snapshots["channel_fee_unit_snapshot"]

        line.save(update_fields=[
            "basalam_installment_increase",
            "digikala_fee_unit",
            "channel_fee_unit_snapshot",
            "channel_fee_total_snapshot",
            "channel_tax_unit_snapshot",
            "provider_fee_unit_snapshot",
            "provider_tax_unit_snapshot",
            "updated_at",
        ])

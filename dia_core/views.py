from collections import defaultdict
from datetime import date, timedelta

import jdatetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .dateutils import format_jalali, jalali_month_bounds, month_calendar, parse_jalali_date
from .models import (
    Account,
    AccountEntry,
    Business,
    AppSetting,
    Color,
    InventoryMovement,
    Payment,
    Product,
    ProductVariant,
    PurchaseLine,
    Receipt,
    ReturnRecord,
    SaleDay,
    SaleLine,
    SaleOrder,
    SalesChannel,
    VariantChannelPrice,
    PaymentProvider,
    Size,
    StockBalance,
    StockLocation,
)
from .services import (
    account_balance,
    create_account_entry,
    create_adjustment,
    create_return,
    digikala_fee_for_unit,
    main_location,
    sale_cost_snapshots,
    sale_metrics,
    stock_for,
    sync_purchase_inventory,
    sync_sale_inventory,
)


def _int(value, default=0):
    try:
        if value in (None, ""):
            return int(default or 0)
        return int(str(value).replace(" ", "").replace(",", "").replace("٬", "").strip())
    except (TypeError, ValueError):
        return int(default or 0)


def _empty_metrics():
    return {
        "gross": 0,
        "digikala_fee": 0,
        "channel_fee": 0,
        "channel_tax": 0,
        "provider_fee": 0,
        "provider_tax": 0,
        "shipping_cost": 0,
        "shipping_collected": 0,
        "provider_fee_collected": 0,
        "customer_total": 0,
        "total_fees": 0,
        "cogs": 0,
        "profit": 0,
        "quantity": 0,
        "margin": 0,
    }


def _sum_lines(lines):
    total = _empty_metrics()
    seen_orders = set()

    for line in lines:
        row = sale_metrics(line)

        for key in (
            "gross",
            "digikala_fee",
            "channel_fee",
            "channel_tax",
            "provider_fee",
            "provider_tax",
            "total_fees",
            "cogs",
            "profit",
            "quantity",
        ):
            total[key] += row[key]

        if line.order_id and line.order_id not in seen_orders:
            seen_orders.add(line.order_id)
            order = line.order

            shipping_cost = int(order.shipping_cost or 0)
            shipping_collected = int(order.shipping_collected or 0)
            provider_collected = int(order.provider_fee_collected or 0)

            total["shipping_cost"] += shipping_cost
            total["shipping_collected"] += shipping_collected
            total["provider_fee_collected"] += provider_collected
            total["total_fees"] += shipping_cost

            total["profit"] += (
                shipping_collected
                + provider_collected
                - shipping_cost
            )

    total["customer_total"] = (
        total["gross"]
        + total["shipping_collected"]
        + total["provider_fee_collected"]
    )

    total["margin"] = (
        total["profit"] * 100 / total["gross"]
        if total["gross"]
        else 0
    )

    return total


@login_required
def dashboard(request):
    today = date.today()
    month_start, month_next, month_label = jalali_month_bounds(today)
    today_lines = list(
        SaleLine.objects.filter(day__date=today, quantity__gt=0).select_related("variant__product", "variant__size", "variant__color")
    )
    month_lines = list(
        SaleLine.objects.filter(day__date__gte=month_start, day__date__lt=month_next, quantity__gt=0)
        .select_related("variant__product", "variant__size", "variant__color")
    )
    today_metrics = _sum_lines(today_lines)
    month_metrics = _sum_lines(month_lines)

    chart_days = list(
        SaleDay.objects.filter(date__lte=today, lines__quantity__gt=0).distinct().order_by("-date")[:14]
    )
    chart_days.sort(key=lambda row: row.date)
    chart_labels, chart_sales, chart_profit = [], [], []
    for sale_day in chart_days:
        lines = list(sale_day.lines.filter(quantity__gt=0))
        metrics = _sum_lines(lines)
        chart_labels.append(format_jalali(sale_day.date)[5:])
        chart_sales.append(metrics["gross"])
        chart_profit.append(metrics["profit"])

    threshold = _int(AppSetting.objects.filter(key="low_stock_threshold").values_list("value", flat=True).first(), 10)
    location = StockLocation.objects.filter(key="main").first()
    alerts = []
    if location:
        low = (
            StockBalance.objects.filter(location=location, variant__active=True, variant__product__active=True, qty__lt=threshold)
            .select_related("variant__product", "variant__size", "variant__color")
            .order_by("qty", "variant__product__code")[:30]
        )
        for balance in low:
            v = balance.variant
            alerts.append({
                "title": f"{v.product.code} / {v.size.name} / {v.color.name}",
                "detail": f"موجودی: {balance.qty} عدد",
            })

    return render(request, "dia_core/dashboard.html", {
        "today_j": format_jalali(today),
        "month_label": month_label,
        "today_metrics": today_metrics,
        "month_metrics": month_metrics,
        "chart_labels": chart_labels,
        "chart_sales": chart_sales,
        "chart_profit": chart_profit,
        "alerts": alerts,
    })


@login_required
def sale_calendar(request):
    try:
        cal = month_calendar(request.GET.get("jy"), request.GET.get("jm"))
    except Exception:
        cal = month_calendar()
    existing = {
        (jdatetime.date.fromgregorian(date=row.date).day): row
        for row in SaleDay.objects.filter(
            date__gte=jdatetime.date(cal["jy"], cal["jm"], 1).togregorian(),
            date__lt=(
                jdatetime.date(cal["jy"] + 1, 1, 1).togregorian()
                if cal["jm"] == 12
                else jdatetime.date(cal["jy"], cal["jm"] + 1, 1).togregorian()
            ),
        ).prefetch_related("lines")
    }
    day_meta = {}
    for day_num, row in existing.items():
        day_meta[day_num] = {
            "id": row.id,
            "has_sales": any(int(line.quantity or 0) > 0 for line in row.lines.all()),
        }
    cal["day_meta"] = day_meta
    return render(request, "dia_core/sales_calendar.html", cal)


@login_required
def select_sale_day(request, jy, jm, jd):
    try:
        gregorian = jdatetime.date(int(jy), int(jm), int(jd)).togregorian()
    except Exception:
        messages.error(request, "تاریخ انتخاب‌شده معتبر نیست.")
        return redirect("sale_start")
    day, _ = SaleDay.objects.get_or_create(date=gregorian)
    return redirect("sale_day", day_id=day.id)


@login_required
@transaction.atomic
def sale_day(request, day_id):
    day = get_object_or_404(SaleDay, id=day_id)

    businesses = list(Business.objects.filter(active=True).order_by("title"))
    channels = list(SalesChannel.objects.filter(active=True).order_by("title"))
    providers = list(PaymentProvider.objects.filter(active=True).order_by("title"))

    orders_qs = (
        SaleOrder.objects
        .filter(day=day)
        .select_related("business", "sales_channel", "payment_provider")
        .prefetch_related("lines")
        .order_by("-id")
    )
    orders = list(orders_qs)

    order_id = _int(
        request.POST.get("order_id")
        if request.method == "POST"
        else request.GET.get("order")
    )

    selected_order = None
    if order_id:
        order_qs = SaleOrder.objects.filter(day=day)
        if request.method == "POST":
            order_qs = order_qs.select_for_update()

        selected_order = get_object_or_404(
            order_qs.select_related(
                "business",
                "sales_channel",
                "payment_provider",
            ),
            id=order_id,
        )

    business_id = _int(
        request.POST.get("business")
        if request.method == "POST"
        else request.GET.get("business"),
        selected_order.business_id if selected_order else 0,
    )

    channel_id = _int(
        request.POST.get("sales_channel")
        if request.method == "POST"
        else request.GET.get("channel"),
        selected_order.sales_channel_id if selected_order else 0,
    )

    provider_id = _int(
        request.POST.get("payment_provider")
        if request.method == "POST"
        else request.GET.get("provider"),
        selected_order.payment_provider_id if selected_order else 0,
    )

    selected_business = next(
        (row for row in businesses if row.id == business_id),
        None,
    )
    selected_channel = next(
        (row for row in channels if row.id == channel_id),
        None,
    )
    selected_provider = next(
        (row for row in providers if row.id == provider_id),
        None,
    )

    if selected_order is None and request.method != "POST":
        if selected_business is None and businesses:
            selected_business = businesses[0]
        if selected_channel is None and channels:
            selected_channel = channels[0]

    variants_qs = ProductVariant.objects.filter(
        active=True,
        product__active=True,
        size__active=True,
        color__active=True,
    )

    if selected_business is not None:
        variants_qs = variants_qs.filter(
            product__business=selected_business
        )
    else:
        variants_qs = variants_qs.none()

    variants = list(
        variants_qs
        .select_related("product", "product__business", "size", "color")
        .order_by(
            "product__code",
            "size__sort_order",
            "color__name",
        )
    )

    channel_price_map = {}

    if selected_channel is not None and variants:
        channel_price_map = {
            row.variant_id: int(row.sale_price or 0)
            for row in VariantChannelPrice.objects.filter(
                variant_id__in=[v.id for v in variants],
                sales_channel=selected_channel,
                active=True,
            )
        }

    existing = {}
    if selected_order is not None:
        lines_qs = selected_order.lines.all()
        if request.method == "POST":
            lines_qs = lines_qs.select_for_update()
        existing = {
            row.variant_id: row
            for row in lines_qs
        }

    if request.method == "POST":
        if selected_business is None:
            raise ValueError("بیزنس را انتخاب کن.")

        if selected_channel is None:
            raise ValueError("کانال فروش را انتخاب کن.")

        if (
            selected_order
            and selected_order.lines.exists()
            and selected_order.business_id != selected_business.id
        ):
            raise ValueError(
                "بیزنس فاکتوری که ردیف فروش دارد قابل تغییر نیست."
            )

        default_status = (
            SaleOrder.PaymentStatus.PENDING
            if selected_provider
            else SaleOrder.PaymentStatus.RECEIVED
        )

        payment_status = (
            request.POST.get("payment_status")
            or (
                selected_order.payment_status
                if selected_order
                else default_status
            )
        ).strip()

        valid_statuses = {
            value
            for value, _label in SaleOrder.PaymentStatus.choices
        }

        if payment_status not in valid_statuses:
            raise ValueError("وضعیت پرداخت معتبر نیست.")

        expected_raw = (
            request.POST.get("expected_settlement_date")
            or ""
        ).strip()

        settled_raw = (
            request.POST.get("settled_date")
            or ""
        ).strip()

        expected_date = (
            parse_jalali_date(expected_raw)
            if expected_raw
            else None
        )

        settled_date = (
            parse_jalali_date(settled_raw)
            if settled_raw
            else None
        )

        shipping_collected = max(
            0,
            _int(request.POST.get("shipping_collected")),
        )

        shipping_cost = max(
            0,
            _int(request.POST.get("shipping_cost")),
        )

        provider_collected_raw = (
            request.POST.get("provider_fee_collected")
        )

        external_reference = (
            request.POST.get("external_reference")
            or ""
        ).strip()[:140]

        note = (
            request.POST.get("note")
            or ""
        ).strip()[:250]

        pricing_context_changed = False

        if selected_order is None:
            selected_order = SaleOrder.objects.create(
                day=day,
                business=selected_business,
                sales_channel=selected_channel,
                payment_provider=selected_provider,
                payment_status=payment_status,
                external_reference=external_reference,
                shipping_collected=shipping_collected,
                shipping_cost=shipping_cost,
                provider_fee_collected=0,
                expected_settlement_date=expected_date,
                settled_date=settled_date,
                note=note,
            )
        else:
            pricing_context_changed = (
                selected_order.sales_channel_id
                != selected_channel.id
                or selected_order.payment_provider_id
                != (
                    selected_provider.id
                    if selected_provider
                    else None
                )
            )

            selected_order.business = selected_business
            selected_order.sales_channel = selected_channel
            selected_order.payment_provider = selected_provider
            selected_order.payment_status = payment_status
            selected_order.external_reference = external_reference
            selected_order.shipping_collected = shipping_collected
            selected_order.shipping_cost = shipping_cost
            selected_order.expected_settlement_date = expected_date
            selected_order.settled_date = settled_date
            selected_order.note = note

            selected_order.save(
                update_fields=[
                    "business",
                    "sales_channel",
                    "payment_provider",
                    "payment_status",
                    "external_reference",
                    "shipping_collected",
                    "shipping_cost",
                    "expected_settlement_date",
                    "settled_date",
                    "note",
                    "updated_at",
                ]
            )

        changed = 0

        for variant in variants:
            qty = max(
                0,
                _int(request.POST.get(f"qty_{variant.id}")),
            )

            current = existing.get(variant.id)

            if current is None and qty <= 0:
                continue

            default_price = channel_price_map.get(
                variant.id,
                int(variant.default_sale_price or 0),
            )

            price = max(
                0,
                _int(
                    request.POST.get(f"price_{variant.id}"),
                    default_price,
                ),
            )

            if qty > 0 and price <= 0:
                raise ValueError(
                    f"قیمت فروش {variant} باید بیشتر از صفر باشد."
                )

            if current is None:
                snapshots = sale_cost_snapshots(
                    sale_price=price,
                    variant=variant,
                    sales_channel=selected_channel,
                    payment_provider=selected_provider,
                )

                current = SaleLine.objects.create(
                    day=day,
                    order=selected_order,
                    variant=variant,
                    business=selected_business,
                    sales_channel=selected_channel,
                    payment_provider=selected_provider,
                    quantity=0,
                    sale_price=price,
                    unit_cost_snapshot=int(
                        variant.unit_cost or 0
                    ),
                    **snapshots,
                )

            else:
                old_price = int(
                    current.sale_price or 0
                )

                current.quantity = qty
                current.sale_price = price
                current.business = selected_business
                current.sales_channel = selected_channel
                current.payment_provider = selected_provider

                if (
                    int(current.unit_cost_snapshot or 0) <= 0
                    and int(
                        current.inventory_applied_quantity or 0
                    ) <= 0
                ):
                    current.unit_cost_snapshot = int(
                        variant.unit_cost or 0
                    )

                if (
                    old_price != price
                    or pricing_context_changed
                ):
                    snapshots = sale_cost_snapshots(
                        sale_price=price,
                        variant=variant,
                        sales_channel=selected_channel,
                        payment_provider=selected_provider,
                    )

                    for key, value in snapshots.items():
                        setattr(current, key, value)

                current.save(
                    update_fields=[
                        "business",
                        "sales_channel",
                        "payment_provider",
                        "quantity",
                        "sale_price",
                        "unit_cost_snapshot",
                        "digikala_fee_unit",
                        "channel_fee_unit_snapshot",
                        "channel_tax_unit_snapshot",
                        "provider_fee_unit_snapshot",
                        "provider_tax_unit_snapshot",
                        "updated_at",
                    ]
                )

            sync_sale_inventory(current)
            changed += 1

        if provider_collected_raw in (None, ""):
            auto_provider_collected = 0

            for line in selected_order.lines.all():
                qty = int(line.quantity or 0)

                auto_provider_collected += qty * (
                    int(
                        line.provider_fee_unit_snapshot
                        or 0
                    )
                    + int(
                        line.provider_tax_unit_snapshot
                        or 0
                    )
                )

            selected_order.provider_fee_collected = (
                auto_provider_collected
            )
        else:
            selected_order.provider_fee_collected = max(
                0,
                _int(provider_collected_raw),
            )

        selected_order.save(
            update_fields=[
                "provider_fee_collected",
                "updated_at",
            ]
        )

        messages.success(
            request,
            f"فاکتور فروش ذخیره شد؛ {changed} ردیف همگام شد.",
        )

        return redirect(
            f"{request.path}?order={selected_order.id}"
        )

    if selected_order is not None:
        existing = {
            row.variant_id: row
            for row in selected_order.lines.all()
        }

    rows = []

    for variant in variants:
        line = existing.get(variant.id)

        rows.append({
            "variant": variant,
            "line": line,
            "quantity": (
                int(line.quantity or 0)
                if line
                else 0
            ),
            "price": (
                int(line.sale_price or 0)
                if line
                else channel_price_map.get(
                    variant.id,
                    int(variant.default_sale_price or 0),
                )
            ),
            "metrics": (
                sale_metrics(line)
                if line
                else None
            ),
        })

    selected_lines = (
        list(selected_order.lines.all())
        if selected_order
        else []
    )

    total = _sum_lines(selected_lines)

    order_rows = []

    for order in orders:
        order_rows.append({
            "order": order,
            "total": _sum_lines(
                list(order.lines.all())
            ),
        })

    return render(
        request,
        "dia_core/sale_day.html",
        {
            "day": day,
            "date_j": format_jalali(day.date),
            "rows": rows,
            "total": total,
            "businesses": businesses,
            "channels": channels,
            "providers": providers,
            "orders": order_rows,
            "selected_order": selected_order,
            "selected_business": selected_business,
            "selected_channel": selected_channel,
            "selected_provider": selected_provider,
            "selected_expected_j": (
                format_jalali(selected_order.expected_settlement_date)
                if selected_order
                else ""
            ),
            "selected_settled_j": (
                format_jalali(selected_order.settled_date)
                if selected_order
                else ""
            ),
            "payment_status_choices": (
                SaleOrder.PaymentStatus.choices
            ),
        },
    )


@login_required
def report(request):
    today = date.today()
    period = (request.GET.get("period") or "month").strip()
    if request.GET.get("start") or request.GET.get("end"):
        start = parse_jalali_date(request.GET.get("start"), today)
        end = parse_jalali_date(request.GET.get("end"), today)
        period = "custom"
    elif period == "today":
        start = end = today
    elif period == "all":
        first = SaleDay.objects.order_by("date").first()
        start = first.date if first else today
        end = today
    else:
        start, next_start, _label = jalali_month_bounds(today)
        end = next_start - timedelta(days=1)
        period = "month"

    lines = list(
        SaleLine.objects.filter(day__date__gte=start, day__date__lte=end, quantity__gt=0)
        .select_related("day", "variant__product", "variant__size", "variant__color")
        .order_by("-day__date", "variant__product__code")
    )
    total = _sum_lines(lines)
    grouped = defaultdict(lambda: _empty_metrics())
    for line in lines:
        key = line.variant.product.code
        metrics = sale_metrics(line)
        for field in ("gross", "digikala_fee", "cogs", "profit", "quantity"):
            grouped[key][field] += metrics[field]
    products = []
    for code, metrics in grouped.items():
        metrics["margin"] = metrics["profit"] * 100 / metrics["gross"] if metrics["gross"] else 0
        products.append({"code": code, **metrics})
    products.sort(key=lambda row: row["gross"], reverse=True)

    return render(request, "dia_core/report.html", {
        "period": period,
        "start_j": format_jalali(start),
        "end_j": format_jalali(end),
        "total": total,
        "products": products,
        "lines": [{"line": line, **sale_metrics(line)} for line in lines[:250]],
    })


@login_required
@transaction.atomic
def inventory(request):
    location = main_location()
    if request.method == "POST":
        variant = get_object_or_404(ProductVariant, id=request.POST.get("variant"))
        delta = _int(request.POST.get("delta"))
        when = parse_jalali_date(request.POST.get("date"), date.today())
        create_adjustment(
            date=when,
            variant=variant,
            location=location,
            delta=delta,
            note=(request.POST.get("note") or "").strip()[:250],
        )
        messages.success(request, "اصلاح موجودی ثبت شد.")
        return redirect("inventory")

    variants = list(
        ProductVariant.objects.filter(active=True, product__active=True)
        .select_related("product", "size", "color")
        .order_by("product__code", "size__sort_order", "color__name")
    )
    balances = {
        row.variant_id: row
        for row in StockBalance.objects.filter(location=location, variant_id__in=[v.id for v in variants])
    }
    rows = []
    total_qty = 0
    total_value = 0
    for variant in variants:
        qty = int(balances.get(variant.id).qty if balances.get(variant.id) else 0)
        value = qty * int(variant.unit_cost or 0)
        total_qty += qty
        total_value += value
        rows.append({"variant": variant, "qty": qty, "value": value})
    recent = list(
        InventoryMovement.objects.select_related("variant__product", "variant__size", "variant__color")[:60]
    )
    return render(request, "dia_core/inventory.html", {
        "rows": rows,
        "variants": variants,
        "recent": recent,
        "total_qty": total_qty,
        "total_value": total_value,
        "today_j": format_jalali(date.today()),
    })


@login_required
@transaction.atomic
def returns(request):
    variants = list(
        ProductVariant.objects.filter(active=True, product__active=True)
        .select_related("product", "size", "color")
        .order_by("product__code", "size__sort_order", "color__name")
    )
    if request.method == "POST":
        variant = get_object_or_404(ProductVariant, id=request.POST.get("variant"))
        qty = max(0, _int(request.POST.get("quantity")))
        when = parse_jalali_date(request.POST.get("date"), date.today())
        create_return(
            date=when,
            variant=variant,
            quantity=qty,
            note=(request.POST.get("note") or "").strip()[:250],
        )
        messages.success(request, "مرجوعی ثبت شد و موجودی افزایش یافت.")
        return redirect("returns")
    history = list(
        ReturnRecord.objects.select_related("variant__product", "variant__size", "variant__color")[:100]
    )
    return render(request, "dia_core/returns.html", {
        "variants": variants,
        "history": history,
        "today_j": format_jalali(date.today()),
    })


@login_required
@transaction.atomic
def purchase(request):
    selected_text = request.GET.get("date") or request.POST.get("date") or format_jalali(date.today())
    try:
        selected_date = parse_jalali_date(selected_text, date.today())
    except ValueError:
        selected_date = date.today()
        selected_text = format_jalali(selected_date)

    variants = list(
        ProductVariant.objects.filter(active=True, product__active=True)
        .select_related("product", "size", "color")
        .order_by("product__code", "size__sort_order", "color__name")
    )
    existing = {
        row.variant_id: row
        for row in PurchaseLine.objects.filter(date=selected_date).select_for_update()
    } if request.method == "POST" else {
        row.variant_id: row
        for row in PurchaseLine.objects.filter(date=selected_date)
    }

    if request.method == "POST":
        changed = 0
        for variant in variants:
            qty = max(0, _int(request.POST.get(f"qty_{variant.id}")))
            row = existing.get(variant.id)
            if row is None and qty <= 0:
                continue
            cost = max(0, _int(request.POST.get(f"cost_{variant.id}"), variant.unit_cost))
            if row is None:
                row = PurchaseLine.objects.create(
                    date=selected_date,
                    variant=variant,
                    quantity=0,
                    unit_cost=cost,
                )
            row.quantity = qty
            row.unit_cost = cost
            row.note = (request.POST.get("note") or "").strip()[:250]
            row.save(update_fields=["quantity", "unit_cost", "note", "updated_at"])
            sync_purchase_inventory(row)
            if qty > 0 and cost > 0 and int(variant.unit_cost or 0) != cost:
                variant.unit_cost = cost
                variant.save(update_fields=["unit_cost"])
            changed += 1
        messages.success(request, f"خرید روز ذخیره شد؛ {changed} ردیف همگام شد.")
        return redirect(f"/purchase/?date={format_jalali(selected_date)}")

    rows = []
    total_qty = 0
    total_cost = 0
    for variant in variants:
        row = existing.get(variant.id)
        qty = int(row.quantity or 0) if row else 0
        cost = int(row.unit_cost or 0) if row else int(variant.unit_cost or 0)
        rows.append({"variant": variant, "line": row, "quantity": qty, "cost": cost, "total": qty * cost})
        total_qty += qty
        total_cost += qty * cost
    return render(request, "dia_core/purchase.html", {
        "selected_date": format_jalali(selected_date),
        "rows": rows,
        "total_qty": total_qty,
        "total_cost": total_cost,
    })


@login_required
@transaction.atomic
def finance(request):
    accounts = list(Account.objects.filter(active=True).order_by("title"))
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_account":
            title = (request.POST.get("title") or "").strip()
            if not title:
                raise ValueError("نام حساب را وارد کن.")
            Account.objects.get_or_create(title=title, defaults={"opening_balance": _int(request.POST.get("opening_balance"))})
            messages.success(request, "حساب اضافه شد.")
        else:
            account = get_object_or_404(Account, id=request.POST.get("account"), active=True)
            amount = max(0, _int(request.POST.get("amount")))
            if amount <= 0:
                raise ValueError("مبلغ باید بیشتر از صفر باشد.")
            when = parse_jalali_date(request.POST.get("date"), date.today())
            title = (request.POST.get("title") or "").strip()[:160] or ("پرداخت" if action == "payment" else "دریافت")
            note = (request.POST.get("note") or "").strip()[:250]
            if action == "payment":
                row = Payment.objects.create(date=when, account=account, amount=amount, title=title, note=note)
                create_account_entry(account=account, date=when, delta=-amount, title=title, reference=f"payment:{row.id}", note=note)
                messages.success(request, "پرداخت ثبت شد.")
            elif action == "receipt":
                row = Receipt.objects.create(date=when, account=account, amount=amount, title=title, note=note)
                create_account_entry(account=account, date=when, delta=amount, title=title, reference=f"receipt:{row.id}", note=note)
                messages.success(request, "دریافت ثبت شد.")
            else:
                raise ValueError("عملیات مالی نامعتبر است.")
        return redirect("finance")

    account_rows = [{"account": account, "balance": account_balance(account)} for account in accounts]
    recent = list(AccountEntry.objects.select_related("account")[:100])
    return render(request, "dia_core/finance.html", {
        "accounts": accounts,
        "account_rows": account_rows,
        "recent": recent,
        "today_j": format_jalali(date.today()),
    })


@login_required
@transaction.atomic
def settings_home(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "size":
            name = (request.POST.get("name") or "").strip()
            if not name:
                raise ValueError("نام سایز را وارد کن.")
            Size.objects.get_or_create(name=name, defaults={"sort_order": _int(request.POST.get("sort_order"))})
            messages.success(request, "سایز اضافه شد.")
        elif action == "color":
            name = (request.POST.get("name") or "").strip()
            if not name:
                raise ValueError("نام رنگ را وارد کن.")
            Color.objects.get_or_create(name=name, defaults={"code": (request.POST.get("code") or "").strip()[:20]})
            messages.success(request, "رنگ اضافه شد.")
        elif action == "product":
            code = (request.POST.get("code") or "").strip()
            if not code:
                raise ValueError("کد محصول را وارد کن.")
            Product.objects.get_or_create(code=code, defaults={"title": (request.POST.get("title") or "").strip()[:140]})
            messages.success(request, "محصول اضافه شد.")
        elif action == "variant":
            product = get_object_or_404(Product, id=request.POST.get("product"))
            size = get_object_or_404(Size, id=request.POST.get("size"))
            color = get_object_or_404(Color, id=request.POST.get("color"))
            variant, _ = ProductVariant.objects.get_or_create(product=product, size=size, color=color)
            variant.default_sale_price = max(0, _int(request.POST.get("sale_price")))
            variant.unit_cost = max(0, _int(request.POST.get("unit_cost")))
            variant.active = True
            variant.save(update_fields=["default_sale_price", "unit_cost", "active"])
            stock_for(variant)
            messages.success(request, "مدل/واریانت محصول ذخیره شد.")
        elif action == "channel_price":
            variant = get_object_or_404(
                ProductVariant,
                id=request.POST.get("variant"),
            )
            channel = get_object_or_404(
                SalesChannel,
                id=request.POST.get("sales_channel"),
                active=True,
            )
            sale_price = max(
                0,
                _int(request.POST.get("sale_price")),
            )

            VariantChannelPrice.objects.update_or_create(
                variant=variant,
                sales_channel=channel,
                defaults={
                    "sale_price": sale_price,
                    "active": True,
                },
            )

            messages.success(
                request,
                "قیمت فروش این کانال ذخیره شد.",
            )

        elif action == "commission":
            fields = {
                "digikala_commission_percent": "کمیسیون دیجی‌کالا (%)",
                "digikala_processing_percent": "پردازش و ارسال (%)",
                "digikala_processing_floor": "حداقل پردازش و ارسال",
                "digikala_vat_percent": "مالیات ارزش افزوده (%)",
                "digikala_floor_taxable_part": "بخش مشمول مالیات در کف پردازش",
                "low_stock_threshold": "حد هشدار موجودی",
            }
            for key, label in fields.items():
                AppSetting.objects.update_or_create(
                    key=key,
                    defaults={"value": str(request.POST.get(key) or "0"), "label": label},
                )
            messages.success(request, "تنظیمات ذخیره شد.")
        else:
            raise ValueError("عملیات تنظیمات نامعتبر است.")
        return redirect("settings_home")

    settings = {row.key: row.value for row in AppSetting.objects.all()}
    return render(request, "dia_core/settings.html", {
        "sizes": Size.objects.all(),
        "colors": Color.objects.all(),
        "products": Product.objects.all(),
        "variants": ProductVariant.objects.select_related(
            "product",
            "size",
            "color",
        ).all(),
        "sales_channels": SalesChannel.objects.filter(
            active=True
        ).order_by("title"),
        "channel_prices": VariantChannelPrice.objects.filter(
            active=True
        ).select_related(
            "variant",
            "variant__product",
            "variant__size",
            "variant__color",
            "sales_channel",
        ).order_by(
            "variant__product__code",
            "sales_channel__title",
        ),
        "settings": settings,
    })

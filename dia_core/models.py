from django.core.validators import MinValueValidator
from django.db import models


class Size(models.Model):
    name = models.CharField(max_length=30, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Product(models.Model):
    code = models.CharField(max_length=60, unique=True)
    business = models.ForeignKey(
        "Business",
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=140, blank=True)
    active = models.BooleanField(default=True)
    note = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.title or self.code


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.ForeignKey(Size, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    default_sale_price = models.PositiveBigIntegerField(default=0)
    unit_cost = models.PositiveBigIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["product", "size", "color"], name="uniq_dia_product_variant")
        ]
        ordering = ["product__code", "size__sort_order", "color__name"]

    def __str__(self):
        return f"{self.product.code} / {self.size.name} / {self.color.name}"


class VariantChannelPrice(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="channel_prices",
    )
    sales_channel = models.ForeignKey(
        "SalesChannel",
        on_delete=models.CASCADE,
        related_name="variant_prices",
    )
    sale_price = models.PositiveBigIntegerField(default=0)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "sales_channel"],
                name="uniq_dia_variant_channel_price",
            )
        ]
        ordering = [
            "variant__product__code",
            "sales_channel__title",
        ]

    def __str__(self):
        return f"{self.variant} - {self.sales_channel}: {self.sale_price}"


class StockLocation(models.Model):
    key = models.SlugField(max_length=30, unique=True)
    title = models.CharField(max_length=80)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class StockBalance(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="stock_balances")
    location = models.ForeignKey(StockLocation, on_delete=models.PROTECT, related_name="stock_balances")
    qty = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["variant", "location"], name="uniq_dia_variant_location")
        ]


class InventoryMovement(models.Model):
    PURCHASE = "purchase"
    SALE = "sale"
    RETURN = "return"
    ADJUST = "adjust"
    MOVEMENT_CHOICES = [
        (PURCHASE, "خرید"),
        (SALE, "فروش"),
        (RETURN, "مرجوعی"),
        (ADJUST, "اصلاح"),
    ]

    date = models.DateField(db_index=True)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES, db_index=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    location = models.ForeignKey(StockLocation, on_delete=models.PROTECT)
    delta = models.IntegerField()
    reference = models.CharField(max_length=140, blank=True, db_index=True)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]


class Business(models.Model):
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class SalesChannel(models.Model):
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PaymentProvider(models.Model):
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class SaleDay(models.Model):
    date = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.date)


class SaleOrder(models.Model):
    class PaymentStatus(models.TextChoices):
        RECEIVED = "received", "واریز شده"
        PENDING = "pending", "در انتظار تسویه"
        SETTLED = "settled", "تسویه شده"
        CANCELLED = "cancelled", "لغو / مرجوع"

    day = models.ForeignKey(
        SaleDay,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="sale_orders",
        null=True,
        blank=True,
    )
    sales_channel = models.ForeignKey(
        SalesChannel,
        on_delete=models.PROTECT,
        related_name="sale_orders",
    )
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="sale_orders",
        null=True,
        blank=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.RECEIVED,
        db_index=True,
    )
    external_reference = models.CharField(
        max_length=140,
        blank=True,
        db_index=True,
    )
    shipping_collected = models.PositiveBigIntegerField(default=0)
    shipping_cost = models.PositiveBigIntegerField(default=0)
    provider_fee_collected = models.PositiveBigIntegerField(default=0)
    expected_settlement_date = models.DateField(null=True, blank=True)
    settled_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-day__date", "-id"]


class SaleLine(models.Model):
    day = models.ForeignKey(SaleDay, on_delete=models.CASCADE, related_name="lines")
    order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="sale_lines")
    quantity = models.PositiveIntegerField(default=0)
    inventory_applied_quantity = models.PositiveIntegerField(default=0)
    sale_price = models.PositiveBigIntegerField(default=0)
    unit_cost_snapshot = models.PositiveBigIntegerField(default=0)
    digikala_fee_unit = models.PositiveBigIntegerField(default=0)
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="sale_lines",
        null=True,
        blank=True,
    )
    sales_channel = models.ForeignKey(
        SalesChannel,
        on_delete=models.PROTECT,
        related_name="sale_lines",
        null=True,
        blank=True,
    )
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="sale_lines",
        null=True,
        blank=True,
    )
    channel_fee_unit_snapshot = models.PositiveBigIntegerField(default=0)
    channel_tax_unit_snapshot = models.PositiveBigIntegerField(default=0)
    provider_fee_unit_snapshot = models.PositiveBigIntegerField(default=0)
    provider_tax_unit_snapshot = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "variant"],
                name="uniq_dia_order_variant",
            )
        ]
        ordering = ["variant__product__code", "variant__size__sort_order", "variant__color__name"]

    @property
    def gross_sales(self):
        return int(self.quantity or 0) * int(self.sale_price or 0)


class PurchaseLine(models.Model):
    date = models.DateField(db_index=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="purchase_lines")
    quantity = models.PositiveIntegerField(default=0)
    inventory_applied_quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.PositiveBigIntegerField(default=0)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "variant"], name="uniq_dia_purchase_date_variant")
        ]
        ordering = ["-date", "variant__product__code"]


class ReturnRecord(models.Model):
    date = models.DateField(db_index=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="returns")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class InventoryAdjustment(models.Model):
    date = models.DateField(db_index=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="adjustments")
    location = models.ForeignKey(StockLocation, on_delete=models.PROTECT)
    delta = models.IntegerField()
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class BusinessExpense(models.Model):
    class ExpenseType(models.TextChoices):
        POST = "post", "پست"
        PACKAGING = "packaging", "بسته‌بندی"
        ADVERTISING = "advertising", "تبلیغات"
        OTHER = "other", "سایر"

    date = models.DateField(db_index=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    sales_channel = models.ForeignKey(
        SalesChannel,
        on_delete=models.PROTECT,
        related_name="expenses",
        null=True,
        blank=True,
    )
    expense_type = models.CharField(
        max_length=20,
        choices=ExpenseType.choices,
        default=ExpenseType.OTHER,
    )
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    paid_from = models.ForeignKey(
        "Account",
        on_delete=models.PROTECT,
        related_name="business_expenses",
        null=True,
        blank=True,
    )
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class PlatformSettlement(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار تسویه"
        SETTLED = "settled", "تسویه شده"
        CANCELLED = "cancelled", "لغو شده"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="settlements",
    )
    sales_channel = models.ForeignKey(
        SalesChannel,
        on_delete=models.PROTECT,
        related_name="settlements",
    )
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="settlements",
        null=True,
        blank=True,
    )
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    gross_amount = models.PositiveBigIntegerField(default=0)
    fee_amount = models.PositiveBigIntegerField(default=0)
    tax_amount = models.PositiveBigIntegerField(default=0)
    shipping_amount = models.PositiveBigIntegerField(default=0)
    other_deductions = models.PositiveBigIntegerField(default=0)
    net_amount = models.PositiveBigIntegerField(default=0)
    expected_settlement_date = models.DateField(null=True, blank=True)
    settled_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-expected_settlement_date", "-id"]




class HolderDirectOrder(models.Model):
    date = models.DateField(db_index=True)
    customer_name = models.CharField(max_length=160)
    quantity_small = models.PositiveIntegerField(default=0)
    quantity_medium = models.PositiveIntegerField(default=0)
    quantity_large = models.PositiveIntegerField(default=0)
    unit_price_small = models.PositiveBigIntegerField(default=0)
    unit_price_medium = models.PositiveBigIntegerField(default=0)
    unit_price_large = models.PositiveBigIntegerField(default=0)
    order_total = models.PositiveBigIntegerField(default=0)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    @property
    def remaining_balance(self):
        received = self.receipts.aggregate(
            total=models.Sum("amount")
        )["total"] or 0
        return max(int(self.order_total or 0) - int(received), 0)


class HolderDirectReceipt(models.Model):
    class ReceiptType(models.TextChoices):
        DEPOSIT = "deposit", "بیعانه"
        FULL = "full", "تسویه کامل"
        BALANCE = "balance", "پرداخت مانده"

    class Recipient(models.TextChoices):
        SAMANEH = "samaneh", "سمانه"
        MEHR = "mehr", "مهر"

    order = models.ForeignKey(
        HolderDirectOrder,
        on_delete=models.CASCADE,
        related_name="receipts",
    )
    date = models.DateField(db_index=True)
    amount = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    )
    receipt_type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
    )
    recipient = models.CharField(
        max_length=20,
        choices=Recipient.choices,
    )
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]



class Counterparty(models.Model):
    title = models.CharField(max_length=120)
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="counterparties",
    )
    active = models.BooleanField(default=True)
    receivable_enabled = models.BooleanField(default=False)
    note = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["business__title", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "title"],
                name="uniq_dia_counterparty_business_title",
            )
        ]

    def __str__(self):
        return f"{self.title} / {self.business}"


class Account(models.Model):
    class Kind(models.TextChoices):
        GENERIC = "generic", "عمومی"
        CASH = "cash", "بانک / نقد"
        PAYABLE = "payable", "بدهی"
        RECEIVABLE = "receivable", "طلب"
        CUSTOMER_DEPOSIT = "customer_deposit", "بیعانه مشتری"

    title = models.CharField(max_length=100, unique=True)
    kind = models.CharField(
        max_length=30,
        choices=Kind.choices,
        default=Kind.GENERIC,
        db_index=True,
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="accounts",
        null=True,
        blank=True,
    )
    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.PROTECT,
        related_name="accounts",
        null=True,
        blank=True,
    )
    opening_balance = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class AccountEntry(models.Model):
    date = models.DateField(db_index=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="entries")
    delta = models.BigIntegerField()
    title = models.CharField(max_length=180)
    reference = models.CharField(max_length=140, blank=True, db_index=True)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class Payment(models.Model):
    date = models.DateField(db_index=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="payments")
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=160)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class Receipt(models.Model):
    date = models.DateField(db_index=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="receipts")
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=160)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=200)
    label = models.CharField(max_length=160)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.label


class BusinessTransfer(models.Model):
    date = models.DateField(db_index=True)
    from_business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="outgoing_business_transfers",
    )
    to_business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="incoming_business_transfers",
    )
    amount = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    )
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    from_business=models.F("to_business")
                ),
                name="dia_transfer_different_businesses",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="dia_transfer_positive_amount",
            ),
        ]

    def __str__(self):
        return (
            f"{self.from_business} -> "
            f"{self.to_business}: {self.amount}"
        )

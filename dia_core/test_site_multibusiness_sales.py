from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Business,
    Color,
    Product,
    ProductVariant,
    SaleDay,
    SalesChannel,
    Size,
)


class SiteMultibusinessSalesTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="site-multi-test",
            password="test-pass-123",
        )
        self.client.force_login(user)

        self.day = SaleDay.objects.create(date=timezone.localdate())
        SalesChannel.objects.create(
            code="site",
            title="سایت",
            active=True,
        )

        size = Size.objects.create(name="M")
        color = Color.objects.create(name="مشکی")

        for code, title in (
            ("DIA-1", "محصول دیا"),
            ("BODY-1", "محصول بادیگارد"),
            ("HOLDER-1", "قالب نوبنیان"),
        ):
            business = Business.objects.create(
                code=code.lower(),
                title=title,
                active=True,
            )
            product = Product.objects.create(
                code=code,
                title=title,
                business=business,
                active=True,
            )
            ProductVariant.objects.create(
                product=product,
                size=size,
                color=color,
                default_sale_price=100000,
                unit_cost=50000,
                active=True,
            )

    def test_site_mode_shows_products_from_all_businesses(self):
        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "site"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DIA-1")
        self.assertContains(response, "BODY-1")
        self.assertContains(response, "HOLDER-1")

    def test_site_invoice_can_be_business_neutral(self):
        from .models import SaleOrder

        self.assertTrue(
            SaleOrder._meta.get_field("business").null
        )

    def test_site_invoice_can_save_lines_from_multiple_businesses(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        body_variant = ProductVariant.objects.get(product__code="BODY-1")

        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=100,
        )
        StockBalance.objects.create(
            variant=body_variant,
            location=location,
            qty=100,
        )

        self.client.raise_request_exception = False

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": "",
                "shipping_collected": "0",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "2",
                f"price_{dia_variant.id}": "120000",
                f"qty_{body_variant.id}": "3",
                f"price_{body_variant.id}": "150000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        self.assertIsNone(order.business)

        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related(
                "variant__product",
                "business",
            )
        }

        self.assertEqual(set(lines), {"DIA-1", "BODY-1"})
        self.assertEqual(lines["DIA-1"].business, dia_variant.product.business)
        self.assertEqual(lines["BODY-1"].business, body_variant.product.business)

        self.assertEqual(
            StockBalance.objects.get(
                variant=dia_variant,
                location=location,
            ).qty,
            98,
        )
        self.assertEqual(
            StockBalance.objects.get(
                variant=body_variant,
                location=location,
            ).qty,
            97,
        )

    def test_site_mode_renders_simplified_sales_form(self):
        business = Business.objects.get(code="dia-1")
        business.title = "برند DIA"
        business.save(update_fields=["title"])

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "site"},
        )

        self.assertEqual(response.status_code, 200)

        # چیزهایی که باید باشند
        self.assertContains(response, 'name="payment_provider"')
        self.assertContains(response, 'name="shipping_cost"')
        self.assertContains(response, "برند DIA")
        self.assertContains(response, 'name="qty_')
        self.assertContains(response, 'name="price_')

        # چیزهای اضافی که در فروش سایت نباید دیده شوند
        self.assertNotContains(response, 'name="business"')
        self.assertNotContains(response, 'name="sales_channel"')
        self.assertNotContains(response, 'name="payment_status"')
        self.assertNotContains(response, 'name="external_reference"')
        self.assertNotContains(response, 'name="expected_settlement_date"')
        self.assertNotContains(response, 'name="settled_date"')
        self.assertNotContains(response, 'name="shipping_collected"')
        self.assertNotContains(response, 'name="provider_fee_collected"')

    def test_editing_site_invoice_preserves_line_businesses_and_adjusts_stock(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        body_variant = ProductVariant.objects.get(product__code="BODY-1")

        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=100,
        )
        StockBalance.objects.create(
            variant=body_variant,
            location=location,
            qty=100,
        )

        create_response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": "",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "2",
                f"price_{dia_variant.id}": "120000",
                f"qty_{body_variant.id}": "3",
                f"price_{body_variant.id}": "150000",
            },
        )
        self.assertEqual(create_response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)

        self.client.raise_request_exception = False

        edit_response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "order_id": str(order.id),
                "payment_provider": "",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "5",
                f"price_{dia_variant.id}": "125000",
                f"qty_{body_variant.id}": "1",
                f"price_{body_variant.id}": "155000",
            },
        )

        self.assertEqual(edit_response.status_code, 302)

        order.refresh_from_db()
        self.assertIsNone(order.business)

        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related(
                "variant__product__business",
                "business",
            )
        }

        self.assertEqual(lines["DIA-1"].business, dia_variant.product.business)
        self.assertEqual(lines["BODY-1"].business, body_variant.product.business)
        self.assertEqual(lines["DIA-1"].quantity, 5)
        self.assertEqual(lines["BODY-1"].quantity, 1)

        self.assertEqual(
            StockBalance.objects.get(
                variant=dia_variant,
                location=location,
            ).qty,
            95,
        )
        self.assertEqual(
            StockBalance.objects.get(
                variant=body_variant,
                location=location,
            ).qty,
            99,
        )

    def test_site_sale_rejects_quantity_above_available_stock(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        balance = StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=2,
        )

        with self.assertRaises(ValueError):
            self.client.post(
                reverse("sale_day", args=[self.day.id]),
                {
                    "mode": "site",
                    "payment_provider": "",
                    "shipping_cost": "0",
                    f"qty_{variant.id}": "5",
                    f"price_{variant.id}": "120000",
                },
            )

        balance.refresh_from_db()
        self.assertEqual(balance.qty, 2)

        self.assertFalse(
            SaleOrder.objects.filter(day=self.day).exists()
        )

    def test_site_digipay_fee_and_payment_status_are_automatic(self):
        from .models import (
            AppSetting,
            PaymentProvider,
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        digipay = PaymentProvider.objects.create(
            code="digipay",
            title="DigiPay",
            active=True,
        )

        AppSetting.objects.create(
            key="digipay_commission_percent",
            value="10",
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": str(digipay.id),
                "shipping_cost": "0",
                f"qty_{variant.id}": "2",
                f"price_{variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        line = order.lines.get(variant=variant)

        self.assertEqual(order.payment_provider, digipay)
        self.assertEqual(
            order.payment_status,
            SaleOrder.PaymentStatus.PENDING,
        )

        # 10% of 100,000
        self.assertEqual(
            line.provider_fee_unit_snapshot,
            10000,
        )

        # 2 items × 10,000 fee
        self.assertEqual(
            order.provider_fee_collected,
            20000,
        )

    def test_site_summary_shows_financial_breakdown_and_net_receivable(self):
        from .models import (
            AppSetting,
            PaymentProvider,
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        digipay = PaymentProvider.objects.create(
            code="digipay",
            title="DigiPay",
            active=True,
        )

        AppSetting.objects.create(
            key="digipay_commission_percent",
            value="10",
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": str(digipay.id),
                "shipping_cost": "15000",
                f"qty_{variant.id}": "2",
                f"price_{variant.id}": "100000",
            },
        )

        order = SaleOrder.objects.get(day=self.day)

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "order": order.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "فروش ناخالص")
        self.assertContains(response, "کل کارمزدها")
        self.assertContains(response, "خالص دریافتی / طلب درگاه")
        self.assertContains(response, "هزینه پست")
        self.assertContains(response, "بهای کالا")
        self.assertContains(response, "سود فاکتور")

        self.assertIn("net_receivable", response.context["total"])

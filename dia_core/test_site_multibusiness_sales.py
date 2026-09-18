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

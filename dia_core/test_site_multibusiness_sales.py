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

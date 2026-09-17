from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import services
from .models import (
    Business,
    Color,
    PaymentProvider,
    Product,
    ProductVariant,
    SaleDay,
    SaleLine,
    SaleOrder,
    SalesChannel,
    Size,
)


class PlatformReceivableTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="platform-receivable-test",
            password="test-pass-123",
        )
        self.client.force_login(user)
        self.business = Business.objects.create(
            code="receivable-business",
            title="Receivable Business",
            active=True,
        )
        self.day = SaleDay.objects.create(date=timezone.localdate())
        self.channels = {
            code: SalesChannel.objects.create(code=code, title=code, active=True)
            for code in ("digikala", "basalam", "site")
        }
        self.providers = {
            code: PaymentProvider.objects.create(code=code, title=code, active=True)
            for code in ("snapp", "digipay", "torobpay")
        }
        product = Product.objects.create(
            code="receivable-product",
            business=self.business,
            title="Receivable Product",
            active=True,
        )
        size = Size.objects.create(name="R", sort_order=1, active=True)
        color = Color.objects.create(name="R", active=True)
        self.variant = ProductVariant.objects.create(
            product=product,
            size=size,
            color=color,
            default_sale_price=1000,
            unit_cost=400,
            active=True,
        )

    def _order(
        self,
        *,
        channel,
        provider=None,
        status=SaleOrder.PaymentStatus.PENDING,
        sale_price=1000,
        digikala_fee=0,
        channel_fee=0,
        channel_tax=0,
        provider_fee=0,
        provider_tax=0,
        shipping_collected=0,
        shipping_cost=0,
        provider_fee_collected=0,
    ):
        order = SaleOrder.objects.create(
            day=self.day,
            business=self.business,
            sales_channel=self.channels[channel],
            payment_provider=self.providers.get(provider),
            payment_status=status,
            shipping_collected=shipping_collected,
            shipping_cost=shipping_cost,
            provider_fee_collected=provider_fee_collected,
        )
        SaleLine.objects.create(
            day=self.day,
            order=order,
            variant=self.variant,
            quantity=1,
            sale_price=sale_price,
            unit_cost_snapshot=400,
            business=self.business,
            sales_channel=self.channels[channel],
            payment_provider=self.providers.get(provider),
            digikala_fee_unit=digikala_fee,
            channel_fee_unit_snapshot=channel_fee,
            channel_tax_unit_snapshot=channel_tax,
            provider_fee_unit_snapshot=provider_fee,
            provider_tax_unit_snapshot=provider_tax,
        )
        return order

    def test_pending_platform_sales_are_grouped_by_platform(self):
        self._order(
            channel="digikala",
            digikala_fee=100,
            shipping_collected=50,
            shipping_cost=40,
        )
        self._order(channel="basalam", channel_fee=140)
        self._order(
            channel="site",
            provider="snapp",
            provider_fee=130,
            provider_tax=13,
            provider_fee_collected=143,
        )
        self._order(
            channel="site",
            provider="digipay",
            provider_fee=120,
            provider_fee_collected=120,
        )
        self._order(
            channel="site",
            provider="torobpay",
            provider_fee=60,
            provider_fee_collected=60,
        )

        self.assertTrue(
            hasattr(services, "platform_receivable_totals"),
            "platform_receivable_totals must exist",
        )
        totals = services.platform_receivable_totals()

        self.assertEqual(totals["digikala"], 950)
        self.assertEqual(totals["basalam"], 860)
        self.assertEqual(totals["snapp"], 1000)
        self.assertEqual(totals["digipay"], 1000)
        self.assertEqual(totals["torobpay"], 1000)

    def test_non_pending_orders_do_not_count_as_receivables(self):
        for status in (
            SaleOrder.PaymentStatus.RECEIVED,
            SaleOrder.PaymentStatus.SETTLED,
            SaleOrder.PaymentStatus.CANCELLED,
        ):
            self._order(
                channel="digikala",
                status=status,
                digikala_fee=100,
            )

        self.assertTrue(
            hasattr(services, "platform_receivable_totals"),
            "platform_receivable_totals must exist",
        )
        totals = services.platform_receivable_totals()

        self.assertEqual(totals["digikala"], 0)

    def test_finance_page_shows_platform_receivable_summary(self):
        self._order(channel="digikala", digikala_fee=100)

        response = self.client.get(reverse("finance"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("platform_receivables", response.context)
        self.assertEqual(response.context["platform_receivables"]["digikala"], 900)
        self.assertContains(response, "طلب از پلتفرم‌ها")

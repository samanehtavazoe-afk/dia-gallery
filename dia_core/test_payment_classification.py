from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from . import services
from .models import Business, SaleDay, SaleOrder, SalesChannel


class SalePaymentClassificationTests(SimpleTestCase):
    def _helper(self):
        self.assertTrue(
            hasattr(services, "default_sale_payment_status"),
            "default_sale_payment_status must exist",
        )
        return services.default_sale_payment_status

    def test_platform_channels_default_to_pending(self):
        helper = self._helper()
        for code in ("digikala", "basalam"):
            status = helper(
                sales_channel=SimpleNamespace(code=code),
                payment_provider=None,
            )
            self.assertEqual(status, SaleOrder.PaymentStatus.PENDING)

    def test_site_cash_is_received(self):
        helper = self._helper()
        status = helper(
            sales_channel=SimpleNamespace(code="site"),
            payment_provider=None,
        )
        self.assertEqual(status, SaleOrder.PaymentStatus.RECEIVED)

    def test_site_credit_providers_default_to_pending(self):
        helper = self._helper()
        for code in ("snapp", "digipay", "torobpay"):
            status = helper(
                sales_channel=SimpleNamespace(code="site"),
                payment_provider=SimpleNamespace(code=code),
            )
            self.assertEqual(status, SaleOrder.PaymentStatus.PENDING)


class SalePaymentViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="payment-view-test",
            password="test-pass-123",
        )
        self.client.force_login(user)
        self.business = Business.objects.create(
            code="payment-view-business",
            title="Payment View Business",
            active=True,
        )
        self.digikala = SalesChannel.objects.create(
            code="digikala",
            title="دیجی‌کالا",
            active=True,
        )
        self.day = SaleDay.objects.create(date=timezone.localdate())

    def test_new_digikala_order_defaults_to_pending(self):
        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "business": self.business.id,
                "sales_channel": self.digikala.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        order = SaleOrder.objects.get()
        self.assertEqual(order.payment_status, SaleOrder.PaymentStatus.PENDING)

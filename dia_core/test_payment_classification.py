from types import SimpleNamespace

from django.test import SimpleTestCase

from . import services
from .models import SaleOrder


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

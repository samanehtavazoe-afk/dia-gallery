from types import SimpleNamespace

from django.test import SimpleTestCase

from .models import SaleOrder


class SalePaymentClassificationTests(SimpleTestCase):
    def test_platform_channels_default_to_pending(self):
        from .services import default_sale_payment_status

        for code in ("digikala", "basalam"):
            status = default_sale_payment_status(
                sales_channel=SimpleNamespace(code=code),
                payment_provider=None,
            )
            self.assertEqual(status, SaleOrder.PaymentStatus.PENDING)

    def test_site_cash_is_received(self):
        from .services import default_sale_payment_status

        status = default_sale_payment_status(
            sales_channel=SimpleNamespace(code="site"),
            payment_provider=None,
        )
        self.assertEqual(status, SaleOrder.PaymentStatus.RECEIVED)

    def test_site_credit_providers_default_to_pending(self):
        from .services import default_sale_payment_status

        for code in ("snapp", "digipay", "torobpay"):
            status = default_sale_payment_status(
                sales_channel=SimpleNamespace(code="site"),
                payment_provider=SimpleNamespace(code=code),
            )
            self.assertEqual(status, SaleOrder.PaymentStatus.PENDING)

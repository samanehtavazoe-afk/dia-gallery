from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Business, PaymentProvider, SaleDay, SalesChannel


class DailySalesModeConstraintTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="daily-sales-mode-test",
            password="test-pass-123",
        )
        self.client.force_login(user)
        self.day = SaleDay.objects.create(date=timezone.localdate())
        Business.objects.create(
            code="mode-business",
            title="Mode Business",
            active=True,
        )
        self.site = SalesChannel.objects.create(
            code="site",
            title="A Site",
            active=True,
        )
        self.basalam = SalesChannel.objects.create(
            code="basalam",
            title="B Basalam",
            active=True,
        )
        self.digikala = SalesChannel.objects.create(
            code="digikala",
            title="C Digikala",
            active=True,
        )
        for code, title in (
            ("snapp", "SnappPay"),
            ("digipay", "DigiPay"),
            ("torobpay", "TorobPay"),
            ("other", "Other Provider"),
        ):
            PaymentProvider.objects.create(
                code=code,
                title=title,
                active=True,
            )

    def _get(self, mode):
        return self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": mode},
        )

    def test_digikala_mode_forces_channel_and_hides_provider_choice(self):
        response = self._get("digikala")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_channel"].code, "digikala")
        self.assertContains(response, "کالاهای فاکتور")
        self.assertNotContains(response, 'name="payment_provider"')

    def test_basalam_mode_forces_channel_and_hides_provider_choice(self):
        response = self._get("basalam")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_channel"].code, "basalam")
        self.assertContains(response, "کالاهای فاکتور")
        self.assertNotContains(response, 'name="payment_provider"')

    def test_site_mode_forces_site_and_limits_payment_providers(self):
        response = self._get("site")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_channel"].code, "site")
        self.assertEqual(
            {provider.code for provider in response.context["providers"]},
            {"snapp", "digipay", "torobpay"},
        )
        self.assertContains(response, 'name="payment_provider"')
        self.assertNotContains(response, "Other Provider")

    def test_holder_mode_does_not_render_generic_invoice_editor(self):
        response = self._get("holder")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "کالاهای فاکتور")

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import SaleDay


class DailySalesHubTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="daily-sales-hub-test",
            password="test-pass-123",
        )
        self.client.force_login(user)
        self.day = SaleDay.objects.create(date=timezone.localdate())

    def test_day_without_mode_shows_four_cards_and_hides_invoice_editor(self):
        response = self.client.get(reverse("sale_day", args=[self.day.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "دیجی‌کالا")
        self.assertContains(response, "سایت")
        self.assertContains(response, "باسلام")
        self.assertContains(response, "فروش قالب")
        self.assertNotContains(response, "کالاهای فاکتور")

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .dateutils import month_calendar


class SalesCalendarHolidayTests(SimpleTestCase):
    def test_shahrivar_1405_marks_friday_and_official_holiday(self):
        cal = month_calendar(1405, 6)
        day_meta = cal["day_meta"]

        self.assertTrue(day_meta[6]["is_friday"])
        self.assertFalse(day_meta[6]["is_holiday"])

        self.assertFalse(day_meta[8]["is_friday"])
        self.assertTrue(day_meta[8]["is_holiday"])
        self.assertIn("ولادت حضرت رسول اکرم", day_meta[8]["holiday_title"])

    def test_normal_day_has_empty_holiday_title(self):
        cal = month_calendar(1405, 6)
        day_meta = cal["day_meta"]

        self.assertFalse(day_meta[7]["is_friday"])
        self.assertFalse(day_meta[7]["is_holiday"])
        self.assertEqual(day_meta[7]["holiday_title"], "")


class SalesCalendarHolidayViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="sales-calendar-holiday-test",
            password="test-pass-123",
        )
        self.client.force_login(user)

    def test_calendar_view_preserves_friday_and_holiday_metadata(self):
        response = self.client.get(
            reverse("sale_start"),
            {"jy": 1405, "jm": 6},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["day_meta"][6]["is_friday"])
        self.assertTrue(response.context["day_meta"][8]["is_holiday"])
        self.assertIn(
            "ولادت حضرت رسول اکرم",
            response.context["day_meta"][8]["holiday_title"],
        )

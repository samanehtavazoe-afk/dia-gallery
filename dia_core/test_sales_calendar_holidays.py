from django.test import SimpleTestCase

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

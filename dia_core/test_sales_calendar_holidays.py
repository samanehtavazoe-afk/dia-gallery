import jdatetime
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .dateutils import month_calendar
from .models import SaleDay


class SalesCalendarHolidayTests(SimpleTestCase):
    def test_shahrivar_1405_marks_friday_and_official_holiday(self):
        cal = month_calendar(1405, 6)
        day_meta = cal["day_meta"]

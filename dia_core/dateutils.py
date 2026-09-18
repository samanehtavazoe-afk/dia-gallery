from datetime import date

import jdatetime


PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

OFFICIAL_HOLIDAYS_1405 = {
    (1, 1): "عید سعید فطر - آغاز نوروز",
    (1, 2): "تعطیل به مناسبت عید سعید فطر - عید نوروز",
    (1, 3): "عید نوروز",
    (1, 4): "عید نوروز",
    (1, 12): "روز جمهوری اسلامی ایران",
    (1, 13): "روز طبیعت",
    (1, 25): "شهادت امام جعفر صادق (ع)",
    (3, 6): "عید سعید قربان",
    (3, 14): "عید سعید غدیر خم - رحلت امام خمینی",
    (3, 15): "قیام خونین ۱۵ خرداد",
    (4, 3): "تاسوعای حسینی",
    (4, 4): "عاشورای حسینی",
    (5, 13): "اربعین حسینی",
    (5, 21): "رحلت حضرت رسول اکرم (ص) - شهادت امام حسن مجتبی (ع)",
    (5, 22): "شهادت امام رضا (ع)",
    (5, 30): "شهادت امام حسن عسکری (ع) - آغاز امامت حضرت ولیعصر (عج)",
    (6, 8): "ولادت حضرت رسول اکرم (ص) - ولادت امام جعفر صادق (ع)",
    (8, 22): "شهادت حضرت فاطمه زهرا (س)",
    (10, 2): "ولادت امام علی (ع) - روز پدر",
    (10, 16): "مبعث حضرت رسول اکرم (ص)",
    (11, 4): "ولادت حضرت قائم (عج)",
    (11, 22): "پیروزی انقلاب اسلامی ایران",
    (12, 9): "شهادت حضرت علی (ع)",
    (12, 19): "عید سعید فطر",
    (12, 20): "تعطیل به مناسبت عید سعید فطر",
    (12, 29): "روز ملی شدن صنعت نفت ایران",
}


def format_jalali(value):
    if not value:
        return ""
    j = jdatetime.date.fromgregorian(date=value)
    return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"


def parse_jalali_date(text, default=None):
    raw = str(text or "").strip().replace("-", "/")
    if not raw:
        return default or date.today()
    try:
        y, m, d = [int(x) for x in raw.split("/")]
        return jdatetime.date(y, m, d).togregorian()
    except Exception as exc:
        raise ValueError("تاریخ شمسی معتبر نیست. نمونه: 1405/06/23") from exc


def jalali_month_bounds(value=None):
    value = value or date.today()
    j = jdatetime.date.fromgregorian(date=value)
    start = jdatetime.date(j.year, j.month, 1).togregorian()
    if j.month == 12:
        next_start = jdatetime.date(j.year + 1, 1, 1).togregorian()
    else:
        next_start = jdatetime.date(j.year, j.month + 1, 1).togregorian()
    return start, next_start, f"{PERSIAN_MONTHS[j.month - 1]} {j.year}"


def _jalali_month_days(jy, jm):
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    try:
        jdatetime.date(jy, 12, 30)
        return 30
    except ValueError:
        return 29


def month_calendar(jy=None, jm=None):
    today_j = jdatetime.date.fromgregorian(date=date.today())
    jy = int(jy or today_j.year)
    jm = int(jm or today_j.month)
    if jm < 1 or jm > 12:
        raise ValueError("ماه نامعتبر است.")
    days_count = _jalali_month_days(jy, jm)
    first = jdatetime.date(jy, jm, 1)
    # Python weekday: Mon=0. Persian week starts Saturday.
    offset = (first.togregorian().weekday() + 2) % 7
    cells = [None] * offset + list(range(1, days_count + 1))
    while len(cells) % 7:
        cells.append(None)
    weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]
    if jm == 1:
        py, pm = jy - 1, 12
    else:
        py, pm = jy, jm - 1
    if jm == 12:
        ny, nm = jy + 1, 1
    else:
        ny, nm = jy, jm + 1
    day_meta = {}
    for day_num in range(1, days_count + 1):
        gregorian = jdatetime.date(jy, jm, day_num).togregorian()
        holiday_title = (
            OFFICIAL_HOLIDAYS_1405.get((jm, day_num), "")
            if jy == 1405
            else ""
        )
        day_meta[day_num] = {
            "is_friday": gregorian.weekday() == 4,
            "is_holiday": bool(holiday_title),
            "holiday_title": holiday_title,
        }

    return {
        "jy": jy,
        "jm": jm,
        "month_name": PERSIAN_MONTHS[jm - 1],
        "weeks": weeks,
        "weekdays": ["ش", "ی", "د", "س", "چ", "پ", "ج"],
        "prev_y": py,
        "prev_m": pm,
        "next_y": ny,
        "next_m": nm,
        "day_meta": day_meta,
    }

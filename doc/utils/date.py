import datetime

from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now


def calculate_delta_time(set_time: str, time_str: str = ""):
    """
    :param set_time: The delta to be applied. One of 1d, 1w, 1m, nw, nm, null.
    :param time_str: The timestring to take as the base. If empty now() is taken as the base.
    :return datetime: The resulting datetime value.
    """

    base_time = parse_datetime(time_str) if time_str else datetime.datetime.now()
    if timezone.is_naive(base_time):
        base_time = make_aware(base_time)

    if set_time == "1d":
        return base_time + datetime.timedelta(days=1)
    elif set_time == "2d":
        return base_time + datetime.timedelta(days=2)
    elif set_time == "3d":
        return base_time + datetime.timedelta(days=3)
    elif set_time == "1w":
        return base_time + datetime.timedelta(weeks=1)
    elif set_time == "1m":
        try:
            next_month = base_time.replace(day=28) + datetime.timedelta(days=4)
            last_day_next_month = (next_month.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            naive_time = base_time.replace(
                month=next_month.month,
                year=next_month.year,
                day=min(base_time.day, last_day_next_month.day)
            )
            return make_aware(naive_time) if timezone.is_naive(naive_time) else naive_time
        except ValueError:
            return None
    elif set_time == "nw":
        weekday = base_time.weekday()
        days_until_monday = (7 - weekday) % 7 or 7
        naive = (base_time + datetime.timedelta(days=days_until_monday)).replace(
            hour=12, minute=0, second=0, microsecond=0
        )
        return make_aware(naive) if timezone.is_naive(naive) else naive
    elif set_time == "nm":
        next_month = (base_time.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        naive = next_month.replace(hour=12, minute=0, second=0, microsecond=0)
        return make_aware(naive) if timezone.is_naive(naive) else naive
    elif set_time == "null":
        return None
    else:
        return parse_datetime(time_str) if time_str else None


def parse_valid_date(value, fallback):
    try:
        parsed = parse_date(value)
        return parsed or fallback
    except Exception:
        return fallback

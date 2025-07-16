from django.utils.dateparse import parse_date


def parse_valid_date(value, fallback):
    try:
        parsed = parse_date(value)
        return parsed or fallback
    except Exception:
        return fallback

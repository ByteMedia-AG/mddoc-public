from django import template

register = template.Library()


@register.filter
def filesize_mb(value):
    try:
        mb = float(value) / (1024 * 1024)
        return f"{mb:.1f} MB"
    except (ValueError, TypeError):
        return ""

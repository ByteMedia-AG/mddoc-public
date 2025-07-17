from django import template

register = template.Library()

MIME_TYPE_MAP = {
    "application/pdf": "PDF",
    "image/jpeg": "JPEG Image",
    "image/png": "PNG Image",
    "text/plain": "Text File",
    "application/zip": "ZIP",
    "application/msword": "Word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
    "application/vnd.ms-excel": "Excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/vnd.ms-powerpoint": "PowerPoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
    "application/xml": "XML",
}


@register.filter
def filesize_mb(value):
    try:
        mb = float(value) / (1024 * 1024)
        return f"{mb:.1f} MB"
    except (ValueError, TypeError):
        return ""


@register.filter
def filetype(mime):
    if not mime:
        return '--'
    return MIME_TYPE_MAP.get(mime, f"{mime}")


@register.filter
def filesize(value):
    try:
        size = float(value)
        if size >= 1024 * 1024:
            mb = size / (1024 * 1024)
            return f"{mb:.1f} MB"
        else:
            kb = round(size / 1024)
            return f"{kb} kB"
    except (ValueError, TypeError):
        return ""

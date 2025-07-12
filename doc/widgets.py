from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe


class EasyMdeTextarea(Textarea):
    """Widget for EasyMDE."""

    template_name = "widgets/easymde_textarea.html"

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit, HTML
from django import forms
from django.forms import modelformset_factory

from .models import Doc, TimeRecord, ChecklistItem
from .widgets import EasyMdeTextarea


# Custom widget to allow multiple file selection
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class DocForm(forms.ModelForm):
    """"""

    class Meta:
        model = Doc
        fields = ["title", "time", "is_archived", "uri", "description", "is_markdown", "text", "tags", "last_settlement", ]
        widgets = {
            "text": EasyMdeTextarea(attrs={"class": "textarea form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["time"].widget = forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M"
        )
        self.fields["time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["last_settlement"].widget = forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d"
        )
        self.fields["last_settlement"].input_formats = ["%Y-%m-%d"]
        self.fields["description"].widget.attrs.update({"rows": 3})

        self.fields["is_markdown"].help_text = None
        self.fields["uri"].help_text = None
        self.fields["time"].help_text = None
        self.fields["title"].help_text = None
        self.fields["description"].help_text = None
        self.fields["text"].label = ""

        if self.instance.pk and self.instance.files.exists():
            self.fields["delete_files"] = forms.MultipleChoiceField(
                label="Remove selected files",
                required=False,
                widget=forms.CheckboxSelectMultiple,
                choices=[(str(f.id), f"{f.name} ({f.id})") for f in self.instance.files.all()],
            )
            show_delete_files = True
        else:
            show_delete_files = False

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save', css_class="btn btn-secondary"))
        self.helper.layout = Layout(
            "title",
            "description",
            Row(
                Column("tags", css_class="form-group col-md-9 mb-0"),
                Column("time", css_class="form-group col-md-3 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("uri", css_class="form-group col-md-6 mb-0"),
                Column(
                    HTML("""
                        <div class="form-group">
                            <label for="id_upload" class="form-label">Select files</label>
                            <input type="file" name="upload" id="id_upload" class="form-control" multiple>
                        </div>
                    """),
                    css_class="form-group col-md-6 mb-0"
                ),
                css_class="form-row",
            ),
            *([Div("delete_files", css_class="border rounded p-3")] if show_delete_files else []),
            Div(
                "is_markdown",
                css_class="mt-3"
            ),
            "text",
        )

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", [])
        return [tag.lower() for tag in tags]


class TimeRecordForm(forms.ModelForm):
    """"""

    class Meta:
        model = TimeRecord
        fields = ["date", "time", "description", ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["date"].widget = forms.DateInput(
            attrs={"type": "date", "required": "required"},
            format="%Y-%m-%d"
        )
        self.fields["date"].input_formats = ["%Y-%m-%d"]
        self.fields["date"].initial = datetime.date.today
        self.fields["time"].widget = forms.NumberInput(
            attrs={
                "type": "number",
                "min": "0",
                "max": "24",
                "step": "0.01",
                "required": "required",
                "lang": "en",
                "inputmode": "decimal",
            }
        )
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 3})

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance


class CleanupForm(forms.Form):
    """Cleanup form."""

    from_date = forms.DateTimeField(
        label="From",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
        required=False,
    )
    to_date = forms.DateTimeField(
        label="To",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
        required=False,
    )
    remove_deleted_docs = forms.BooleanField(
        label="Deleted documents",
        required=False,
    )
    remove_previous_revisions = forms.BooleanField(
        label="Previous revisions",
        required=False,
    )
    remove_archived_revisions = forms.BooleanField(
        label="Revisions of archived documents",
        required=False,
    )
    remove_unused_tags = forms.BooleanField(
        label="Unused tags",
        required=False,
    )
    remove_deleted_timerecords = forms.BooleanField(
        label="Deleted time records",
        required=False,
    )
    remove_settled_timerecords = forms.BooleanField(
        label="Settled time records",
        required=False,
    )
    undo_delete_timerecords = forms.BooleanField(
        label="Undelete time records",
        required=False,
    )
    undo_settle_timerecords = forms.BooleanField(
        label="Unsettle time records",
        required=False,
    )
    do_commit = forms.BooleanField(
        label="Commit the transaction (if not checked, the system does a fake cleanup)",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Do CleanUp', css_class="btn btn-secondary"))
        layout = [
            Row(
                Column(
                    Div(
                        HTML("<p>If a date is set, only entries created after the specified date are affected by the deletion.</p>"),
                        "from_date",
                        css_class="border rounded py-2 px-3",
                    ),
                    css_class="col-md-6 mb-0"),
                Column(
                    Div(
                        HTML("<p>If a date is set, only entries that were created before the specified date are affected by the deletion.</p>"),
                        "to_date",
                        css_class="border rounded py-2 px-3",
                    ),
                    css_class="col-md-6 mb-0"),
                css_class="mb-3",
            ),
            Row(
                Column(
                    Div(
                        HTML("<p>Please select the entity types that are to be permanently removed.</p>"),
                        "remove_deleted_docs",
                        "remove_previous_revisions",
                        "remove_archived_revisions",
                        "remove_unused_tags",
                        "remove_deleted_timerecords",
                        "remove_settled_timerecords",
                        css_class="border rounded py-2 px-3",
                    ),
                    css_class="col-md-6",
                ),
                Column(
                    Div(
                        HTML("<p>Please specify which time entries are to be restored.</p>"),
                        "undo_delete_timerecords",
                        "undo_settle_timerecords",
                        css_class="border rounded py-2 px-3"
                    ),
                    css_class="col-md-6",
                ),
                css_class="mb-3",
            ),
        ]

        if args and isinstance(args[0], dict) and args[0]:
            # The field below is only part of the form if the request method is post.
            layout.append(Div("do_commit", css_class="mt-4"))

        self.helper.layout = Layout(*layout)

    def clean(self):
        cleaned_data = super().clean()

        # remove_* Checkboxen)
        remove_flags = [
            cleaned_data.get("remove_deleted_docs"),
            cleaned_data.get("remove_previous_revisions"),
            cleaned_data.get("remove_deleted_timerecords"),
            cleaned_data.get("remove_settled_timerecords"),
        ]

        # undo_* Checkboxen)
        undo_flags = [
            cleaned_data.get("undo_delete_timerecords"),
            cleaned_data.get("undo_settle_timerecords"),
        ]

        # Prüfen, ob in beiden Gruppen Checkboxen aktiviert wurden
        if any(remove_flags) and any(undo_flags):
            raise forms.ValidationError(
                "Please select either deletions or restorations - not both at the same time."
            )

        return cleaned_data


class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'position', 'description', 'checked']
        widgets = {
            'id': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False


ChecklistItemFormSet = modelformset_factory(
    ChecklistItem,
    form=ChecklistItemForm,
    extra=1,
    can_order=True,
    can_delete=False
)

from django import forms
from django.contrib.auth.models import User

from archival.models import ArchivalRecord
from authority.models import Entity


RICHTEXT_ATTRS = {
    'class': 'richtext',
    'rows': 8,
}


class HTML5DateInput(forms.DateInput):

    input_type = 'date'


class ArchivalRecordEditForm(forms.ModelForm):

    disabled_fields = (
        'arrangement', 'cataloguer', 'copyright_status', 'description_date',
        'extent', 'physical_description', 'provenance', 'rcin', 'record_type',
        'repository', 'rights_declaration', 'withheld'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            # Due to polymorphic model, some fields are not going to exist.
            try:
                self.fields[field].disabled = True
            except KeyError:
                pass

    class Meta:
        model = ArchivalRecord
        exclude = []
        widgets = {
            'administrative_history': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'arrangement': forms.Textarea(),
            'description': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'description_date': HTML5DateInput(),
            'end_date': HTML5DateInput(),
            'languages': forms.SelectMultiple(attrs={'size': 4}),
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'physical_description': forms.Textarea(),
            'provenance': forms.Textarea(attrs={'rows': 4}),
            'rights_declaration': forms.Textarea(),
            'start_date': HTML5DateInput(),
        }


class EntityEditForm(forms.ModelForm):

    disabled_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = Entity
        exclude = []
        widgets = {
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
        }


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

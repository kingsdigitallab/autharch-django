from django import forms
from django.contrib.auth.models import User

from archival.models import ArchivalRecord
from authority.models import (
    BiographyHistory, Description, Entity, Event, Identity, LanguageScript,
    LegalStatus, LocalDescription, Mandate, NameEntry, NamePart, Place,
    Relation, Resource
)


RICHTEXT_ATTRS = {
    'class': 'richtext',
    'rows': 8,
}


class HTML5DateInput(forms.DateInput):

    input_type = 'date'


class ContainerModelForm(forms.ModelForm):

    """Base class for model forms that have associated inline formsets.

    These inline formsets must be individually created and added to
    self.formsets in _add_formsets. Each must have its own prefix,
    consisting of self.prefix and something corresponding to the
    inline.

    The formsets are stored in a dictionary, to allow for reference in
    a template to a specific formset, for custom display. Note that
    general rendering of the form will *not* work, since the contained
    formsets will not render (including the management forms) and
    validation of supplied data will therefore fail.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formsets = self._add_formsets(*args, **kwargs)

    def _add_formsets(self, *args, **kwargs):
        raise NotImplementedError

    def formsets_are_valid(self):
        for formset in self.formsets.values():
            if not formset.is_valid():
                return False
        return True

    def is_valid(self):
        return super().is_valid() and self.formsets_are_valid()

    def save(self, commit=True):
        result = super().save(commit)
        for formset in self.formsets.values():
            formset.save(commit)
        return result


class NamePartEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = NamePart


class EventEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Event


class LanguageScriptEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LanguageScript


class LegalStatusEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LegalStatus


class LocalDescriptionEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LocalDescription


class MandateEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Mandate


class PlaceEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Place


class RelationEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Relation


class ResourceEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Resource


class BiographyHistoryEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        EventFormset = forms.models.inlineformset_factory(
            BiographyHistory, Event, form=EventEditInlineForm, extra=0)
        formsets['events'] = EventFormset(
            data, instance=self.instance, prefix=self.prefix + '-event')
        return formsets

    class Meta:
        exclude = []
        model = BiographyHistory


class DescriptionEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        instance = self.instance
        prefix = self.prefix
        PlaceFormset = forms.models.inlineformset_factory(
            Description, Place, form=PlaceEditInlineForm, extra=0)
        formsets['places'] = PlaceFormset(
            data, instance=instance, prefix=prefix + '-place')
        LanguageScriptFormset = forms.models.inlineformset_factory(
            Description, LanguageScript, form=LanguageScriptEditInlineForm,
            extra=0)
        formsets['language_scripts'] = LanguageScriptFormset(
            data, instance=instance, prefix=prefix + '-language_script')
        BiographyHistoryFormset = forms.models.inlineformset_factory(
            Description, BiographyHistory, form=BiographyHistoryEditInlineForm,
            extra=0)
        formsets['biography_histories'] = BiographyHistoryFormset(
            data, instance=instance, prefix=prefix + '-biography_history')
        LocalDescriptionFormset = forms.models.inlineformset_factory(
            Description, LocalDescription, form=LocalDescriptionEditInlineForm,
            extra=0)
        formsets['local_descriptions'] = LocalDescriptionFormset(
            data, instance=instance, prefix=prefix + '-local_description')
        MandateFormset = forms.models.inlineformset_factory(
            Description, Mandate, form=MandateEditInlineForm, extra=0)
        formsets['mandates'] = MandateFormset(
            data, instance=instance, prefix=prefix + '-mandate')
        LegalStatusFormset = forms.models.inlineformset_factory(
            Description, LegalStatus, form=LegalStatusEditInlineForm,
            extra=0)
        formsets['legal_statuses'] = LegalStatusFormset(
            data, instance=instance, prefix=prefix + '-legal_status')
        return formsets

    class Meta:
        exclude = []
        model = Description


class NameEntryEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        NamePartFormset = forms.models.inlineformset_factory(
            NameEntry, NamePart, form=NamePartEditInlineForm, extra=0)
        formsets['name_parts'] = NamePartFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_part')
        return formsets

    class Meta:
        exclude = []
        model = NameEntry


class IdentityEditInlineForm(ContainerModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        NameEntryFormset = forms.models.inlineformset_factory(
            Identity, NameEntry, exclude=[], form=NameEntryEditInlineForm,
            extra=0)
        formsets['name_entries'] = NameEntryFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_entry')
        DescriptionFormset = forms.models.inlineformset_factory(
            Identity, Description, exclude=[], form=DescriptionEditInlineForm,
            extra=0)
        formsets['descriptions'] = DescriptionFormset(
            data, instance=self.instance, prefix=self.prefix + '-description')
        RelationFormset = forms.models.inlineformset_factory(
            Identity, Relation, exclude=[], form=RelationEditInlineForm,
            extra=0)
        formsets['relations'] = RelationFormset(
            data, instance=self.instance, prefix=self.prefix + '-relation')
        ResourceFormset = forms.models.inlineformset_factory(
            Identity, Resource, exclude=[], form=ResourceEditInlineForm,
            extra=0)
        formsets['resources'] = ResourceFormset(
            data, instance=self.instance, prefix=self.prefix + '-resource')
        return formsets

    class Meta:
        model = Identity
        exclude = []


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


class EntityEditForm(ContainerModelForm):

    disabled_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        IdentityFormset = forms.models.inlineformset_factory(
            Entity, Identity, exclude=[], form=IdentityEditInlineForm,
            extra=0)
        identity_formset = IdentityFormset(*args, instance=self.instance,
                                           prefix='identity')
        formsets['identities'] = identity_formset
        return formsets

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

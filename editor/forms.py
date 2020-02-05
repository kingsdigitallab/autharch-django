from django import forms
from django.contrib.auth.models import User

import haystack.forms
from haystack.query import SQ

from archival.models import Collection, File, Item, Series
from authority.models import (
    BiographyHistory, Control, Description, Function, Entity, Event, Identity,
    LanguageScript, LegalStatus, LocalDescription, Mandate, NameEntry,
    NamePart, Place, Relation, Resource, Source
)
from .models import EditorProfile


RICHTEXT_ATTRS = {
    'class': 'richtext',
    'rows': 8,
}

SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search our catalogue',
    'type': 'search',
}

SEARCH_SELECT_ATTRS = {
    'class': 'select-with-search',
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

    def has_changed(self):
        return bool(self.changed_data) or \
            any(formset.has_changed() for formset in self.formsets.values())

    def is_valid(self):
        return super().is_valid() and \
            all(formset.is_valid() for formset in self.formsets.values())

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


class FunctionEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Function


class LanguageScriptEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LanguageScript


class LegalStatusEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LegalStatus
        widgets = {
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'citation': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


class LocalDescriptionEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = LocalDescription


class MandateEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Mandate
        widgets = {
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'citation': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


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
        widgets = {
            'citation': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


class SourceEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Source


class BiographyHistoryEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = BiographyHistory
        widgets = {
            'abstract': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'content': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'structure_or_genealogy': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'sources': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'copyright': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


class ControlEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        SourceFormset = forms.models.inlineformset_factory(
            Control, Source, form=SourceEditInlineForm, extra=0)
        formsets['sources'] = SourceFormset(
            data, instance=self.instance, prefix=self.prefix + '-source')
        return formsets

    class Meta:
        exclude = []
        model = Control


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
        EventFormset = forms.models.inlineformset_factory(
            Description, Event, form=EventEditInlineForm, extra=0)
        formsets['events'] = EventFormset(
            data, instance=instance, prefix=prefix + '-event')
        FunctionFormset = forms.models.inlineformset_factory(
            Description, Function, form=FunctionEditInlineForm, extra=0)
        formsets['functions'] = FunctionFormset(
            data, instance=instance, prefix=prefix + '-function')
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

    """Base class for all ArchivalRecord forms.

    The intention is that this class carries as much of the
    configuration for all of the polymorphic models as possible, even
    when they do not apply to a subclass. Only the Meta.model should
    change.

    """

    disabled_fields = [
        'arrangement', 'cataloguer', 'copyright_status',
        'description_date', 'extent', 'physical_description',
        'provenance', 'rcin', 'record_type', 'repository',
        'rights_declaration', 'withheld'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            # Due to polymorphic model, some fields are not going
            # to exist.
            try:
                self.fields[field].disabled = True
            except KeyError:
                pass

    class Meta:
        exclude = []
        widgets = {
            'administrative_history': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'arrangement': forms.Textarea(),
            'description': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'end_date': HTML5DateInput(),
            'languages': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'creators': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'parent_file': forms.Select(attrs=SEARCH_SELECT_ATTRS),
            'parent_series': forms.Select(attrs=SEARCH_SELECT_ATTRS),
            'persons_as_relations': forms.SelectMultiple(
                attrs=SEARCH_SELECT_ATTRS),
            'persons_as_subjects': forms.SelectMultiple(
                attrs=SEARCH_SELECT_ATTRS),
            'physical_description': forms.Textarea(),
            'project': forms.HiddenInput(),
            'provenance': forms.Textarea(attrs={'rows': 4}),
            'rights_declaration': forms.Textarea(),
            'start_date': HTML5DateInput(),
            'uuid': forms.HiddenInput()
        }


class CollectionArchivalRecordEditForm(ArchivalRecordEditForm):

    class Meta(ArchivalRecordEditForm.Meta):
        model = Collection


class FileArchivalRecordEditForm(ArchivalRecordEditForm):

    class Meta(ArchivalRecordEditForm.Meta):
        model = File


class ItemArchivalRecordEditForm(ArchivalRecordEditForm):

    class Meta(ArchivalRecordEditForm.Meta):
        model = Item


class SeriesArchivalRecordEditForm(ArchivalRecordEditForm):

    class Meta(ArchivalRecordEditForm.Meta):
        model = Series


class EntityEditForm(ContainerModelForm):

    disabled_fields = ['entity_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        IdentityFormset = forms.models.inlineformset_factory(
            Entity, Identity, exclude=[], form=IdentityEditInlineForm,
            extra=0)
        formsets['identities'] = IdentityFormset(*args, instance=self.instance,
                                                 prefix='identity')
        ControlFormset = forms.models.inlineformset_factory(
            Entity, Control, exclude=[], form=ControlEditInlineForm, extra=1,
            max_num=1, validate_max=True)
        formsets['control'] = ControlFormset(*args, instance=self.instance,
                                             prefix='control')
        return formsets

    class Meta:
        model = Entity
        exclude = []
        widgets = {
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
        }


class LogForm(forms.Form):

    comment = forms.CharField(label='Comments', widget=forms.Textarea)


# User dashboard forms.

class EditorProfileEditInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_changed(self):
        return bool(self.changed_data)

    def is_valid(self):
        return super().is_valid()

    class Meta:
        model = EditorProfile
        fields = ['role']


class UserEditForm(forms.ModelForm):

    """Form for editing basic details of a user (not password, not editor
    role)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserForm(ContainerModelForm):

    """Form for deleting a user or editing its associated editor
    profile."""

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        EditorProfileFormset = forms.models.inlineformset_factory(
            User, EditorProfile, exclude=[], form=EditorProfileEditInlineForm,
            extra=0)
        formsets['editor_profile'] = EditorProfileFormset(
            data, *args, instance=self.instance,
            prefix=self.prefix + '-editor_profile')
        return formsets

    class Meta:
        model = User
        fields = ['id']


# Search forms.

class FacetedSearchForm(haystack.forms.SearchForm):

    """We do not want the faceting to narrow the results searched over,
    but rather for them to be ORed together as a filter. Therefore do
    not inherit from haystack.forms.FacetedSearchForm."""

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(attrs=SEARCH_INPUT_ATTRS))

    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop('selected_facets', [])
        super().__init__(*args, **kwargs)

    def _apply_facets(self, sqs):
        query = None
        previous_field = None
        for facet in sorted(self.selected_facets):
            if ':' not in facet:
                continue
            field, value = facet.split(':', 1)
            if value:
                if query is None:
                    query = SQ(**{field: sqs.query.clean(value)})
                elif field == previous_field:
                    query = query | SQ(**{field: sqs.query.clean(value)})
                else:
                    query = query & SQ(**{field: sqs.query.clean(value)})
        if query is not None:
            sqs = sqs.filter(query)
        return sqs

    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        sqs = super().search()
        sqs = self._apply_facets(sqs)
        return sqs


class SearchForm(haystack.forms.SearchForm):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(attrs=SEARCH_INPUT_ATTRS))

    def no_query_found(self):
        return self.searchqueryset.all()


def get_archival_record_edit_form_for_subclass(instance):
    """Returns the appropriate subclass of ArchivalRecordEditForm for the
    type of `instance`."""
    # Rather than do generic cleverness with getattr, just enumerate
    # the options.
    #
    # However, if ever there was a tempting situation to engage in
    # metaclass programming etc, it's with this whole situation.
    if isinstance(instance, Collection):
        return CollectionArchivalRecordEditForm
    elif isinstance(instance, File):
        return FileArchivalRecordEditForm
    elif isinstance(instance, Item):
        return ItemArchivalRecordEditForm
    elif isinstance(instance, Series):
        return SeriesArchivalRecordEditForm
    else:
        raise Exception('Trying to get an ArchivalRecordEditForm subclass'
                        ' for an unrecognised ArchivalRecord subclass.')

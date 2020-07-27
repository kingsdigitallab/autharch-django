from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm \
    as DjangoPasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

import haystack.forms

from geonames_place.widgets import PlaceSelect, PlaceSelectMultiple

from archival.models import (
    ArchivalRecord, ArchivalRecordTranscription, Collection, File, Item,
    OriginLocation, Reference, RelatedMaterialReference, Series
)
from authority.models import (
    BiographyHistory, Control, Description, Function, Entity, Event, Identity,
    LanguageScript, LegalStatus, LocalDescription, Mandate, NameEntry,
    NamePart, Place, Relation, Resource, Source
)
from jargon.models import EntityType, NamePartType, PublicationStatus

from .constants import CORPORATE_BODY_ENTITY_TYPE, PERSON_ENTITY_TYPE
from .models import EditorProfile
from .widgets import FunctionMultiSelect, FunctionSelect, GenderSelect


RICHTEXT_ATTRS = {
    'class': 'richtext',
    'rows': 8,
    'aria-label': 'richtext field'
}

RICHTEXT_TRANSCRIPTION = {
    'class': 'richtext-transcription',
    'rows': 8,
    'aria-label': 'richtext field'
}

PSEUDO_CHECKBOX = {
    'class': 'pseudo-checkbox',
}

DATE_FORMAT = {
    'placeholder': 'YYYY-MM-DD',
    'onfocus': "this.placeholder=''",
    'onblur': "this.placeholder='YYYY-MM-DD'"
}

ENTITY_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search all people and corporate bodies',
    'type': 'search',
}

DELETED_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search all deleted objects',
    'type': 'search',
}

RECORD_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search all archival records',
    'type': 'search',
}

RECORD_SEARCH_START_YEAR_INPUT_ATTRS = {
    'aria-label': 'Start year',
    'form': 'record-search-form',
}

RECORD_SEARCH_END_YEAR_INPUT_ATTRS = {
    'aria-label': 'End year',
    'form': 'record-search-form',
}

SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search catalogue',
    'type': 'search',
}

SEARCH_SELECT_ATTRS = {
    'class': 'select-with-search',
    'aria-label': 'select-with-search'
}

SEARCH_SELECT_ATTRS_DYNAMIC = {
    'class': 'select-with-search-dynamic',
    'aria-label': 'select-with-search'
}


ENTITY_START_DATE_HELP = 'This element indicates a date of existence - birth date for people and existence date for corporate bodies. <br><br>1. It is required that you follow the date format: <br><strong>(-)YYYY(-MM(-DD))</strong><br><em>e.g., 1822-03-27, 1822-03, 1822, or, if BC, -750.</em><br>2. To also assist with improving date searching, please always add a date range:<br><em>e.g., if the display date is 1822, include Identity existed from: 1822, Identity existed until: 1822.</em><br><br>NB: Date ranges for years prior to the change in calendar may need to be taken into account. <br>NB: For dates spanning the change in calendars from Julian to Gregorian in many European countries and their colonies, include New Style dates for machine-reading. Old Style dates can be included in the display date field where needed.'  # noqa
ENTITY_END_DATE_HELP = 'This element indicates a date of existence - death date for people and extinction date for corporate bodies. <br><br>1. It is required that you follow the date format: <br><strong>(-)YYYY(-MM(-DD))</strong><br><em>e.g., 1822-03-27, 1822-03, 1822, or, if BC, -750.</em><br>2. To also assist with improving date searching, please always add a date range:<br><em>e.g., if the display date is 1822, include Identity existed from: 1822, Identity existed until: 1822.</em><br><br>NB: Date ranges for years prior to the change in calendar may need to be taken into account. <br>NB: For dates spanning the change in calendars from Julian to Gregorian in many European countries and their colonies, include New Style dates for machine-reading. Old Style dates can be included in the display date field where needed.'  # noqa


class RelatedMaterialRecordChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return ', '.join([str(ref) for ref in obj.references.all()])


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

    @property
    def media(self):
        media = super().media
        for formset in self.formsets.values():
            media += formset.media
        return media

    def save(self, commit=True):
        result = super().save(commit)
        for formset in self.formsets.values():
            formset.save(commit)
        return result


class ArchivalRecordTranscriptionEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = ArchivalRecordTranscription
        widgets = {
            'transcription': forms.Textarea(attrs=RICHTEXT_TRANSCRIPTION),
        }


class NamePartEditInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name_part_type'].queryset = NamePartType.objects.filter(
            entity_type=self.Meta.entity_type)

    class Meta:
        exclude = []
        model = NamePart


class EventEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Event
        labels = {
            'date_from': 'Event date from',
            'date_to': 'Event date until',
        }
        widgets = {
            'place': PlaceSelect(),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


class FunctionEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Function
        labels = {
            'date_from': 'Date function active from',
            'date_to': 'Date function active until',
            'display_date': 'Date function active',
        }
        widgets = {
            'title': FunctionSelect(),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


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
        labels = {
            'date_from': 'Gender used from',
            'date_to': 'Gender used until',
            'display_date': 'Display date gender used',
        }
        widgets = {
            'citation': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'gender': GenderSelect(),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


class MandateEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Mandate
        widgets = {
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'citation': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


class OriginLocationEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = OriginLocation


class PlaceEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Place
        widgets = {
            'place': PlaceSelect(),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


class RelatedMaterialEditInlineForm(forms.ModelForm):

    related_record = RelatedMaterialRecordChoiceField(
        label='Related material', queryset=ArchivalRecord.objects.all(),
        widget=forms.Select(attrs=SEARCH_SELECT_ATTRS_DYNAMIC))

    class Meta:
        exclude = []
        model = RelatedMaterialReference


class RelationEditInlineForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = Relation
        widgets = {
            'place': PlaceSelect(),
            'related_entity': forms.Select(attrs=SEARCH_SELECT_ATTRS_DYNAMIC),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


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
        widgets = {
            'name': forms.Textarea(attrs=RICHTEXT_ATTRS)
        }


class BiographyHistoryEditInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.entity_type == PERSON_ENTITY_TYPE:
            self.fields['content'].label = 'Biography'
            self.fields['sources'].label = 'Biography sources'
            self.fields['copyright'].label = \
                'Biography Digital Rights Statement'
        elif self.Meta.entity_type == CORPORATE_BODY_ENTITY_TYPE:
            self.fields['content'].label = 'History'
            self.fields['sources'].label = 'History sources'
            self.fields['copyright'].label = 'History Digital Rights Statement'

    class Meta:
        exclude = []
        model = BiographyHistory
        widgets = {
            'abstract': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'content': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'sources': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'copyright': forms.Textarea(attrs=RICHTEXT_ATTRS),
        }


class ControlEditInlineForm(ContainerModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maintenance_status'].disabled = True
        if self.Meta.editor_role == EditorProfile.EDITOR:
            in_process_status = PublicationStatus.objects.get(
                title='inProcess')
            self.fields['publication_status'].widget = forms.Select(
                choices=[(in_process_status.pk, 'inProcess')])
            self.fields['publication_status'].disabled = True

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        SourceFormset = inlineformset_factory(
            Control, Source, form=SourceEditInlineForm, extra=0, min_num=1,
            validate_min=True)
        formsets['sources'] = SourceFormset(
            data, instance=self.instance, prefix=self.prefix + '-source')
        return formsets

    class Meta:
        exclude = []
        model = Control
        widgets = {
            'rights_declaration': forms.Textarea(attrs=RICHTEXT_ATTRS)
        }


class DescriptionEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        instance = self.instance
        prefix = self.prefix
        PlaceFormset = inlineformset_factory(
            Description, Place, form=PlaceEditInlineForm, extra=0)
        formsets['places'] = PlaceFormset(
            data, instance=instance, prefix=prefix + '-place')
        EventFormset = inlineformset_factory(
            Description, Event, form=EventEditInlineForm, extra=0)
        formsets['events'] = EventFormset(
            data, instance=instance, prefix=prefix + '-event')
        function_kwargs = {}
        if self.Meta.entity_type == CORPORATE_BODY_ENTITY_TYPE:
            function_kwargs['min_num'] = 1
            function_kwargs['validate_min'] = True
        FunctionFormset = inlineformset_factory(
            Description, Function, form=FunctionEditInlineForm, extra=0,
            **function_kwargs)
        formsets['functions'] = FunctionFormset(
            data, instance=instance, prefix=prefix + '-function')
        LanguageScriptFormset = inlineformset_factory(
            Description, LanguageScript, form=LanguageScriptEditInlineForm,
            extra=0)
        formsets['language_scripts'] = LanguageScriptFormset(
            data, instance=instance, prefix=prefix + '-language_script')
        BiographyHistoryFormset = inlineformset_factory(
            Description, BiographyHistory, form=BiographyHistoryEditInlineForm,
            extra=0, entity_type=self.Meta.entity_type)
        formsets['biography_histories'] = BiographyHistoryFormset(
            data, instance=instance, prefix=prefix + '-biography_history')
        if self.Meta.entity_type == PERSON_ENTITY_TYPE:
            LocalDescriptionFormset = inlineformset_factory(
                Description, LocalDescription,
                form=LocalDescriptionEditInlineForm, extra=0, min_num=1,
                validate_min=True)
            formsets['local_descriptions'] = LocalDescriptionFormset(
                data, instance=instance, prefix=prefix + '-local_description')
        if self.Meta.entity_type == CORPORATE_BODY_ENTITY_TYPE:
            MandateFormset = inlineformset_factory(
                Description, Mandate, form=MandateEditInlineForm, extra=0)
            formsets['mandates'] = MandateFormset(
                data, instance=instance, prefix=prefix + '-mandate')
            LegalStatusFormset = inlineformset_factory(
                Description, LegalStatus, form=LegalStatusEditInlineForm,
                extra=0)
            formsets['legal_statuses'] = LegalStatusFormset(
                data, instance=instance, prefix=prefix + '-legal_status')
        return formsets

    class Meta:
        exclude = []
        model = Description


class NameEntryEditInlineForm(ContainerModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.entity_type != PERSON_ENTITY_TYPE:
            del self.fields['is_royal_name']

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        NamePartFormset = inlineformset_factory(
            NameEntry, NamePart, form=NamePartEditInlineForm, extra=0,
            entity_type=self.Meta.entity_type, min_num=1)
        formsets['name_parts'] = NamePartFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_part')
        return formsets

    def clean(self):
        cleaned_data = super().clean()
        # A royal name must have at least a "forename" name part
        # and a "properTitle" name part.
        if cleaned_data.get('is_royal_name'):
            self._validate_royal_name()

    def _validate_royal_name(self):
        forename_type = NamePartType.objects.get(title='forename')
        proper_title_type = NamePartType.objects.get(title='proper title')
        has_forename = False
        has_proper_title = False
        try:
            # The parts may be invalid, in which case we don't
            # want to bother with this check.
            parts_data = self.formsets['name_parts'].cleaned_data
        except AttributeError:
            return
        for part_data in parts_data:
            part_type = part_data.get('name_part_type')
            if part_type == forename_type:
                has_forename = True
            elif part_type == proper_title_type:
                has_proper_title = True
        if not (has_forename and has_proper_title):
            raise forms.ValidationError(
                'A royal name must contain a "forename" part and a '
                '"proper title" part.', code='invalid')

    class Meta:
        exclude = []
        model = NameEntry
        labels = {
            'date_from': 'Name used from',
            'date_to': 'Name used until',
            'display_date': 'Display date name used',
        }
        widgets = {
            'authorised_form': forms.CheckboxInput(attrs=PSEUDO_CHECKBOX),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


class IdentityEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        NameEntryFormset = inlineformset_factory(
            Identity, NameEntry, exclude=[], form=NameEntryEditInlineForm,
            extra=0, min_num=1, validate_min=True,
            entity_type=self.Meta.entity_type)
        formsets['name_entries'] = NameEntryFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_entry')
        DescriptionFormset = inlineformset_factory(
            Identity, Description, exclude=[], form=DescriptionEditInlineForm,
            extra=0, entity_type=self.Meta.entity_type, max_num=1,
            validate_max=True, min_num=1, validate_min=True)
        formsets['descriptions'] = DescriptionFormset(
            data, instance=self.instance, prefix=self.prefix + '-description')
        RelationFormset = inlineformset_factory(
            Identity, Relation, exclude=[], form=RelationEditInlineForm,
            extra=0)
        formsets['relations'] = RelationFormset(
            data, instance=self.instance, prefix=self.prefix + '-relation')
        ResourceFormset = inlineformset_factory(
            Identity, Resource, exclude=[], form=ResourceEditInlineForm,
            extra=0)
        formsets['resources'] = ResourceFormset(
            data, instance=self.instance, prefix=self.prefix + '-resource')
        return formsets

    def clean(self):
        super().clean()
        # One and only one NameEntry associated with an Identity may
        # be marked as being the authorised form.
        self._validate_authorised_form()

    def _validate_authorised_form(self):
        try:
            entries_data = self.formsets['name_entries'].cleaned_data
        except AttributeError:
            return
        count_authorised_forms = 0
        for entry_data in entries_data:
            if entry_data.get('authorised_form'):
                count_authorised_forms += 1
        if count_authorised_forms == 0:
            raise forms.ValidationError(
                'Each identity must have a name entry that is marked as '
                'the authorised form.', code='invalid')
        elif count_authorised_forms > 1:
            raise forms.ValidationError(
                'Each identity must have only one name entry that is marked '
                'as the authorised form.', code='invalid')

    class Meta:
        model = Identity
        exclude = []
        labels = {
            'date_from': 'Identity existed from',
            'date_to': 'Identity existed until',
        }
        help_texts = {
            'date_from': ENTITY_START_DATE_HELP,
            'date_to': ENTITY_END_DATE_HELP,
        }
        widgets = {
            'preferred_identity': forms.CheckboxInput(attrs=PSEUDO_CHECKBOX),
            'date_from': forms.TextInput(attrs=DATE_FORMAT),
            'date_to': forms.TextInput(attrs=DATE_FORMAT)
        }


class ArchivalRecordEditForm(ContainerModelForm):

    """Base class for all ArchivalRecord forms.

    The intention is that this class carries as much of the
    configuration for all of the polymorphic models as possible, even
    when they do not apply to a subclass. Only the Meta.model should
    change.

    """

    calm_references = forms.models.ModelMultipleChoiceField(
        queryset=Reference.objects.filter(source__title='CALM'),
        label='CALM References', widget=forms.SelectMultiple(
            attrs=SEARCH_SELECT_ATTRS))
    ra_references = forms.models.ModelMultipleChoiceField(
        queryset=Reference.objects.filter(source__title='RA'),
        label='RA References', widget=forms.SelectMultiple(
            attrs=SEARCH_SELECT_ATTRS))

    disabled_fields = {
        EditorProfile.ADMIN: [
            'calm_references', 'maintenance_status', 'parent_collection',
            'parent_file', 'parent_series', 'ra_references'],
        EditorProfile.MODERATOR: [
            'arrangement', 'extent', 'maintenance_status', 'parent_collection',
            'parent_file', 'parent_series', 'physical_description',
            'provenance', 'publication_permission', 'ra_references', 'rcin',
            'record_type', 'repository', 'rights_declaration',
            'rights_declaration_citation', 'withheld'
        ],
        EditorProfile.EDITOR: [
            'arrangement', 'extent', 'maintenance_status', 'parent_collection',
            'parent_file', 'parent_series', 'physical_description',
            'provenance', 'publication_permission', 'publication_status',
            'ra_references', 'rcin', 'record_type', 'repository',
            'rights_declaration', 'rights_declaration_citation', 'withheld'
        ],
    }

    # Fields visible only to admin users.
    private_fields = ['calm_references', 'copyright_status',
                      'rights_declaration_abbreviation']

    def __init__(self, *args, editor_role=EditorProfile.EDITOR, **kwargs):
        super().__init__(*args, **kwargs)
        # We are displaying RA and CALM references separately, so
        # remove the field matching the model.
        del self.fields['references']
        if editor_role != EditorProfile.ADMIN:
            for field in self.private_fields:
                try:
                    del self.fields[field]
                except KeyError:
                    pass
        for field in self.disabled_fields[editor_role]:
            # Due to polymorphic model, some fields are not going
            # to exist.
            try:
                self.fields[field].disabled = True
                if field == 'rights_declaration':
                    self.fields[field].widget = forms.Textarea()
            except KeyError:
                pass
        if editor_role == EditorProfile.EDITOR:
            in_process_status = PublicationStatus.objects.get(
                title='inProcess')
            self.fields['publication_status'].widget = forms.Select(
                choices=[(in_process_status.pk, 'inProcess')])
        references = self.instance.references.all()
        self.fields['calm_references'].initial = references.filter(
            source__title='CALM')
        self.fields['ra_references'].initial = references.filter(
            source__title='RA')

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        OriginLocationFormset = inlineformset_factory(
            self.Meta.model, OriginLocation, exclude=[], extra=0,
            form=OriginLocationEditInlineForm, min_num=1)
        formsets['origin_locations'] = OriginLocationFormset(
            *args, instance=self.instance, prefix='origin_location')
        RelatedMaterialFormset = inlineformset_factory(
            self.Meta.model, RelatedMaterialReference, exclude=[], extra=0,
            form=RelatedMaterialEditInlineForm, fk_name='record')
        formsets['related_materials'] = RelatedMaterialFormset(
            *args, instance=self.instance, prefix='related_material')
        TranscriptionFormset = inlineformset_factory(
            self.Meta.model, ArchivalRecordTranscription, exclude=[],
            form=ArchivalRecordTranscriptionEditInlineForm, extra=0)
        formsets['transcriptions'] = TranscriptionFormset(
            *args, instance=self.instance, prefix='transcription')
        return formsets

    class Meta:
        exclude = []
        widgets = {
            'administrative_history': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'arrangement': forms.Textarea(attrs={'rows': 4}),
            'creation_places': PlaceSelectMultiple(),
            'description': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'languages': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'creators': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'notes': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'organisations_as_subjects': forms.SelectMultiple(
                attrs=SEARCH_SELECT_ATTRS),
            'parent_file': forms.Select(attrs=SEARCH_SELECT_ATTRS),
            'parent_series': forms.Select(attrs=SEARCH_SELECT_ATTRS),
            'persons_as_relations': forms.SelectMultiple(
                attrs=SEARCH_SELECT_ATTRS),
            'persons_as_subjects': forms.SelectMultiple(
                attrs=SEARCH_SELECT_ATTRS),
            'physical_description': forms.Textarea(attrs={'rows': 4}),
            'places_as_relations': PlaceSelectMultiple(),
            'places_as_subjects': PlaceSelectMultiple(),
            'project': forms.HiddenInput(),
            'provenance': forms.Textarea(attrs={'rows': 4}),
            'record_type': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'subjects': FunctionMultiSelect(),
            'uuid': forms.HiddenInput(),
            'rights_declaration': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'publications': forms.Textarea(attrs=RICHTEXT_ATTRS),
            'start_date': forms.TextInput(attrs=DATE_FORMAT),
            'end_date': forms.TextInput(attrs=DATE_FORMAT)
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

    def __init__(self, *args, editor_role=EditorProfile.EDITOR, **kwargs):
        self._editor_role = editor_role
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        if self.instance.entity_type.title.lower() == 'person':
            entity_type = PERSON_ENTITY_TYPE
        else:
            entity_type = CORPORATE_BODY_ENTITY_TYPE
        IdentityFormset = inlineformset_factory(
            Entity, Identity, exclude=[], form=IdentityEditInlineForm,
            extra=0, min_num=1, validate_min=True, entity_type=entity_type)
        formsets['identities'] = IdentityFormset(*args, instance=self.instance,
                                                 prefix='identity')
        ControlFormset = inlineformset_factory(
            Entity, Control, exclude=[], form=ControlEditInlineForm,
            max_num=1, validate_max=True, min_num=1, validate_min=True,
            editor_role=self._editor_role)
        formsets['control'] = ControlFormset(*args, instance=self.instance,
                                             prefix='control')
        return formsets

    def clean(self):
        super().clean()
        # One and only one Identity may be marked as being preferred.
        self._validate_preferred_identity()

    def _validate_preferred_identity(self):
        try:
            identities_data = self.formsets['identities'].cleaned_data
        except AttributeError:
            return
        count_preferred_identities = 0
        for identity_data in identities_data:
            if identity_data.get('preferred_identity'):
                count_preferred_identities += 1
        if count_preferred_identities == 0:
            raise forms.ValidationError(
                'One identity must be marked as preferred.', code='invalid')
        elif count_preferred_identities > 1:
            raise forms.ValidationError(
                'Only one identity may be marked as preferred.',
                code='invalid')

    class Meta:
        model = Entity
        exclude = []


class EntityCreateForm(forms.Form):

    entity_type = forms.ModelChoiceField(
        widget=forms.RadioSelect, empty_label=None,
        queryset=EntityType.objects.all())


class LogForm(forms.Form):

    comment = forms.CharField(label='Comments', widget=forms.Textarea)


# User dashboard forms.

class BaseUserFormset(forms.BaseModelFormSet):

    def clean(self):
        # Check that not all admin users are being deleted.
        if any(self.errors):
            return
        admin_remaining = False
        for form in self.forms:
            if form.formsets['editor_profile'].cleaned_data[0]['role'] == \
               EditorProfile.ADMIN and not form.cleaned_data['DELETE']:
                admin_remaining = True
        if not admin_remaining:
            raise forms.ValidationError('There must always be one admin user.',
                                        code='invalid')


class EditorProfileForm(forms.Form):

    # There is a problem I haven't been able to understand or fix with
    # creating an inline object for a parent that doesn't exist yet,
    # hence this non-model form for use when creating new users.

    role = forms.ChoiceField(choices=EditorProfile.ROLE_CHOICES,
                             initial=EditorProfile.VISITOR)


class EditorProfileEditInlineForm(forms.ModelForm):

    def has_changed(self):
        return bool(self.changed_data)

    def is_valid(self):
        return super().is_valid()

    class Meta:
        model = EditorProfile
        fields = ['role']


class UserCreateForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', strip=False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', strip=False,
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        EditorProfileFormset = inlineformset_factory(
            User, EditorProfile, exclude=[], form=EditorProfileEditInlineForm,
            extra=1, max_num=1, validate_max=True)
        formsets['editor_profile'] = EditorProfileFormset(
            *args, prefix='profile')
        return formsets

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The two password fields didn't match.")
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):

    """Form for editing basic details of a user (not password, not editor
    role)."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserForm(ContainerModelForm):

    """Form for deleting a user or editing its associated editor
    profile."""

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        EditorProfileFormset = inlineformset_factory(
            User, EditorProfile, exclude=[], form=EditorProfileEditInlineForm,
            extra=0)
        formsets['editor_profile'] = EditorProfileFormset(
            data, *args, instance=self.instance,
            prefix=self.prefix + '-editor_profile')
        return formsets

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class PasswordChangeForm(DjangoPasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.pop("autofocus", None)


# Search forms.

class FacetedSearchForm(haystack.forms.FacetedSearchForm):

    def no_query_found(self):
        return self.searchqueryset.all()


class ArchivalRecordFacetedSearchForm(FacetedSearchForm):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(
                            attrs=RECORD_SEARCH_INPUT_ATTRS))
    start_year = forms.IntegerField(
        required=False, label='Creation start year', widget=forms.NumberInput(
            attrs=RECORD_SEARCH_START_YEAR_INPUT_ATTRS))
    end_year = forms.IntegerField(
        required=False, label='Creation end year', widget=forms.NumberInput(
            attrs=RECORD_SEARCH_END_YEAR_INPUT_ATTRS))

    def __init__(self, *args, min_year=0, max_year=2040, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_year'].widget.attrs['min'] = min_year
        self.fields['start_year'].widget.attrs['max'] = max_year
        self.fields['start_year'].widget.attrs['placeholder'] = min_year
        self.fields['end_year'].widget.attrs['min'] = min_year
        self.fields['end_year'].widget.attrs['max'] = max_year
        self.fields['end_year'].widget.attrs['placeholder'] = max_year
        self._min_year = min_year
        self._max_year = max_year

    def search(self):
        sqs = super().search()
        if not self.is_valid():
            return self.no_query_found()
        start_year = self.cleaned_data['start_year']
        end_year = self.cleaned_data['end_year']
        if start_year:
            sqs = sqs.filter(dates__gte=start_year)
        if end_year:
            sqs = sqs.filter(dates__lte=end_year)
        return sqs


class EntityFacetedSearchForm(FacetedSearchForm):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(
                            attrs=ENTITY_SEARCH_INPUT_ATTRS))


class DeletedFacetedSearchForm(FacetedSearchForm):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(
                            attrs=DELETED_SEARCH_INPUT_ATTRS))


class SearchForm(haystack.forms.SearchForm):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(attrs=SEARCH_INPUT_ATTRS))

    def no_query_found(self):
        return self.searchqueryset.all()


def assemble_form_errors(form):
    """Return a dictionary of errors for `form` and any formset
    descendants it has.

    The dictionary has keys for field errors and non-field
    errors. Field errors is a Boolean indicating whether there are any
    field errors anywhere. Non-field errors are a list of error
    strings.

    """
    def add_form_errors(errors, form):
        for field, field_errors in form.errors.items():
            if field == '__all__':
                errors['non_field'].extend(field_errors)
            else:
                errors['field'] = True
        if hasattr(form, 'formsets'):
            for formset in form.formsets.values():
                for form in formset.forms:
                    errors = add_form_errors(errors, form)
        return errors

    errors = {'field': False, 'non_field': []}
    errors = add_form_errors(errors, form)
    if not(errors['field'] or errors['non_field']):
        errors = {}
    return errors


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


# Replacements for Django forms functions for creating model formsets,
# since we need to pass information on an Entity or the editing user
# down to the nested inline forms.

def modelform_factory(model, form=forms.models.ModelForm, fields=None,
                      exclude=None, formfield_callback=None, widgets=None,
                      localized_fields=None, labels=None, help_texts=None,
                      error_messages=None, field_classes=None,
                      editor_role=None, entity_type=None):
    """Return a ModelForm containing form fields for the given model."""
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.

    # Build up a list of attributes that the Meta object will have.
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude
    if widgets is not None:
        attrs['widgets'] = widgets
    if localized_fields is not None:
        attrs['localized_fields'] = localized_fields
    if labels is not None:
        attrs['labels'] = labels
    if help_texts is not None:
        attrs['help_texts'] = help_texts
    if error_messages is not None:
        attrs['error_messages'] = error_messages
    if field_classes is not None:
        attrs['field_classes'] = field_classes
    if editor_role is not None:
        attrs['editor_role'] = editor_role
    if entity_type is not None:
        attrs['entity_type'] = entity_type

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    bases = (form.Meta,) if hasattr(form, 'Meta') else ()
    Meta = type('Meta', bases, attrs)
    if formfield_callback:
        Meta.formfield_callback = staticmethod(formfield_callback)
    # Give this new form class a reasonable name.
    class_name = model.__name__ + 'Form'

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }

    if (getattr(Meta, 'fields', None) is None and
            getattr(Meta, 'exclude', None) is None):
        raise ImproperlyConfigured(
            "Calling modelform_factory without defining 'fields' or "
            "'exclude' explicitly is prohibited."
        )

    # Instantiate type(form) in order to use the same metaclass as form.
    return type(form)(class_name, (form,), form_class_attrs)


def modelformset_factory(model, form=forms.models.ModelForm,
                         formfield_callback=None,
                         formset=forms.models.BaseModelFormSet, extra=1,
                         can_delete=False, can_order=False, max_num=None,
                         fields=None, exclude=None, widgets=None,
                         validate_max=False, localized_fields=None,
                         labels=None, help_texts=None, error_messages=None,
                         min_num=None, validate_min=False, field_classes=None,
                         editor_role=None, entity_type=None):
    """Return a FormSet class for the given Django model class."""
    meta = getattr(form, 'Meta', None)
    if (getattr(meta, 'fields', fields) is None and
            getattr(meta, 'exclude', exclude) is None):
        raise ImproperlyConfigured(
            "Calling modelformset_factory without defining 'fields' or "
            "'exclude' explicitly is prohibited."
        )

    form = modelform_factory(
        model, form=form, fields=fields, exclude=exclude,
        formfield_callback=formfield_callback, widgets=widgets,
        localized_fields=localized_fields, labels=labels,
        help_texts=help_texts, error_messages=error_messages,
        field_classes=field_classes, editor_role=editor_role,
        entity_type=entity_type)
    FormSet = forms.formsets.formset_factory(
        form, formset, extra=extra, min_num=min_num, max_num=max_num,
        can_order=can_order, can_delete=can_delete, validate_min=validate_min,
        validate_max=validate_max)
    FormSet.model = model
    return FormSet


def inlineformset_factory(parent_model, model, form=forms.models.ModelForm,
                          formset=forms.models.BaseInlineFormSet, fk_name=None,
                          fields=None, exclude=None, extra=3, can_order=False,
                          can_delete=True, max_num=None,
                          formfield_callback=None, widgets=None,
                          validate_max=False, localized_fields=None,
                          labels=None, help_texts=None, error_messages=None,
                          min_num=None, validate_min=False,
                          field_classes=None, editor_role=None,
                          entity_type=None):
    """Return an ``InlineFormSet`` for the given kwargs."""
    fk = forms.models._get_foreign_key(parent_model, model, fk_name=fk_name)
    # enforce a max_num=1 when the foreign key to the parent model is unique.
    if fk.unique:
        max_num = 1
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'min_num': min_num,
        'max_num': max_num,
        'widgets': widgets,
        'validate_min': validate_min,
        'validate_max': validate_max,
        'localized_fields': localized_fields,
        'labels': labels,
        'help_texts': help_texts,
        'error_messages': error_messages,
        'field_classes': field_classes,
        'editor_role': editor_role,
        'entity_type': entity_type,
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.fk = fk
    return FormSet

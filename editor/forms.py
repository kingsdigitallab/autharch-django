from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm \
    as DjangoPasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

import haystack.forms

# from geonames_place.widgets import PlaceSelect

from archival.models import Collection, File, Item, Series
from authority.models import (
    BiographyHistory, Control, Description, Function, Entity, Event, Identity,
    LanguageScript, LegalStatus, LocalDescription, Mandate, NameEntry,
    NamePart, Place, Relation, Resource, Source
)
from jargon.models import EntityType, NamePartType

from .constants import CORPORATE_BODY_ENTITY_TYPE, PERSON_ENTITY_TYPE
from .models import EditorProfile
from .widgets import FunctionSelect, HTML5DateInput


RICHTEXT_ATTRS = {
    'class': 'richtext',
    'rows': 8,
    'aria-label': 'richtext field'
}

ENTITY_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search entities',
    'type': 'search',
}

DELETED_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search deleted objects',
    'type': 'search',
}

RECORD_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search archival records',
    'type': 'search',
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
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
            # 'place': PlaceSelect(),
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
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
            'title': FunctionSelect(),
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
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
        }


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
        if self.Meta.entity_type == CORPORATE_BODY_ENTITY_TYPE:
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
        NamePartFormset = inlineformset_factory(
            NameEntry, NamePart, form=NamePartEditInlineForm, extra=0,
            entity_type=self.Meta.entity_type)
        formsets['name_parts'] = NamePartFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_part')
        return formsets

    class Meta:
        exclude = []
        model = NameEntry
        labels = {
            'date_from': 'Name used from',
            'date_to': 'Name used until',
            'display_date': 'Display date name used',
        }
        widgets = {
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
        }


class IdentityEditInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        NameEntryFormset = inlineformset_factory(
            Identity, NameEntry, exclude=[], form=NameEntryEditInlineForm,
            extra=0, entity_type=self.Meta.entity_type)
        formsets['name_entries'] = NameEntryFormset(
            data, instance=self.instance, prefix=self.prefix + '-name_entry')
        DescriptionFormset = inlineformset_factory(
            Identity, Description, exclude=[], form=DescriptionEditInlineForm,
            extra=0, entity_type=self.Meta.entity_type, max_num=1,
            validate_max=True)
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
        labels = {
            'date_from': 'Identity existed from',
            'date_to': 'Identity existed until',
        }
        widgets = {
            'date_from': HTML5DateInput(),
            'date_to': HTML5DateInput(),
        }


class ArchivalRecordEditForm(forms.ModelForm):

    """Base class for all ArchivalRecord forms.

    The intention is that this class carries as much of the
    configuration for all of the polymorphic models as possible, even
    when they do not apply to a subclass. Only the Meta.model should
    change.

    """

    disabled_fields = {
        EditorProfile.ADMIN: [],
        EditorProfile.MODERATOR: [
            'arrangement', 'cataloguer', 'copyright_status',
            'description_date', 'extent', 'physical_description', 'provenance',
            'publication_permission', 'rcin', 'record_type', 'references',
            'repository', 'rights_declaration',
            'rights_declaration_abbreviation', 'rights_declaration_citation',
            'withheld'
        ],
        EditorProfile.EDITOR: [
            'arrangement', 'cataloguer', 'copyright_status',
            'description_date', 'extent', 'physical_description', 'provenance',
            'publication_permission', 'publication_status', 'rcin',
            'record_type', 'references', 'repository', 'rights_declaration',
            'rights_declaration_abbreviation', 'rights_declaration_citation',
            'withheld'
        ],
    }

    def __init__(self, *args, editor_role=EditorProfile.EDITOR, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields[editor_role]:
            # Due to polymorphic model, some fields are not going
            # to exist.
            try:
                self.fields[field].disabled = True
            except KeyError:
                pass

    class Meta:
        exclude = []
        widgets = {
            'references': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
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
            'record_type': forms.SelectMultiple(attrs=SEARCH_SELECT_ATTRS),
            'rights_declaration': forms.Textarea(),
            'start_date': HTML5DateInput(),
            'subjects': FunctionSelect(),
            'transcription': forms.Textarea(attrs=RICHTEXT_ATTRS),
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

    def __init__(self, *args, editor_role=EditorProfile.EDITOR, **kwargs):
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
            extra=0, entity_type=entity_type)
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
            raise forms.ValidationError('There must always be one admin user.')


class EditorProfileForm(forms.Form):

    # There is a problem I haven't been able to understand or fix with
    # creating an inline object for a parent that doesn't exist yet,
    # hence this non-model form for use when creating new users.

    role = forms.ChoiceField(choices=EditorProfile.ROLE_CHOICES,
                             initial=EditorProfile.VISITOR)


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
        EditorProfileFormset = forms.models.inlineformset_factory(
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
        EditorProfileFormset = forms.models.inlineformset_factory(
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
    """Return a list of error dictionaries for `form` and any formset
    descendants it has."""
    def assemble_formset_errors(errors, formset):
        if formset.total_error_count():
            errors.extend(formset.errors)
        for form in formset.forms:
            for formset in form.formsets.values():
                errors = assemble_formset_errors(errors, formset)
        return errors

    errors = []
    if form.errors:
        errors.append(form.errors)
    if hasattr(form, 'formsets'):
        for formset in form.formsets.values():
            errors = assemble_formset_errors(errors, formset)
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
# since we need to pass information on an Entity down to the nested
# inline forms.

def modelform_factory(model, form=forms.models.ModelForm, fields=None,
                      exclude=None, formfield_callback=None, widgets=None,
                      localized_fields=None, labels=None, help_texts=None,
                      error_messages=None, field_classes=None,
                      entity_type=None):
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
                         entity_type=None):
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
        field_classes=field_classes, entity_type=entity_type)
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
                          field_classes=None, entity_type=None):
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
        'entity_type': entity_type,
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.fk = fk
    return FormSet

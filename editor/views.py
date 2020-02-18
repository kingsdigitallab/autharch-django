from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from haystack.generic_views import FacetedSearchView, SearchView
from haystack.query import SearchQuerySet

import reversion
from reversion.models import Revision, Version
from reversion.views import create_revision

from archival.models import ArchivalRecord, Collection, Series, File, Item
from authority.models import Entity

from .forms import (
    EntityCreateForm, EntityEditForm, LogForm, UserCreateForm, UserEditForm,
    UserForm, FacetedSearchForm, PasswordResetForm, SearchForm,
    EditorProfileForm, get_archival_record_edit_form_for_subclass
)
from .models import EditorProfile


def is_user_admin(user):
    try:
        return user.editor_profile.role == EditorProfile.ADMIN
    except AttributeError:
        return False


def is_user_editor_plus(user):
    try:
        return user.editor_profile.role in (
            EditorProfile.ADMIN, EditorProfile.MODERATOR, EditorProfile.EDITOR)
    except AttributeError:
        return False


class HomeView(UserPassesTestMixin, SearchView):

    template_name = 'editor/home.html'
    queryset = SearchQuerySet().models(Collection, Entity, File, Item, Series)
    form_class = SearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = 'home'
        user = self.request.user
        entities, records = self._get_recently_modified(user)
        context['recently_modified_entities'] = entities
        context['recently_modified_records'] = records
        entities, records = self._get_unpublished_records(user)
        context['unpublished_entities'] = entities
        context['unpublished_records'] = records
        return context

    def _get_recently_modified(self, user):
        """Return the archival records and entities most recently modified by
        `user`."""
        entity_versions = Version.objects.get_for_model(Entity).filter(
            revision__user=user)
        record_versions = Version.objects.get_for_model(ArchivalRecord).filter(
            revision__user=user)
        entity_ids = [version.object_id for version in entity_versions]
        record_ids = [version.object_id for version in record_versions]
        entities = Entity.objects.filter(id__in=entity_ids)
        records = ArchivalRecord.objects.filter(id__in=record_ids)
        return entities, records

    def _get_unpublished_records(self, user):
        entities = None
        records = None
        if user.editor_profile.role in (EditorProfile.ADMIN,
                                        EditorProfile.MODERATOR):
            entities = Entity.objects.exclude(
                control__publication_status__title='published')
            records = ArchivalRecord.objects.exclude(
                publication_status__title='published')
        return entities, records

    def test_func(self):
        return is_user_editor_plus(self.request.user)


class EntityListView(UserPassesTestMixin, FacetedSearchView):

    template_name = 'editor/entities_list.html'
    queryset = SearchQuerySet().models(Entity).facet('entity_type',
                                                     sort='index')
    form_class = FacetedSearchForm
    facet_fields = ['entity_type']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = 'entities'
        return context

    def test_func(self):
        return is_user_editor_plus(self.request.user)


class RecordListView(UserPassesTestMixin, FacetedSearchView):

    template_name = 'editor/records_list.html'
    queryset = SearchQuerySet().models(Collection, File, Item, Series).facet(
        'archival_level', order='term').facet('writers', order='term').facet(
        'addressees', order='term').facet('languages', order='term').facet(
        'dates', order='term')
    form_class = FacetedSearchForm
    facet_fields = ['addressees', 'archival_level', 'dates', 'languages',
                    'writers']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query_dict = self.request.GET.copy()
        context['facets'] = self._merge_facets(context['facets'],
                                               query_dict)
        context['current_section'] = 'records'
        context['writer_manager'] = Entity.objects
        return context

    def _create_apply_link(self, value_data, query_dict, facet):

        """Return a link to apply the facet value in `value_data` and False to
        indicate that the facet is not selected."""
        qd = query_dict.copy()
        value = value_data[0]
        facets = qd.getlist('selected_facets')
        new_facet = '{}_exact:{}'.format(facet, value)
        qd.setlist('selected_facets', facets + [new_facet])
        link = '?{}'.format(qd.urlencode())
        return link, False

    def _create_unapply_link(self, value_data, query_dict, facet):
        """Return a link to apply the facet value in `value_data` and True to
        indicate that the facet is selected."""
        qd = query_dict.copy()
        value = value_data[0]
        facets = qd.getlist('selected_facets')
        old_facet = '{}_exact:{}'.format(facet, value)
        facets.remove(old_facet)
        qd.setlist('selected_facets', facets)
        link = qd.urlencode()
        if link:
            link = '?{}'.format(link)
        else:
            link = '.'
        return link, True

    def _merge_facets(self, facets, query_dict):
        """Return the Haystack `facets` annotated with links to apply or
        unapply the facet values. Data from `query_dict` is used to
        determine selected facets."""
        selected_facets = self._split_selected_facets(
            query_dict.getlist('selected_facets'))
        for facet, values in facets['fields'].items():
            # Some facet field values are a model object ID, so get
            # a display string for them.
            display_values = None
            if facet == 'addressees':
                ids = [value[0] for value in values]
                display_values = Entity.objects.filter(id__in=ids)
            elif facet == 'writers':
                ids = [value[0] for value in values]
                display_values = Entity.objects.filter(id__in=ids)
            new_values = []
            for value_data in values:
                if value_data[0] in selected_facets.get(facet, []):
                    link, is_selected = self._create_unapply_link(
                        value_data, query_dict, facet)
                else:
                    link, is_selected = self._create_apply_link(
                        value_data, query_dict, facet)
                if display_values is None:
                    new_values.append((value_data[0], value_data[1], link,
                                       is_selected))
                else:
                    new_values.append(
                        (str(display_values.get(id=value_data[0])),
                         value_data[1], link, is_selected))
            facets['fields'][facet] = new_values
        return facets

    def _split_selected_facets(self, selected_facets):
        """Return a dictionary of selected facet values keyed by the facet
        each belongs to."""
        split_facets = {}
        for selected_facet in selected_facets:
            facet, value = selected_facet.split(':', maxsplit=1)
            facet = facet[:-len('_exact')]
            split_facets.setdefault(facet, []).append(value)
        return split_facets

    def test_func(self):
        return is_user_editor_plus(self.request.user)


@user_passes_test(is_user_editor_plus)
def dashboard(request):
    user = request.user
    AllUsersFormSet = modelformset_factory(
        User, extra=0, can_delete=True, form=UserForm)
    user_form = UserEditForm(instance=user)
    password_form = PasswordChangeForm(user=user)
    all_users_formset = None
    if user.editor_profile.role == EditorProfile.ADMIN:
        all_users_formset = AllUsersFormSet()
    if request.method == 'POST':
        if request.POST.get('user_submit') is not None:
            user_form = UserEditForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                return redirect('editor:dashboard')
        elif request.POST.get('password_submit') is not None:
            password_form = PasswordChangeForm(data=request.POST, user=user)
            if password_form.is_valid():
                password_form.save()
                return redirect('editor:dashboard')
        elif (user.editor_profile.role == EditorProfile.ADMIN and
              request.POST.get('all_users_submit') is not None):
            # Changing editor profile role or deleting user.
            all_users_formset = AllUsersFormSet(request.POST)
            if all_users_formset.is_valid():
                all_users_formset.save()
                return redirect('editor:dashboard')
    context = {
        'current_section': 'account',
        'all_users_formset': all_users_formset,
        'user': user,
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'editor/dashboard.html', context)


@user_passes_test(is_user_editor_plus)
@create_revision()
def entity_create(request):
    if request.method == 'POST':
        form = EntityCreateForm(request.POST)
        if form.is_valid():
            entity = Entity()
            entity.entity_type = form.cleaned_data['entity_type']
            entity.save()
            return redirect('editor:entity-edit', entity_id=entity.pk)
    else:
        form = EntityCreateForm()
    context = {
        'current_section': 'entities',
        'form': form,
    }
    return render(request, 'editor/entity_create.html', context)


@user_passes_test(is_user_editor_plus)
@require_POST
def entity_delete(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.POST.get('DELETE') == 'DELETE':
        entity.delete()
        return redirect('editor:entities-list')
    return redirect('editor:entity-edit', entity_id=entity_id)


@user_passes_test(is_user_editor_plus)
@create_revision()
def entity_edit(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.method == 'POST':
        form = EntityEditForm(request.POST, instance=entity)
        log_form = LogForm(request.POST)
        if form.is_valid() and log_form.is_valid():
            reversion.set_comment(log_form.cleaned_data['comment'])
            form.save()
            return redirect('editor:entity-edit', entity_id=entity_id)
    else:
        form = EntityEditForm(instance=entity)
        log_form = LogForm()
    context = {
        'current_section': 'entities',
        'delete_url': reverse('editor:entity-delete',
                              kwargs={'entity_id': entity_id}),
        'entity': entity,
        'form': form,
        'last_revision': Version.objects.get_for_object(entity)[0].revision,
        'log_form': log_form,
    }
    return render(request, 'editor/entity_edit.html', context)


@user_passes_test(is_user_editor_plus)
def entity_history(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    context = {
        'current_section': 'entities',
        'edit_url': reverse('editor:entity-edit',
                            kwargs={'entity_id': entity_id}),
        'item': entity,
        'versions': Version.objects.get_for_object(entity),
    }
    return render(request, 'editor/history.html', context)


@user_passes_test(is_user_editor_plus)
def password_reset(request, user_id):
    # Avoid revealing valid user IDs.
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    editor = request.user
    if user is None or (editor != user and
                        editor.editor_profile.role != EditorProfile.ADMIN):
        return redirect('editor:dashboard')
    if request.method == 'POST':
        password_form = PasswordResetForm(user=user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            return redirect('editor:dashboard')
    else:
        # removed user=user from arguments
        password_form = PasswordResetForm()
    context = {
        'current_section': 'account',
        'password_form': password_form,
        'user': user,
    }
    return render(request, 'editor/password_reset.html', context)


@user_passes_test(is_user_editor_plus)
@require_POST
def record_delete(request, record_id):
    record = get_object_or_404(ArchivalRecord, pk=record_id)
    if request.POST.get('DELETE') == 'DELETE':
        record.delete()
        return redirect('editor:records-list')
    return redirect('editor:record-edit', record_id=record_id)


@user_passes_test(is_user_editor_plus)
@create_revision()
def record_edit(request, record_id):
    record = get_object_or_404(ArchivalRecord, pk=record_id)
    form_class = get_archival_record_edit_form_for_subclass(record)
    if request.method == 'POST':
        form = form_class(request.POST, instance=record)
        log_form = LogForm(request.POST)
        if form.is_valid() and log_form.is_valid():
            reversion.set_comment(log_form.cleaned_data['comment'])
            form.save()
            return redirect('editor:record-edit', record_id=record_id)
    else:
        form = form_class(instance=record)
        log_form = LogForm()
    context = {
        'current_section': 'records',
        'delete_url': reverse('editor:record-delete',
                              kwargs={'record_id': record_id}),
        'form': form,
        'last_revision': Version.objects.get_for_object(record)[0].revision,
        'log_form': log_form,
        'record': record,
    }
    return render(request, 'editor/record_edit.html', context)


@user_passes_test(is_user_editor_plus)
def record_history(request, record_id):
    record = get_object_or_404(ArchivalRecord, pk=record_id)
    context = {
        'current_section': 'records',
        'edit_url': reverse('editor:record-edit',
                            kwargs={'record_id': record_id}),
        'item': record,
        'versions': Version.objects.get_for_object(record),
    }
    return render(request, 'editor/history.html', context)


@user_passes_test(is_user_editor_plus)
@require_POST
def revert(request):
    revision_id = request.POST.get('revision_id')
    revision = get_object_or_404(Revision, pk=revision_id)
    revision.revert()
    return redirect(request.POST.get('redirect_url'))


@user_passes_test(is_user_admin)
def user_create(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        profile_form = EditorProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            role = profile_form.cleaned_data['role']
            profile = EditorProfile(user=user, role=role)
            profile.save()
            return redirect('editor:dashboard')
    else:
        user_form = UserCreateForm()
        profile_form = EditorProfileForm()
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
    }
    return render(request, 'editor/user_create.html', context)

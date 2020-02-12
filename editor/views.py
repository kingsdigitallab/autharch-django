from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from haystack.generic_views import FacetedSearchView, SearchView
from haystack.query import SearchQuerySet

import reversion
from reversion.models import Version, Revision
from reversion.views import create_revision

from archival.models import ArchivalRecord, Collection, Series, File, Item
from authority.models import Entity

from .forms import (
    EntityCreateForm, EntityEditForm, LogForm, UserEditForm, UserForm,
    FacetedSearchForm, PasswordResetForm, SearchForm,
    get_archival_record_edit_form_for_subclass
)
from .models import EditorProfile


class HomeView(SearchView):

    template_name = 'editor/home.html'
    queryset = SearchQuerySet().models(Collection, Entity, File, Item, Series)
    form_class = SearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = 'home'
        return context


class EntityListView(FacetedSearchView):

    template_name = 'editor/entities_list.html'
    queryset = SearchQuerySet().models(Entity).facet('entity_type',
                                                     sort='index')
    form_class = FacetedSearchForm
    facet_fields = ['entity_type']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = 'entities'
        return context


class RecordListView(FacetedSearchView):

    template_name = 'editor/records_list.html'
    queryset = SearchQuerySet().models(Collection, File, Item, Series).facet(
        'archival_level', sort='index').facet('writers', sort='index')
    form_class = FacetedSearchForm
    facet_fields = ['archival_level', 'writers']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = 'records'
        context['writer_manager'] = Entity.objects
        context['selected_facets'] = self.request.GET.getlist(
            'selected_facets')
        return context


@login_required
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


@require_POST
def entity_delete(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.POST.get('DELETE') == 'DELETE':
        entity.delete()
        return redirect('editor:entities-list')
    return redirect('editor:entity-edit', entity_id=entity_id)


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


def password_reset(request, user_id):
    # Avoid revealing valid user IDs.
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    editor = request.user
    if user is None or (editor != user and
                        editor.editor_profile.role != EditorProfile.ADMIN):
        redirect('editor:dashboard')
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


@require_POST
def record_delete(request, record_id):
    record = get_object_or_404(ArchivalRecord, pk=record_id)
    if request.POST.get('DELETE') == 'DELETE':
        record.delete()
        return redirect('editor:records-list')
    return redirect('editor:record-edit', record_id=record_id)


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


@require_POST
def revert(request):
    revision_id = request.POST.get('revision_id')
    revision = get_object_or_404(Revision, pk=revision_id)
    revision.revert()
    return redirect(request.POST.get('redirect_url'))

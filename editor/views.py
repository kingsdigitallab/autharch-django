from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from reversion.models import Version

from archival.models import ArchivalRecord
from authority.models import Entity

from .forms import ArchivalRecordEditForm, EntityEditForm, UserEditForm


@login_required
def dashboard(request):
    user = request.user
    if request.method == 'POST':
        if request.POST.get('old_password') is not None:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                return redirect('editor:dashboard')
        elif request.POST.get('email') is not None:
            user_form = UserEditForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                return redirect('editor:dashboard')
    else:
        user_form = UserEditForm(instance=user)
        password_form = PasswordChangeForm(user=user)
    context = {
        'current_section': 'account',
        'password_form': password_form,
        'user': user,
        'user_form': user_form,
    }
    return render(request, 'editor/dashboard.html', context)


def entity_create(request):
    context = {
        'current_section': 'entities',
    }
    return render(request, 'editor/entity_create.html', context)


def entity_edit(request, entity_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    if request.method == 'POST':
        form = EntityEditForm(request.POST, instance=entity)
        if form.is_valid():
            form.save()
    else:
        form = EntityEditForm(instance=entity)
    context = {
        'current_section': 'entities',
        'entity': entity,
        'form': form,
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


def entities_list(request):
    entities = Entity.objects.all()
    person_count = entities.filter(entity_type__title='Person').count()
    corporate_body_count = entities.filter(
        entity_type__title='corporateBody').count()
    context = {
        'corporate_body_count': corporate_body_count,
        'current_section': 'entities',
        'entities': entities,
        'entity_count': entities.count(),
        'person_count': person_count,
    }
    return render(request, 'editor/entities_list.html', context)


def record_edit(request, record_id):
    record = get_object_or_404(ArchivalRecord, pk=record_id)
    if request.method == 'POST':
        form = ArchivalRecordEditForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
    else:
        form = ArchivalRecordEditForm(instance=record)
    context = {
        'current_section': 'records',
        'form': form,
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


def records_list(request):
    records = ArchivalRecord.objects.all()
    context = {
        'current_section': 'records',
        'records': records,
        'records_count': records.count(),
    }
    return render(request, 'editor/records_list.html', context)


def home(request):
    entities = Entity.objects.all()
    records = ArchivalRecord.objects.all()
    context = {
        'current_section': 'home',
        'entities': entities,
        'entity_count': entities.count(),
        'records': records,
        'record_count': records.count(),
    }
    return render(request, 'editor/home.html', context)

from django.shortcuts import get_object_or_404, render

from archival.models import ArchivalRecord
from authority.models import Entity

from .forms import ArchivalRecordEditForm, EntityEditForm


def dashboard(request):
    pass


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
        'entity': entity,
    }
    return render(request, 'editor/entity_history.html', context)


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
        'record': record,
    }
    return render(request, 'editor/record_history.html', context)


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

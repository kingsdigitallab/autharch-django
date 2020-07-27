import logging

from django.db import transaction

import pandas as pd

from archival.models import (Item, Project)
from authority.models import Entity
from controlled_vocabulary.utils import search_term_or_none
from django.core.management.base import BaseCommand, CommandError
from jargon.models import (MaintenanceStatus, PublicationStatus, EntityType,
                           Repository, RecordType)
from script_codes.models import Script
import datetime
import re


class Command(BaseCommand):
    args = '<spreadsheet_path>'
    help = 'Imports entity data from a spreadsheet or csv file'
    logger = logging.getLogger(__name__)

    delim = 'QQQQQ'
    language = search_term_or_none('iso639-2', 'eng', exact=True)
    script = Script.objects.get(name='Latin')
    project, _ = Project.objects.get_or_create(
        title='Shakespeare in the Royal Collections',
        slug='sharc')

    et_work, _ = EntityType.objects.get_or_create(
        title='Work'
    )

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_path', nargs=1, type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        path = options['spreadsheet_path'][0]

        if path.endswith('.csv'):
            df = pd.read_csv(path)
        elif path.endswith('.xlsx'):
            df = pd.read_excel(path)
        else:
            raise CommandError(
                'Invalid file type, please provide a csv or xlsx file.')

        for i, row in df.iterrows():
            self._import_row(row)
        raise Exception

    def _import_row(self, row):

        # Gather and cleanse facts
        rcin = 'RCIN {}'.format(self._obj_or_none(
            row, 'Inventory Number (RCIN)'))
        uuid = 'sharc_{}'.format(rcin)
        if Item.objects.filter(uuid=uuid).count() > 0:
            self.stdout.write('Skipping duplicate.')
            return
        category = self._obj_or_none(row, 'Category')
        location = self._obj_or_none(row, 'Location')
        title = self._obj_or_none(row, 'Short Title')
        date_of_creation = self._obj_or_none(row, 'Date of creation')
        doc_notes = self._obj_or_none(row, 'DoC Notes')
        place_of_origin = self._obj_or_none(row, 'Place of origin')
        provenance = self._obj_or_none(row, 'Provenance')
        date_of_aquisition = self._obj_or_none(row, 'Date of acquisition')
        doa_notes = self._obj_or_none(row, 'DoA Notes')
        authors = self._qqqqq(self._obj_or_none(
            row, 'Author(s)/ Artist(s)/ Maker(s)'))
        associated_people = self._qqqqq(
            self._obj_or_none(row, 'Associated people'))
        physical_description = self._obj_or_none(row, 'Physical description')
        size = self._obj_or_none(row, 'Size')
        label = self._obj_or_none(row, 'Label/ inscription/ caption')
        notes = self._obj_or_none(row, 'Notes')
        publication_details = self._obj_or_none(row, 'Publication details')
        shakespeare_connection_works = self._obj_or_none(
            row, 'Shakespeare connection: Individual or Works?')
        shakespeare_connection_relation = self._obj_or_none(
            row, 'Shakespeare connection: How does it relate to the relevant work? ')  # noqa
        shakespeare_connection_secondary = self._obj_or_none(
            row, 'Shakespeare connection: Secondary connection to relevant work?')  # noqa
        shakespeare_connection_rel_work = self._obj_or_none(
            row, 'Shakespeare connection: related work')
        related_entries = self._qqqqq(
            self._obj_or_none(row, 'Related entries'))
        references = self._qqqqq(self._obj_or_none(row, 'References'))

        # Create an object
        obj = Item()
        obj.project = self.project
        obj.uuid = uuid
        obj.rcin = rcin
        obj.repository = Repository.objects.get(code=262)  # Royal Archives?
        obj.title = title
        obj.provenance = provenance
        obj.creation_dates = date_of_creation
        obj.creation_dates_notes = doc_notes

        obj.caption = label

        obj.publication_description = publication_details
        obj.aquisition_dates = date_of_aquisition
        obj.aquisition_dates_notes = doa_notes

        obj.description = physical_description
        obj.description_date = datetime.date.today()
        obj.extent = size

        obj.physical_location = location
        obj.origin_location = place_of_origin

        obj.connection_a = shakespeare_connection_works
        obj.connection_b = shakespeare_connection_relation
        obj.connection_c = shakespeare_connection_secondary

        obj.sources = '\n'.join(references)
        obj.notes = notes

        obj.related_materials = ' '.join(related_entries)

        ps, _ = PublicationStatus.objects.get_or_create(
            title='published')
        obj.publication_status = ps
        ms, _ = MaintenanceStatus.objects.get_or_create(title='new')
        obj.maintenance_status = ms
        obj.language = self.language
        obj.script = self.script
        obj.rights_declaration = """
            <p>
            Images: © HM Queen Elizabeth II - <a
            href="https://creativecommons.org/licenses/by-nc-sa/4.0/">
            CC BY-NC-SA 4.0</a>
            </p>"""

        obj.save()

        # M2M (after save)

        # Related entity:
        if shakespeare_connection_rel_work:
            a, _ = Entity.get_or_create_by_display_name(
                re.sub(r'\(.*\)', '', shakespeare_connection_rel_work),
                self.language, self.script, self.project)
            if _:
                a.project = self.project
                a.entity_type = self.et_work
                a.save()
            obj.related_entities.add(a)

        # - References

        # - Category -> record type
        if category:
            rec_type, _ = RecordType.objects.get_or_create(title=category)
            obj.record_type.add(rec_type)

        # - Languages
        # Place of origin -> creation places

        # Author(s)/ Artist(s)/ Maker(s) -> creators
        for author in authors:
            a, _ = Entity.get_or_create_by_display_name(
                re.sub(r'\(.*\)', '', author), self.language, self.script,
                self.project)
            if _:
                a.project = self.project
                a.save()
            obj.creators.add(a)

        # Associated people -> persons as relations
        for assocpers in associated_people:
            name = re.sub(r'\(.*\)', '', assocpers)
            a, _ = Entity.get_or_create_by_display_name(
                name, self.language, self.script,
                self.project)
            if _:
                a.project = self.project
                a.save()
            if a is None:
                self.stderr.write('Failed creating entity "{}" for {}.'.format(
                    name, rcin))
            obj.persons_as_relations.add(a)

    # There's a reason for this method name... I promise.
    def _qqqqq(self, obj):
        if obj is None:
            return []
        else:
            return [o.strip() for o in str(obj).split(self.delim)]

    def _obj_or_none(self, row, key):
        if key not in row:
            return None
        if pd.isnull(row[key]):
            return None
        else:
            data = row[key]
            if isinstance(data, str):
                return data.strip() or None
            else:
                return data

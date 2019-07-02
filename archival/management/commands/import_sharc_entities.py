import logging

import pandas as pd
from archival.models import Project
from authority.models import (Entity, Identity, Relation, NameEntry,
                              Control, Source)
from django.core.management.base import BaseCommand, CommandError
from jargon.models import (PublicationStatus, EntityRelationType,
                           EntityType, MaintenanceStatus)
from languages_plus.models import Language
from script_codes.models import Script
import re


class Command(BaseCommand):
    args = '<spreadsheet_path>'
    help = 'Imports entity data from a spreadsheet or csv file'
    logger = logging.getLogger(__name__)

    maintenance_status, _ = MaintenanceStatus.objects.get_or_create(
        title='new')
    publication_status, _ = PublicationStatus.objects.get_or_create(
        title='published'
    )
    language = Language.objects.get(name_en='English')
    script = Script.objects.get(name='Latin')

    project, _ = Project.objects.get_or_create(
        title='Shakespeare in the Royal Collections',
        slug='SHARC')

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_path', nargs=1, type=str)

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

    def _import_row(self, row):

        entity_type = self._obj_or_none(row, 'Type')

        if not pd.isnull(entity_type):
            # Gather and cleanse facts
            name_and_date = self._obj_or_none(row, 'Authoritative name (full)')
            name = re.sub(r'\(.*\)', '', name_and_date)
            name = name.replace(' ,', ',')
            date = re.search(r'\((.*?)\)', name_and_date).group(1)

            name_1 = self._obj_or_none(row, 'Alt Name 1')
            date_1 = self._obj_or_none(row, 'Use Dates 1')
            name_2 = self._obj_or_none(row, 'Alt name 2')
            date_2 = self._obj_or_none(row, 'Use dates 2')
            name_3 = self._obj_or_none(row, 'Alt name 3')
            date_3 = self._obj_or_none(row, 'Use dates 3')
            name_4 = self._obj_or_none(row, 'Alt name 4')
            date_4 = self._obj_or_none(row, 'Use dates 4')
            name_5 = self._obj_or_none(row, 'Alt name 5')
            date_5 = self._obj_or_none(row, 'Use dates 5')

            bd_dates = self._obj_or_none(row, 'birth and death Dates')

            relationships = self._obj_or_none(row, 'Key relationships')

            viaf = self._obj_or_none(row, 'VIAF link')

            # Create!
            et, _ = EntityType.objects.get_or_create(title=entity_type)

            entity = Entity(entity_type=et)
            entity.project = self.project
            entity.display_date = bd_dates
            entity.save()

            identity = Identity(entity=entity)
            identity.display_date = date
            identity.preferred_identity = True
            identity.save()

            # Relationships!
            if relationships is not None:
                rel_type, _ = EntityRelationType.objects.get_or_create(
                    title="SHARC_KEY")

                rel_list = relationships.split(',')
                for rel in rel_list:
                    r = Relation()
                    r.identity = identity
                    r.relation_detail = rel
                    r.relation_type = rel_type
                    r.save()

            name_entry = NameEntry(identity=identity)
            name_entry.display_name = name
            name_entry.authorised_form = True
            name_entry.display_date = identity.display_date
            name_entry.language = self.language
            name_entry.script = self.script
            name_entry.save()

            if name_1:
                identity = Identity(entity=entity)
                identity.display_date = date_1
                identity.preferred_identity = False
                identity.save()

                name_entry = NameEntry(identity=identity)
                name_entry.display_name = name_1
                name_entry.authorised_form = True
                name_entry.display_date = identity.display_date
                name_entry.language = self.language
                name_entry.script = self.script
                name_entry.save()

            if name_2:
                identity = Identity(entity=entity)
                identity.display_date = date_2
                identity.preferred_identity = False
                identity.save()

                name_entry = NameEntry(identity=identity)
                name_entry.display_name = name_2
                name_entry.authorised_form = True
                name_entry.display_date = identity.display_date
                name_entry.language = self.language
                name_entry.script = self.script
                name_entry.save()

            if name_3:
                identity = Identity(entity=entity)
                identity.display_date = date_3
                identity.preferred_identity = False
                identity.save()

                name_entry = NameEntry(identity=identity)
                name_entry.display_name = name_3
                name_entry.authorised_form = True
                name_entry.display_date = identity.display_date
                name_entry.language = self.language
                name_entry.script = self.script
                name_entry.save()

            if name_4:
                identity = Identity(entity=entity)
                identity.display_date = date_4
                identity.preferred_identity = False
                identity.save()

                name_entry = NameEntry(identity=identity)
                name_entry.display_name = name_4
                name_entry.authorised_form = True
                name_entry.display_date = identity.display_date
                name_entry.language = self.language
                name_entry.script = self.script
                name_entry.save()

            if name_5:
                identity = Identity(entity=entity)
                identity.display_date = date_5
                identity.preferred_identity = False
                identity.save()

                name_entry = NameEntry(identity=identity)
                name_entry.display_name = name_5
                name_entry.authorised_form = True
                name_entry.display_date = identity.display_date
                name_entry.language = self.language
                name_entry.script = self.script
                name_entry.save()

            # Create Control
            control = Control()
            control.entity = entity
            control.maintenance_status = self.maintenance_status
            control.publication_status = self.publication_status
            control.language = self.language
            control.script = self.script
            control.save()

            # Create Sources!
            if viaf:
                for v in viaf.split('QQQQQ'):
                    source = Source()
                    source.control = control
                    source.name = 'VIAF Link'
                    source.url = v
                    source.save()

    def _obj_or_none(self, row, key):
        if pd.isnull(row[key]):
            return None
        else:
            return row[key]

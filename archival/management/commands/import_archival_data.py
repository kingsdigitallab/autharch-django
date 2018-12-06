import logging

import pandas as pd
from archival.models import Collection, File, Item, Reference, Series
from authority.models import Entity
from django.core.management.base import BaseCommand, CommandError
from jargon.models import (Publication, PublicationStatus, ReferenceSource,
                           Repository)
from languages_plus.models import Language
from script_codes.models import Script


class Command(BaseCommand):
    args = '<spreadsheet_path>'
    help = 'Imports archival data from a spreadsheet or csv file'
    logger = logging.getLogger(__name__)

    language = Language.objects.get(name_en='English')
    script = Script.objects.get(name='Latin')

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

        df['Date of Description'] = pd.to_datetime(df['Date of Description'])

        for i, row in df.iterrows():
            self._import_row(row)

    def _import_row(self, row):
        uuid = row['ID']
        level = row['Level'].lower()

        if level in ['collection', 'fonds']:
            col = self._create_or_get_object(Collection, uuid)
            col = self._add_base_collection_data(col, row)
            col = self._add_collection_data(col, row)
            col.save()
        elif level == 'series':
            series = self._create_or_get_object(Series, uuid)
            series = self._add_base_collection_data(series, row)
            series = self._add_base_series_data(series, row)
            series = self._add_series_data(series, row)
            series.save()
        elif 'file' in level:
            f = self._create_or_get_object(File, uuid)
            f = self._add_base_collection_data(f, row)
            f = self._add_base_series_data(f, row)
            f = self._add_base_file_data(f, row)
            f = self._add_file_data(f, row)
            f.save()
        elif level == 'item':
            item = self._create_or_get_object(Item, uuid)
            item = self._add_base_collection_data(item, row)
            item = self._add_base_series_data(item, row)
            item = self._add_base_file_data(item, row)
            item = self._add_item_data(item, row)
            item.save()

    def _create_or_get_object(self, model, uuid):
        try:
            obj = model.objects.get(uuid=uuid)
            self.logger.info('Found existing {} with uuid: {}'.format(
                model, uuid))

            return obj
        except model.DoesNotExist:
            self.logger.warning('{} not found for uuid: {}. Creating.'.format(
                model, uuid))
            obj = model(uuid=uuid)

            return obj

    def _add_base_collection_data(self, obj, row):
        repository, created = Repository.objects.get_or_create(
            code=row['Repository Code'], title=row['Repository'])
        self.logger.debug(
            'Repository {} was created? {}'.format(repository, created))
        obj.repository = repository

        obj.title = row['Title']
        # obj.provenance
        obj.creation_dates = row['Date']

        if not pd.isnull(row['Description']):
            obj.description = row['Description']

        if not pd.isnull(row['Notes']):
            obj.notes = row['Notes']

        obj.extent = row['Extent']

        if not pd.isnull(row['RA_Related Materials']):
            obj.related_materials = row['RA_Related Materials']

        obj.cataloguer = row['Cataloguer']
        obj.description_date = row['Date of Description']

        ps, _ = PublicationStatus.objects.get_or_create(
            title=row['Publication Status'])
        obj.publication_status = ps

        obj.save()

        source, _ = ReferenceSource.objects.get_or_create(title='RA')
        ref, _ = Reference.objects.get_or_create(
            source=source, unitid=row['RA_Reference'])
        obj.references.add(ref)

        source, _ = ReferenceSource.objects.get_or_create(title='CALM')
        ref, _ = Reference.objects.get_or_create(
            source=source, unitid=row['CALM_reference'])
        obj.references.add(ref)

        if not pd.isnull(row['Language']):
            try:
                language = Language.objects.get(name_en=row['Language'])
                obj.languages.add(language)
            except Language.DoesNotExist:
                self.logger.warning('Language {} not found'.format(
                    row['Language']))

        return obj

    def _add_collection_data(self, col, row):
        if not pd.isnull(row['Admin History']):
            col.administrative_history = row['Admin History']

        if not pd.isnull(row['Arrangement']):
            col.arrangement = row['Arrangement']

        return col

    def _add_base_series_data(self, obj, row):
        if not pd.isnull(row['Publications']):
            publication, _ = Publication.objects.get_or_create(
                title=row['Publications'])
            obj.publications.add(publication)

        return obj

    def _add_series_data(self, obj, row):
        if not pd.isnull(row['Arrangement']):
            obj.arrangement = row['Arrangement']

        reference = self._get_parent_reference(row)
        if not reference:
            return obj

        series = Series.objects.filter(references=reference)
        if series:
            obj.parent = series[0]
            return obj

        collections = Collection.objects.filter(references=reference)
        if collections:
            obj.collection = collections[0]

        return obj

    def _get_parent_reference(self, row):
        source = ReferenceSource.objects.get(title='CALM')
        unitid = '/'.join(row['CALM_reference'].split('/')[:-1])

        try:
            reference = Reference.objects.get(source=source, unitid=unitid)
            self.logger.debug('Found reference: {}: {}'.format(source, unitid))
            return reference
        except Reference.DoesNotExist:
            self.logger.debug('Reference {}: {} not found'.format(
                source, unitid))
            return None

    def _add_base_file_data(self, obj, row):
        if not pd.isnull(row['Physical Description']):
            obj.physical_description = row['Physical Description']

        if not pd.isnull(row['Withheld']):
            obj.withheld = row['Withheld']

        return obj

    def _add_file_data(self, f, row):
        if not pd.isnull(row['Writer']):
            entity = self._get_entity_by_name(row['Writer'])
            if entity:
                f.creators.add(entity)

        if not pd.isnull(row['Addressee']):
            entity = self._get_entity_by_name(row['Addressee'])
            if entity:
                f.persons_as_relations.add(entity)

        reference = self._get_parent_reference(row)
        if not reference:
            return f

        files = File.objects.filter(references=reference)
        if files:
            f.parent = files[0]
            return f

        series = Series.objects.filter(references=reference)
        if series:
            f.series = series[0]

        return f

    def _get_entity_by_name(self, name):
        if not name:
            return None

        entity, _ = Entity.get_or_create_by_display_name(
            name, self.language, self.script)

        return entity

    def _add_item_data(self, obj, row):
        if not pd.isnull(row['Writer']):
            entity = self._get_entity_by_name(row['Writer'])
            if entity:
                obj.creators.add(entity)

        if not pd.isnull(row['Addressee']):
            entity = self._get_entity_by_name(row['Addressee'])
            if entity:
                obj.persons_as_relations.add(entity)

        reference = self._get_parent_reference(row)
        if not reference:
            return obj

        files = File.objects.filter(references=reference)
        if files:
            obj.f = files[0]
            return obj

        series = Series.objects.filter(references=reference)
        if series:
            obj.series = series[0]

        return obj

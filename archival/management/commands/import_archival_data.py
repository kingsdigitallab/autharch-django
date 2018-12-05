import logging

import pandas as pd
from archival.models import Collection, Reference, Series
from django.core.management.base import BaseCommand
from jargon.models import (Publication, PublicationStatus, ReferenceSource,
                           Repository)
from languages_plus.models import Language


class Command(BaseCommand):
    args = '<spreadsheet_path>'
    help = 'Imports archival data from a spreadsheet'
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_path', nargs=1, type=str)

    def handle(self, *args, **options):
        df = pd.read_excel(options['spreadsheet_path'][0])
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

    def _add_series_data(self, series, row):
        source = ReferenceSource.objects.get(title='CALM')
        unitid = '/'.join(row['CALM_reference'].split('/')[:-1])

        try:
            reference = Reference.objects.get(source=source, unitid=unitid)
            self.logger.debug('Found reference: {}: {}'.format(source, unitid))
        except Reference.DoesNotExist:
            self.logger.debug('Reference {}: {} not found'.format(
                source, unitid))
            return series

        collections = Collection.objects.filter(references=reference)
        if collections:
            series.collection = collections[0]

        if not pd.isnull(row['Arrangement']):
            series.arrangement = row['Arrangement']

        return series

import logging
import os.path

import pandas as pd

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from archival.models import Collection, File, Item, Reference, Series
from authority.models import Entity
from jargon.models import (
    MaintenanceStatus, Publication, PublicationStatus, ReferenceSource,
    Repository)
from languages_plus.models import Language
from script_codes.models import Script


# Parser help.
HELP = ('Import archival data from spreadsheet or CSV files. Creates initial '
        'revisions on successful import.')
PATHS_HELP = 'Path to spreadsheet/CSV file to import.'

# Default values for missing data.
DEFAULT_PUBLICATION_STATUS = 'published'
DEFAULT_REPOSITORY_CODE = 262

NON_ESSENTIAL_COLUMNS = (
    'Admin History', 'Arrangement', 'Cataloguer', 'Date',
    'Description', 'Extent', 'Notes', 'Title')

# Error and log messages.
INVALID_INPUT_FILE_TYPE_MSG = (
    'Invalid file type for "{}"; please provide a .csv or .xlsx file.')
MISSING_OPTIONAL_COL_MSG = (
    'Data at "{}" does not include the optional "{}" column.')
MISSING_REQUIRED_COL_MSG = (
    'Data at "{}" does not include the required "{}" column.')
NO_PUBLICATION_CODE_COL_MSG = (
    'Data at "{}" does not include a "Publication Status" column; using '
    'default value of "%s" for all rows.' % DEFAULT_PUBLICATION_STATUS)
NO_REPOSITORY_CODE_COL_MSG = (
    'Data at "{}" does not include a "Repository Code" column; using default '
    'value of "%s" for Royal Archives and Royal Library repositories.'
    % DEFAULT_REPOSITORY_CODE)
NO_REPOSITORY_CODE_MSG = (
    'Data at "{}" has no "Repository Code" column and specifies an archive '
    'other than "Royal Archives" or "Royal Library.')


class Command(BaseCommand):

    help = HELP
    logger = logging.getLogger(__name__)

    language = Language.objects.filter(name_en='English').first()
    script = Script.objects.get(name='Latin')

    def add_arguments(self, parser):
        parser.add_argument('paths', help=PATHS_HELP, metavar='FILE',
                            nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        paths = options['paths']
        for path in paths:
            self._import_path(os.path.abspath(path))
        management.call_command('createinitialrevisions')

    def _import_path(self, path):
        if path.endswith('.csv'):
            df = pd.read_csv(path)
        elif path.endswith('.xlsx'):
            df = pd.read_excel(path)
        else:
            raise CommandError(INVALID_INPUT_FILE_TYPE_MSG.format(path))

        self._path = path
        df = self._tidy_df(df)

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
            self.logger.debug(f.creators.all())
            self.logger.debug(f.persons_as_relations.all())
            f.save()
        elif level == 'item':
            item = self._create_or_get_object(Item, uuid)
            item = self._add_base_collection_data(item, row)
            item = self._add_base_series_data(item, row)
            item = self._add_base_file_data(item, row)
            item = self._add_item_data(item, row)
            self.logger.debug(item.creators.all())
            self.logger.debug(item.persons_as_relations.all())
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
        repository_name = row['Repository']
        if 'Repository Code' in row:
            repository_code = row['Repository Code']
        elif repository_name in ('Royal Archives', 'Royal Library'):
            repository_code = DEFAULT_REPOSITORY_CODE
        else:
            raise CommandError(NO_REPOSITORY_CODE_MSG)
        repository, created = Repository.objects.get_or_create(
            code=repository_code, title=repository_name)
        self.logger.debug(
            'Repository {} was created? {}'.format(repository, created))
        obj.repository = repository

        obj = self._set_field_from_cell_data(obj, 'title', row, 'Title')
        obj = self._set_field_from_cell_data(obj, 'creation_dates', row,
                                             'Date')
        obj = self._set_field_from_cell_data(obj, 'description', row,
                                             'Description')
        obj = self._set_field_from_cell_data(obj, 'notes', row, 'Notes')
        obj = self._set_field_from_cell_data(obj, 'extent', row, 'Extent')
        obj = self._set_field_from_cell_data(obj, 'related_materials', row,
                                             'RA_Related Materials')
        obj = self._set_field_from_cell_data(obj, 'cataloguer', row,
                                             'Cataloguer')
        obj = self._set_field_from_cell_data(obj, 'description_date', row,
                                             'Date of Description')

        # Use a default publication status if none is supplied.
        publication_status = DEFAULT_PUBLICATION_STATUS
        if 'Publication Status' in row:
            publication_status = row['Publication Status']
        ps, _ = PublicationStatus.objects.get_or_create(
            title=publication_status)
        obj.publication_status = ps

        ms, _ = MaintenanceStatus.objects.get_or_create(title='new')
        obj.maintenance_status = ms

        obj.language = self.language
        obj.script = self.script

        obj.save()

        if 'RA_Reference' in row:
            source, _ = ReferenceSource.objects.get_or_create(title='RA')
            ref, _ = Reference.objects.get_or_create(
                source=source, unitid=row['RA_Reference'])
            obj.references.add(ref)

        if 'CALM_reference' in row:
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
        col = self._set_field_from_cell_data(col, 'administrative_history',
                                             row, 'Admin History')
        col = self._set_field_from_cell_data(col, 'arrangement', row,
                                             'Arrangement')
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
        self.logger.debug('reference {}'.format(reference))
        if not reference:
            return obj

        series = Series.objects.filter(references=reference)
        if series:
            obj.parent_series = series[0]
            return obj

        collections = Collection.objects.filter(references=reference)
        if collections:
            obj.parent_collection = collections[0]

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
        obj = self._set_field_from_cell_data(obj, 'physical_description', row,
                                             'Physical Description')
        obj = self._set_field_from_cell_data(obj, 'withheld', row, 'Withheld')
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
            f.parent_file = files[0]
            return f

        series = Series.objects.filter(references=reference)
        if series:
            f.parent_series = series[0]

        return f

    def _get_entity_by_name(self, name):
        if not name:
            return None

        if '[' in name:
            name = name.replace('[', '')

        if ']' in name:
            name = name.replace(']', '')

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
            obj.parent_series = series[0]

        return obj

    def _set_field_from_cell_data(self, obj, field, row, column):
        value = row.get(column)
        if not pd.isnull(value):
            setattr(obj, field, value)
        return obj

    def _tidy_df(self, df):
        """The archival records data exists in multiple Excel
        spreadsheets. These are inconsistent with each in regards to
        which columns are present and the names used for columns that
        hold the same sort of data.

        Make an attempt to sort out any problems here, raising a
        CommandError on a problem that cannot be worked around, and
        logging a warning otherwise.

        """
        # Essential columns (error if not present).

        if 'ID' not in df.columns:
            # Yes, there is a fallback. Yes, it has two spaces in it.
            if 'Serial  No.' in df.columns:
                df.rename(columns={'Serial  No.': 'ID'}, inplace=True)
            else:
                raise CommandError(
                    MISSING_REQUIRED_COL_MSG.format(self._path, 'ID'))

        if 'Date of Description' in df.columns:
            df['Date of Description'] = pd.to_datetime(
                df['Date of Description'])
        else:
            raise CommandError(MISSING_REQUIRED_COL_MSG.format(
                self._path, 'Date of Description'))

        # Non-essential columns (warning if not present).

        if 'RA_Reference' not in df.columns:
            if 'RA Reference' in df.columns:
                df.rename(columns={'RA Reference': 'RA_Reference'},
                          inplace=True)
            else:
                self.logger.warning(MISSING_OPTIONAL_COL_MSG.format(
                    self._path, 'RA_Reference'))

        if 'Publication Status' not in df.columns:
            self.logger.warning(NO_PUBLICATION_CODE_COL_MSG.format(self._path))
        if 'Repository Code' not in df.columns:
            self.logger.warning(NO_REPOSITORY_CODE_COL_MSG.format(self._path))

        for column in NON_ESSENTIAL_COLUMNS:
            if column not in df.columns:
                self.logger.warning(MISSING_OPTIONAL_COL_MSG.format(
                    self._path, column))

        return df

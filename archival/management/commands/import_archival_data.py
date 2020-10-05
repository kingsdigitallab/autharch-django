"""Import archival records from supplied spreadsheets.

Due to needing to capture relationships between the data (Collection
holds Series holds File holds Item), and uncertain ordering and
location of related data, the import operates in two phases: the first
to create the objects with their individual data, the second to add in
the relationships between them.

The CALM Reference defines the hierarchy, with parts separated by "/";
eg, DEBUDE/1/1 is the first File or Item in the first Series of the
DEBUDE Collection.

"""

import logging
import os.path
import re

import pandas as pd

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from controlled_vocabulary.utils import search_term_or_none
from jargon.models import (
    MaintenanceStatus, PublicationStatus, ReferenceSource, Repository)
from script_codes.models import Script

from archival.models import (
    ArchivalRecord, Collection, File, Item, Project, Reference, Series)
from authority.models import Entity


# Parser help.
HELP = ('Import archival data from spreadsheet or CSV files. Creates initial '
        'revisions on successful import.')
PATHS_HELP = 'Path to spreadsheet/CSV file to import.'
PROJECT_ID_HELP = 'ID of project the imported data is to be associated with.'

# Default values for missing data.
DEFAULT_PUBLICATION_STATUS = 'published'
DEFAULT_REPOSITORY_CODE = 262

NON_ESSENTIAL_COLUMNS = {
    'Admin History': None,
    'Addressee': None,
    'Arrangement': None,
    'Date': None,
    'Description': None,
    'Extent': None,
    'Notes': None,
    'Publication Status': DEFAULT_PUBLICATION_STATUS,
    'Publications': None,
    'RA_Reference': None,
    'Title': None,
    'Writer': None,
}

# Error and log messages.
COLLECTION_CALM_REFERENCE_HAS_SLASH = (
    'Collection record in data at "{}" (sheet "{}") has CALM reference "{}" '
    'containing a slash; check for hierarchy violation.')
EXISTING_CALM_REF = (
    'DUPLICATE CALM REF: '
    'Record "{}" with CALM Reference "{}" from data at "{}" (sheet "{}") '
    'already exists from record "{}" at "{}" (sheet "{}")')
EXISTING_RA_REF = (
    'DUPLICATE RA REF: '
    'Record "{}" with RA Ref "{}" from data at "{}" (sheet "{}") already '
    'exists from record "{}" at "{}" (sheet "{}")')
EXISTING_RECORD_DIFFERENT_MODEL_MSG = (
    'Existing record with UUID "{}" is "{}"; wanted to create "{}" from data '
    'at "{}" (sheet "{}").')
EXISTING_RECORD_IN_DIFFERENT_PROJECT_MSG = (
    'Record with UUID "{}" in data at "{}" (sheet "{}") already exists under '
    'different project "{}".')
EXISTING_RECORD_MSG = (
    'DUPLICATE ID: '
    'Record with UUID "{}" (RA Ref "{}"; CALM Ref "{}") in data at "{}" '
    '(sheet "{}") already exists from record "{}" at "{}" (sheet "{}").')
HIERARCHY_MISMATCH_MSG = (
    'Hierarchy mismatch: {} record ("{}") with reference to {} ("{}") in data '
    'at "{}" (sheet "{}").')
INVALID_INPUT_FILE_TYPE_MSG = (
    'Invalid file type for "{}"; please provide a .csv or .xlsx file.')
INVALID_LEVEL_MSG = ('Invalid level "{}" in data at "{}" (sheet "{}").')
LANGUAGE_NOT_FOUND_MSG = (
    'Language "{}" not found in record in data at "{}" (sheet "{}").')
MISSING_ID_FOR_RECORD = (
    'MISSING ID: '
    'Record "{}" has no ID value in data at "{}" (sheet "{}"); skipping.')
MISSING_OPTIONAL_COL_MSG = (
    'Data at "{}" (sheet "{}") does not include the optional "{}" column.')
MISSING_OPTIONAL_COL_WITH_DEFAULT_MSG = (
    'Data at "{}" (sheet "{}") does not include the optional "{}" column; '
    'using default value of "{}" for all rows.')
MISSING_PARENT_RECORD = (
    'MISSING PARENT: '
    'Record "{}" from data at "{}" (sheet "{}") has reference to parent '
    'record "{}" that does not exist.')
MISSING_PARENT_REFERENCE = (
    'MISSING PARENT: '
    'Parent CALM Reference "{}" does not exist; child reference is "{}" from '
    'record "{}" at "{}" (sheet "{}").')
MISSING_REQUIRED_COL_MSG = (
    'Data at "{}" (sheet "{}") does not include the required "{}" column.')
MULTIPLE_PARENT_RECORDS = (
    'Record "{}" from data at "{}" (sheet "{}") has reference to parent '
    'record "{}" that matches multiple records.')
NO_CALM_REF = (
    'MISSING CALM Reference: '
    'Record with UUID "{}" in data at "{}" (sheet "{}") has no CALM Ref.')
NO_RA_REF = (
    'MISSING RA Reference'
    'Record with UUID "{}" in data at "{}" (sheet "{}") has no RA Ref.')
NO_REPOSITORY_CODE_COL_MSG = (
    'Data at "{}" (sheet "{}") does not include a "Repository Code" column; '
    'using default value of "%s" for Royal Archives and Royal Library '
    'repositories.' % DEFAULT_REPOSITORY_CODE)
NO_REPOSITORY_CODE_MSG = (
    'Data at "{}" has no "Repository Code" column and specifies an archive '
    'other than "Royal Archives" or "Royal Library.')
NON_EXISTENT_PROJECT_MSG = 'Project with ID "{}" does not exist.'
UPDATE_SEARCH_INDEX_MSG = (
    'Note that the search index has not been updated to incorpoate any new '
    'data imported. Run ./manage.py rebuild_index when appropriate.')
USING_PROJECT_MSG = 'Importing records into project "{}".'


class Command(BaseCommand):

    help = HELP
    logger = logging.getLogger(__name__)

    language = search_term_or_none('iso639-2', 'eng', exact=True)
    script = Script.objects.get(name='Latin')
    normalise_space = re.compile(r'\s+').sub

    def add_arguments(self, parser):
        parser.add_argument('project_id', help=PROJECT_ID_HELP, type=int)
        parser.add_argument('paths', help=PATHS_HELP, metavar='FILE',
                            nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            project = Project.objects.get(pk=options['project_id'])
        except Project.DoesNotExist:
            raise CommandError(NON_EXISTENT_PROJECT_MSG.format(
                options['project_id']))
        self.logger.info(USING_PROJECT_MSG.format(project.title))
        self._records = {}
        self._uuids = {}
        self._calm_refs = {}
        self._ra_refs = {}
        paths = options['paths']
        for path in paths:
            self._import_path(os.path.abspath(path), project)
        for record, location_data in self._records.items():
            self._path, self._sheet = location_data
            self._import_relationships(record)
        management.call_command('createinitialrevisions')
        self.stdout.write(UPDATE_SEARCH_INDEX_MSG)

    def _import_path(self, path, project):
        self._path = path
        if path.endswith('.csv'):
            self._sheet = None
            df = pd.read_csv(path)
            self._import_sheet(df, project)
        elif path.endswith('.xlsx'):
            for sheet, df in pd.read_excel(path, sheet_name=None).items():
                self._import_sheet(df, project, sheet)
        else:
            raise CommandError(INVALID_INPUT_FILE_TYPE_MSG.format(path))

    def _import_sheet(self, df, project, sheet):
        self._sheet = sheet
        df = self._tidy_df(df)
        for i, row in df.iterrows():
            record = self._import_row(row, project)
            if record is not None:
                self._records[record] = [self._path, self._sheet]

    def _import_row(self, row, project):
        uuid = row['ID']
        if pd.isnull(uuid):
            self.logger.warning(MISSING_ID_FOR_RECORD.format(
                row.get('Title', '[no title]'), self._path, self._sheet))
            return

        level = row['Level'].lower()
        if level in ['collection', 'fonds']:
            record = self._create_object(Collection, uuid, project, row)
            if record is not None:
                record = self._add_base_collection_data(record, row)
                record = self._add_collection_data(record, row)
                record.save()
        elif level.endswith('series'):
            record = self._create_object(Series, uuid, project, row)
            if record is not None:
                record = self._add_base_collection_data(record, row)
                record = self._add_base_series_data(record, row)
                record = self._add_series_data(record, row)
                record.save()
        elif 'file' in level:
            record = self._create_object(File, uuid, project, row)
            if record is not None:
                record = self._add_base_collection_data(record, row)
                record = self._add_base_series_data(record, row)
                record = self._add_base_file_data(record, row)
                record = self._add_file_data(record, row, project)
                self.logger.debug(record.creators.all())
                self.logger.debug(record.persons_as_relations.all())
                record.save()
        elif level == 'item':
            record = self._create_object(Item, uuid, project, row)
            if record is not None:
                record = self._add_base_collection_data(record, row)
                record = self._add_base_series_data(record, row)
                record = self._add_base_file_data(record, row)
                record = self._add_item_data(record, row, project)
                self.logger.debug(record.creators.all())
                self.logger.debug(record.persons_as_relations.all())
                record.save()
        else:
            raise CommandError(INVALID_LEVEL_MSG.format(
                level, self._path, self._sheet))
        return record

    def _import_relationships(self, record):
        calm_reference = record.calm_reference
        if '/' in calm_reference:
            if isinstance(record, Collection):
                self.logger.warning(COLLECTION_CALM_REFERENCE_HAS_SLASH.format(
                    self._path, self._sheet, calm_reference))
                return
            parent_reference = self._get_parent_reference(calm_reference,
                                                          record.uuid)
            if parent_reference is None:
                return
            try:
                parent = ArchivalRecord.objects.get(
                    calm_reference=parent_reference)
            except ArchivalRecord.DoesNotExist:
                self.logger.warning(MISSING_PARENT_RECORD.format(
                    calm_reference, self._path, self._sheet, parent_reference))
                return
            except ArchivalRecord.MultipleObjectsReturned:
                self.logger.warning(MULTIPLE_PARENT_RECORDS.format(
                    calm_reference, self._path, self._sheet, parent_reference))
                return
            if isinstance(parent, Collection):
                record.parent_collection = parent
            elif isinstance(parent, Series):
                record.parent_series = parent
            elif isinstance(parent, File):
                if isinstance(record, Series):
                    raise CommandError(HIERARCHY_MISMATCH_MSG.format(
                        'Series', calm_reference, 'File',
                        parent_reference.unitid, self._path, self._sheet))
                else:
                    record.parent_file = parent
            else:
                raise CommandError(HIERARCHY_MISMATCH_MSG.format(
                    'A', calm_reference, 'Item', parent_reference.unitid,
                    self._path, self._sheet))
            record.save()

    def _create_object(self, model, uuid, project, row):
        """Create and return a `model` object in `project` with `uuid`.

        Returns None if a record with `uuid` already exists."""
        try:
            obj = ArchivalRecord.objects.get(uuid=uuid)
            calm_ref = row.get('CALM_reference', 'None')
            ra_ref = row.get('RA_Reference', 'None')
            self.logger.warning(EXISTING_RECORD_MSG.format(
                uuid, ra_ref, calm_ref, self._path, self._sheet,
                *self._uuids.get(uuid, ['', 'not from current import', ''])))
            existing_model = obj.get_real_instance_class()
            if existing_model != model:
                self.logger.warning(
                    EXISTING_RECORD_DIFFERENT_MODEL_MSG.format(
                        uuid, existing_model._meta.model_name,
                        model._meta.model_name, self._path, self._sheet))
            if obj.project is None:
                pass
            elif obj.project.id != project.id:
                raise CommandError(
                    EXISTING_RECORD_IN_DIFFERENT_PROJECT_MSG.format(
                        uuid, self._path, self._sheet, obj.project.title))
            return None
        except ArchivalRecord.DoesNotExist:
            self.logger.debug('{} not found for uuid: {}. Creating.'.format(
                model, uuid))
            obj = model(uuid=uuid, project=project)
            self._uuids[uuid] = [row.get('Title', '[no title]'), self._path,
                                 self._sheet]
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
        obj = self._set_creation_date_range(obj, row)
        obj = self._set_field_from_cell_data(obj, 'description', row,
                                             'Description')
        obj = self._set_field_from_cell_data(obj, 'notes', row, 'Notes')
        obj = self._set_field_from_cell_data(obj, 'extent', row, 'Extent')

        # Use a default publication status if none is supplied.
        publication_status = DEFAULT_PUBLICATION_STATUS
        if 'Publication Status' in row:
            publication_status = row['Publication Status']
        ps = PublicationStatus.objects.get(title=publication_status)
        obj.publication_status = ps

        ms = MaintenanceStatus.objects.get(title='new')
        obj.maintenance_status = ms

        obj.language = self.language
        obj.script = self.script

        obj.save()

        title = row.get('Title', '[no title]')
        if 'RA_Reference' in row:
            ra_ref = row['RA_Reference']
            source = ReferenceSource.objects.get(title='RA')
            try:
                ref = Reference.objects.get(source=source, unitid=ra_ref)
                self.logger.info(EXISTING_RA_REF.format(
                    title, ra_ref, self._path, self._sheet, *self._ra_refs.get(
                        ra_ref, ['', 'not from current import', ''])))
            except Reference.DoesNotExist:
                ref = Reference(source=source, unitid=ra_ref)
                ref.save()
                self._ra_refs[ra_ref] = [title, self._path, self._sheet]
            obj.references.add(ref)
        else:
            self.logger.warning(NO_RA_REF.format(obj.uuid, self._path,
                                                 self._sheet))

        if 'CALM_reference' in row:
            calm_ref = row['CALM_reference']
            try:
                ArchivalRecord.objects.get(calm_reference=calm_ref)
                raise CommandError(EXISTING_CALM_REF.format(
                    title, calm_ref, self._path, self._sheet,
                    *self._calm_refs.get(
                        calm_ref, ['', 'not from current import', ''])))
            except ArchivalRecord.DoesNotExist:
                obj.calm_reference = calm_ref
                self._calm_refs[calm_ref] = [title, self._path, self._sheet]
            obj.references.add(ref)
        else:
            self.logger.warning(NO_CALM_REF.format(obj.uuid, self._path,
                                                   self._sheet))

        if not pd.isnull(row['Language']):
            languages = []
            for lang_string in row['Language'].split('\n'):
                if ', ' in lang_string:
                    languages.extend(lang_string.split(', '))
                else:
                    languages.append(lang_string)
            for lang in languages:
                if lang == 'Greek':
                    lang = 'Greek, Modern (1453-)'
                language = search_term_or_none('iso639-2', lang, exact=True)
                if language is None:
                    self.logger.warning(LANGUAGE_NOT_FOUND_MSG.format(
                        lang, self._path, self._sheet))
                else:
                    obj.languages.add(language)

        return obj

    def _add_collection_data(self, col, row):
        col = self._set_field_from_cell_data(col, 'administrative_history',
                                             row, 'Admin History')
        col = self._set_field_from_cell_data(col, 'arrangement', row,
                                             'Arrangement')
        return col

    def _add_base_series_data(self, obj, row):
        obj = self._set_field_from_cell_data(obj, 'publications', row,
                                             'Publications')
        return obj

    def _add_series_data(self, obj, row):
        obj = self._set_field_from_cell_data(obj, 'arrangement', row,
                                             'Arrangement')
        return obj

    def _get_parent_reference(self, reference, uuid):
        unitid = '/'.join(reference.split('/')[:-1])
        try:
            record = ArchivalRecord.objects.get(calm_reference=unitid)
            self.logger.debug('Found reference: {}: {}'.format(record, unitid))
            return record.calm_reference
        except ArchivalRecord.DoesNotExist:
            self.logger.warning(MISSING_PARENT_REFERENCE.format(
                unitid, reference, *self._uuids[uuid]))

    def _add_base_file_data(self, obj, row):
        obj = self._set_field_from_cell_data(obj, 'physical_description', row,
                                             'Physical Description')
        obj = self._set_field_from_cell_data(obj, 'withheld', row, 'Withheld')
        return obj

    def _add_file_data(self, f, row, project):
        if not pd.isnull(row.get('Writer')):
            entities = self._get_entities_by_name(row['Writer'], project)
            if entities:
                f.creators.add(*entities)

        if not pd.isnull(row.get('Addressee')):
            entities = self._get_entities_by_name(row['Addressee'], project)
            if entities:
                f.persons_as_relations.add(*entities)

        return f

    def _get_entities_by_name(self, full_name, project):
        """Return a list of entities matching the names in `full_name` -
        either created or already existing.

        `full_name` may include multiple names separated with "|".

        """
        if full_name is None:
            return None
        full_name = full_name.replace('[', '')
        full_name = full_name.replace(']', '')
        full_name = self.normalise_space(' ', full_name)
        full_name = full_name.replace(';', '|')
        names = full_name.split('|')
        entities = []
        for name in names:
            name = name.strip()
            if not name:
                continue
            entity, _ = Entity.get_or_create_by_display_name(
                name, self.language, self.script, project)
            if entity is not None:
                entities.append(entity)
        return entities

    def _add_item_data(self, obj, row, project):
        if not pd.isnull(row.get('Writer')):
            entities = self._get_entities_by_name(row['Writer'], project)
            if entities:
                obj.creators.add(*entities)

        if not pd.isnull(row.get('Addressee')):
            entities = self._get_entities_by_name(row['Addressee'], project)
            if entities:
                obj.persons_as_relations.add(*entities)

        return obj

    def _join_iso_date(self, year, month, day):
        if month is None:
            return year
        if day is None:
            return '-'.join([year, month])
        return '-'.join([year, month, day])

    def _parse_date_day_month_year(self, date):
        full = r'^(?P<day>[0-3]?[0-9]) m(?P<month>[01][0-9]) (?P<year>\d{4})$'
        return re.match(full, date)

    def _parse_date_month_year(self, date):
        return re.match(r'^m(?P<month>[01][0-9]) (?P<year>\d{4})$', date)

    def _parse_date_to_iso(self, date, substitute_year=None,
                           substitute_month=None):
        date = self.normalise_space(' ', date).strip()
        months = {'January': 'm01', 'February': 'm02', 'March': 'm03',
                  'April': 'm04', 'May': 'm05', 'June': 'm06', 'July': 'm07',
                  'August': 'm08', 'September': 'm09', 'October': 'm10',
                  'November': 'm11', 'December': 'm12'}
        for month, number in months.items():
            date = date.replace(month, number)
        parts = date.split()
        if len(parts) == 1:
            # One part is either "year", "month" (with year supplied),
            # or "day" (with month and year supplied).
            if re.match(r'^\d{4}$', date):
                return (date, None, None)
            if substitute_year is not None and substitute_month is not None:
                match = self._parse_date_day_month_year('{} m{} {}'.format(
                    date, substitute_month, substitute_year))
                if match is not None:
                    return (match.group('year'), match.group('month'),
                            match.group('day').zfill(2))
            if substitute_year is not None:
                match = self._parse_date_month_year('{} {}'.format(
                    date, substitute_year))
                if match is not None:
                    return (match.group('year'), match.group('month'), None)
        elif len(parts) == 2:
            # Two parts are either "month year" or "day month" (with
            # year supplied).
            match = self._parse_date_month_year(date)
            if match is not None:
                return (match.group('year'), match.group('month'), None)
            if substitute_year is not None:
                match = self._parse_date_day_month_year('{} {}'.format(
                    date, substitute_year))
                if match is not None:
                    return (match.group('year'), match.group('month'),
                            match.group('day').zfill(2))
        elif len(parts) == 3:
            # Three parts are "day month year".
            match = self._parse_date_day_month_year(date)
            if match is not None:
                return (match.group('year'), match.group('month'),
                        match.group('day').zfill(2))
        raise ValueError

    def _set_creation_date_range(self, obj, row):
        date = row.get('Date')
        if pd.isnull(date):
            return obj
        date = str(date)
        unwanted_chars = ['?', '[', ']']
        for char in unwanted_chars:
            date = date.replace(char, '')
        dates = date.split('-')
        if len(dates) == 1:
            try:
                iso_date = self._parse_date_to_iso(dates[0])
            except ValueError:
                return obj
            obj.start_date = self._join_iso_date(*iso_date)
            obj.end_date = self._join_iso_date(*iso_date)
        elif len(dates) == 2:
            try:
                iso_end_date = self._parse_date_to_iso(dates[1])
            except ValueError:
                return obj
            try:
                iso_start_date = self._parse_date_to_iso(
                    dates[0], iso_end_date[0], iso_end_date[1])
            except ValueError:
                return obj
            obj.start_date = self._join_iso_date(*iso_start_date)
            obj.end_date = self._join_iso_date(*iso_end_date)
        return obj

    def _set_field_from_cell_data(self, obj, field, row, column, default=None):
        value = row.get(column) or default
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
            elif 'Serial Number' in df.columns:
                df.rename(columns={'Serial Number': 'ID'}, inplace=True)
            elif 'Serial No.' in df.columns:
                df.rename(columns={'Serial No.': 'ID'}, inplace=True)
            elif 'Id' in df.columns:
                df.rename(columns={'Id': 'ID'}, inplace=True)
            else:
                raise CommandError(MISSING_REQUIRED_COL_MSG.format(
                    self._path, self._sheet, 'ID'))

        if 'Repository' not in df.columns:
            if 'Respository' in df.columns:
                df.rename(columns={'Respository': 'Repository'}, inplace=True)

        if 'CALM_reference' not in df.columns:
            if 'CALM Reference' in df.columns:
                df.rename(columns={'CALM Reference': 'CALM_reference'},
                          inplace=True)
            elif 'Calm_Reference' in df.columns:
                df.rename(columns={'Calm_Reference': 'CALM_reference'},
                          inplace=True)
            else:
                raise CommandError(MISSING_REQUIRED_COL_MSG.format(
                    self._path, self._sheet, 'CALM_reference'))

        # Non-essential columns (warning if not present).

        if 'RA_Reference' not in df.columns:
            if 'RA Reference' in df.columns:
                df.rename(columns={'RA Reference': 'RA_Reference'},
                          inplace=True)

        if 'Repository Code' not in df.columns:
            self.logger.info(NO_REPOSITORY_CODE_COL_MSG.format(
                self._path, self._sheet))

        for column, default in NON_ESSENTIAL_COLUMNS.items():
            if column not in df.columns:
                if default is not None:
                    msg = MISSING_OPTIONAL_COL_WITH_DEFAULT_MSG.format(
                        self._path, self._sheet, column, default)
                else:
                    msg = MISSING_OPTIONAL_COL_MSG.format(
                        self._path, self._sheet, column)
                self.logger.info(msg)

        return df

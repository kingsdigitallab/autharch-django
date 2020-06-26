import json
import logging
import re

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geonames_place.models import Place as GeoPlace
from languages_plus.models import Language
from script_codes.models import Script

from archival.models import Project
from authority.models import (
    BiographyHistory, Control, Description, Entity, Function, Identity,
    LanguageScript, LocalDescription, NameEntry, Place, Relation, Source)
from jargon.models import (
    EntityRelationType, EntityType, Function as FunctionTerm, Gender,
    MaintenanceStatus, PublicationStatus)


HELP = 'Import entities from JSON (georgian API).'
PROJECT_ID_HELP = 'ID of project the imported data is to be associated with.'
PATHS_HELP = 'Path to JSON file containing entity data.'

MISSING_ENTITY_TYPE_MSG = 'Document "{}" has no entity type information.'
MISSING_FUNCTION_MSG = (
    'Document "{}" references function "{}" that does not exist.')
MISSING_LANGUAGE_ERROR = (
    'Document "{}" references language code "{}" that does not exist.')
MISSING_SCRIPT_ERROR = (
    'Document "{}" references script code "{}" that does not exist.')
MISSING_TERM_ERROR = 'Document "{}" references {} "{}" that does not exist.'
MULTIPLE_EXIST_DATES_MSG = (
    'Document "{}" has multiple existDates; we are not equipped to handle '
    'multiple identities as this requires.')
NO_PROJECT_MSG = 'Project with ID "{}" does not exist.'
PLACE_NOT_FOUND_ERROR = (
    'Document "{}" references place "{}" that does not return a result from '
    'a GeoNames lookup.')
UNKNOWN_LANGUAGE_SCRIPT_MSG = (
    'Document "{}" references language "{}" that cannot be parsed into a '
    'language and script.')
UPDATE_SEARCH_INDEX_MSG = (
    'Note that the search index has not been updated to incorpoate any new '
    'data imported. Run ./manage.py rebuild_index when appropriate.')

GEONAMES_BASE_URL = 'http://www.geonames.org/'
TERM_MAP = {
    'entity_type': EntityType,
    'gender': Gender,
    'maintenance_status': MaintenanceStatus,
    'publication_status': PublicationStatus,
    'relation_type': EntityRelationType,
}
TITLE_MAP = {
    ('gender', 'male'): 'Men',
    ('gender', 'women (wimmin, womyn)'): 'Women',
}
UKAT_BASE_URL = 'http://www.ukat.org.uk/thesaurus/concept/'


default_language = Language.objects.filter(name_en='English').first()
default_script = Script.objects.get(name='Latin')
extract_language_script = re.compile(
    r'(?P<language>[^(]+) \((?P<script>[^)]+)\)').fullmatch
normalise_space = re.compile(r'\s+').sub


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('project_id', help=PROJECT_ID_HELP, type=int)
        parser.add_argument('paths', help=PATHS_HELP, metavar='FILE',
                            nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            project = Project.objects.get(pk=options['project_id'])
        except Project.DoesNotExist:
            raise CommandError(NO_PROJECT_MSG.format(options['project_id']))
        entity_map = {}
        for path in options['paths']:
            entity_map[path] = self._import_entity(path, project)
        for path in options['paths']:
            entity_map[path].import_relations()
        management.call_command('createinitialrevisions')
        self.stdout.write(UPDATE_SEARCH_INDEX_MSG)

    def _import_entity(self, path, project):
        entity_import = EntityImport(path, project)
        try:
            entity_import.import_entity()
        except Exception as e:
            self.stderr.write(path)
            raise e
        return entity_import


class EntityImport:

    logger = logging.getLogger(__name__)

    def __init__(self, path, project):
        self._path = path
        self._project = project
        self._identity = None

    def import_entity(self):
        with open(self._path) as fh:
            data = json.load(fh)
        try:
            entity_type_data = data['eac:p.entityType'][0]
        except KeyError:
            raise CommandError(MISSING_ENTITY_TYPE_MSG.format(self._path))
        entity_type = self._get_jargon_term(
            'entity_type', entity_type_data)
        entity = Entity(project=self._project, entity_type=entity_type)
        entity.save()
        self._import_control(entity, data)
        for i, exist_date in enumerate(data['eac:p.existDates']):
            self._identity = self._import_identity(entity, exist_date, data)
            if i > 0:
                raise CommandError(MULTIPLE_EXIST_DATES_MSG.format(self._path))

    def import_relations(self):
        with open(self._path) as fh:
            data = json.load(fh)
        for index, relation_data in enumerate(
                data.get('eac:p.cpfRelation', [])):
            self._import_relation(self._identity, relation_data, data, index)

    def _get_jargon_term(self, term_type, data):
        model = TERM_MAP[term_type]
        title = data.get('@value') or data['o:label']
        real_title = TITLE_MAP.get((term_type, title), title)
        try:
            term = model.objects.get(title__iexact=real_title)
        except model.DoesNotExist:
            raise CommandError(MISSING_TERM_ERROR.format(
                self._path, term_type, title))
        return term

    def _get_language(self, lang_name):
        """Return the `Language` object corresponding to `lang_name`.

        :param lang_name: English name of the language
        :type lang_name: `str`
        :rtype: `Language`

        """
        try:
            language = Language.objects.get(name_en=lang_name)
        except Language.DoesNotExist:
            raise CommandError(MISSING_LANGUAGE_ERROR.format(
                self._path, lang_name))
        return language

    def _get_script(self, script_name):
        """Return the `Script` object corresponding to `script_name`.

        :param script_name: English name of the script
        :type script_name: `str`
        :rtype: `Script`

        """
        try:
            script = Script.objects.get(name=script_name)
        except Script.DoesNotExist:
            raise CommandError(MISSING_SCRIPT_ERROR.format(
                self._path, script_name))
        return script

    def _import_biog_hist(self, description, data):
        abstract = data['eac:p.abstract'][0]['@value']
        try:
            sources = data['eac:p.citation'][0]['@value']
        except KeyError:
            sources = ''
        copyright = '<p>{}</p>'.format(data['eac:p.p'][0]['@value'])
        biog_hist = BiographyHistory(
            description=description, abstract=abstract, sources=sources,
            copyright=copyright)
        biog_hist.save()

    def _import_control(self, entity, data):
        control = Control(entity=entity)
        control.maintenance_status = self._get_jargon_term(
            'maintenance_status', data['eac:p.maintenanceStatus'][0])
        control.publication_status = self._get_jargon_term(
            'publication_status', data['eac:p.publicationStatus'][0])
        control.language = default_language
        control.script = default_script
        control.save()
        for source_data in data.get('eac:p.source', []):
            self._import_source(control, source_data)

    def _import_date(self, holder, date_data):
        # Only set the display date; anything more requires
        # complicated parsing of a single string that might express a
        # date or a date range with circa, floruit, unknown elements,
        # etc.
        holder.display_date = date_data['@value']

    def _import_description(self, identity, data):
        description = Description(identity=identity)
        description.save()
        self._import_local_description(description, data)
        for language_data in data.get('eac:p.languageUsed', []):
            self._import_language_used(description, language_data)
        for index, place_data in enumerate(data.get('eac:p.placeEntry', [])):
            self._import_place(description, place_data, data, index)
        if data.get('eac:p.abstract'):
            self._import_biog_hist(description, data)
        for function_data in data.get('eac:p.function', []):
            self._import_function(description, function_data)

    def _import_function(self, description, function_data):
        uri = function_data.get('@id')
        if uri and uri.startswith(UKAT_BASE_URL):
            uri_id = '/' + uri[len(UKAT_BASE_URL):]
            try:
                function_obj = FunctionTerm.objects.get(uri__endswith=uri_id)
            except FunctionTerm.DoesNotExist:
                if uri_id.endswith('/'):
                    uri_id = uri_id[:-1]
                else:
                    uri_id = uri_id + '/'
                try:
                    function_obj = FunctionTerm.objects.get(
                        uri__endswith=uri_id)
                except FunctionTerm.DoesNotExist:
                    raise CommandError(MISSING_FUNCTION_MSG.format(
                        self._path, uri_id))
        else:
            title = function_data.get('o:label') or function_data['@value']
            try:
                function_obj = FunctionTerm.objects.get(
                    title__iexact=title.strip())
            except FunctionTerm.DoesNotExist:
                self.logger.warning(MISSING_FUNCTION_MSG.format(
                    self._path, title))
                return
        function = Function(description=description, title=function_obj)
        function.save()

    def _import_identity(self, entity, exist_date, data):
        identity = Identity(entity=entity, preferred_identity=True)
        self._import_date(identity, exist_date)
        identity.save()
        names = data['eac:p.nameEntry'] + \
            data.get('eac:p.nameEntryParallel', [])
        for index, name in enumerate(names):
            self._import_name_entry(identity, name, data, index)
        self._import_description(identity, data)
        return identity

    def _import_language_used(self, description, language_data):
        match = extract_language_script(
            normalise_space(' ', language_data['@value'].strip()))
        if match is None:
            raise CommandError(UNKNOWN_LANGUAGE_SCRIPT_MSG.format(
                self._path, language_data['@value']))
        language = self._get_language(match.group('language'))
        script = self._get_script(match.group('script'))
        language_script = LanguageScript(
            description=description, language=language, script=script)
        language_script.save()

    def _import_local_description(self, description, data):
        gender_data = data.get('eac:p.localDescription')
        if gender_data:
            gender = self._get_jargon_term('gender', gender_data[0])
            local_description = LocalDescription(description=description,
                                                 gender=gender)
            local_description.save()

    def _import_name_entry(self, identity, name, data, index):
        is_authorised = False
        if index == 0:
            is_authorised = True
        name_entry = NameEntry(
            identity=identity, language=default_language,
            script=default_script, authorised_form=is_authorised)
        name_entry.display_name = normalise_space(' ', name['@value'])
        try:
            date_data = data['eac:p.useDates'][index]
            self._import_date(name_entry, date_data)
        except (KeyError, IndexError):
            pass
        name_entry.save()

    def _import_place(self, description, place_data, data, index):
        place_id = place_data.get('@id', '')
        if place_id.startswith(GEONAMES_BASE_URL):
            place_id = place_id[len(GEONAMES_BASE_URL):]
            try:
                geo_place = GeoPlace.objects.get(geonames_id=place_id)
            except GeoPlace.DoesNotExist:
                geo_place = GeoPlace(geonames_id=place_id)
                geo_place.save()
        else:
            place_name = place_data.get('o:label', False) or \
                place_data['@value']
            geo_place = GeoPlace.get_or_create_from_geonames(place_name)
            if geo_place is None:
                self.logger.warning(PLACE_NOT_FOUND_ERROR.format(
                    self._path, place_name))
                return
        try:
            role = data['eac:p.placeRole'][index]['@value']
        except IndexError:
            role = ''
        place = Place(description=description, place=geo_place, role=role)
        place.save()

    def _import_relation(self, identity, relation_data, data, index):
        relation_detail = relation_data['@value']
        relation_type = self._get_jargon_term(
            'relation_type', data['eac:p.cpfRelationType'][index])
        name = normalise_space(' ', data['eac:p.relationEntry'][index][
            'display_title'])
        related_entity, created = Entity.get_or_create_by_display_name(
            name, default_language, default_script, self._project)
        relation = Relation(
            identity=identity, relation_type=relation_type,
            relation_detail=relation_detail, related_entity=related_entity)
        relation.save()

    def _import_source(self, control, source_data):
        name = source_data['o:label']
        url = source_data['@id']
        source = Source(control=control, name=name, url=url)
        source.save()

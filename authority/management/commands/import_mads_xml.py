import datetime
import os.path

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lxml import etree

from languages_plus.models import Language
from script_codes.models import Script

from archival.models import Project
from authority.models import Control, Entity, Identity, NameEntry, NamePart
from jargon.models import (
    EntityType, MaintenanceStatus, NamePartType, PublicationStatus)


HELP = 'Import person entities from MADS XML files.'
PROJECT_ID_HELP = 'ID of project the imported data is to be associated with.'
XML_PATHS_HELP = 'Path to MADS XML file.'

MADS_XSD_FILENAME = 'mads.xsd'

INVALID_XML_MSG = 'Document {} is not valid MADS: {}'
MISSING_PROJECT_MSG = 'Project with ID "{}" does not exist.'
MISSING_TERM_MSG = 'Document "{}" references {} "{}" that does not exist.'
NOT_WELL_FORMED_XML_MSG = 'Document "{}" is not well-formed XML: {}'
UPDATE_SEARCH_INDEX_MSG = (
    'Note that the search index has not been updated to incorpoate any new '
    'data imported. Run ./manage.py rebuild_index when appropriate.')

NS_MAP = {'m': 'http://www.loc.gov/mads/v2'}

NAME_PART_TYPE_MAP = {
    'family': 'surname',
    'given': 'forename',
    'termsOfAddress': 'proper title'
}
NAME_PARTS_ORDER = ['family', 'given', 'date', 'termsOfAddress']


def from_iso_format(date_str):
    try:
        year = int(date_str[:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
    except Exception:
        raise ValueError('Invalid ISO date: {}'.format(date_str))
    return [year, month, day]


PERSON_ENTITY_TYPE = EntityType.objects.get(title='person')
VALID_START_DATE = datetime.date(*from_iso_format('1714-01-01'))
VALID_END_DATE = datetime.date(*from_iso_format('1837-12-31'))


default_language = Language.objects.filter(name_en='English').first()
default_maintenance_status = MaintenanceStatus.objects.get(title='new')
default_publication_status = PublicationStatus.objects.get(title='inProcess')
default_script = Script.objects.get(name='Latin')


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('project_id', help=PROJECT_ID_HELP, type=int,
                            metavar='PROJECT_ID')
        parser.add_argument('xml_paths', help=XML_PATHS_HELP, nargs='+',
                            metavar='XML')

    @transaction.atomic
    def handle(self, *args, **options):
        project_id = options['project_id']
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise CommandError(MISSING_PROJECT_MSG.format(project_id))
        xsd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                MADS_XSD_FILENAME)
        xsd_doc = etree.parse(xsd_path)
        xsd = etree.XMLSchema(xsd_doc)
        for xml_path in options['xml_paths']:
            self._import_file(xml_path, project, xsd)
        management.call_command('createinitialrevisions')
        self.stdout.write(UPDATE_SEARCH_INDEX_MSG)

    def _assemble_display_name(self, name_parts):
        display_name = ''
        for part_type in NAME_PARTS_ORDER:
            name_part = name_parts.get(part_type)
            if not name_part:
                continue
            if not display_name:
                display_name = name_part
            else:
                display_name = display_name + ', ' + name_part
        return display_name

    def _collate_name_parts(self, name_part_els):
        name_parts = {}
        for name_part_el in name_part_els:
            part_type = name_part_el.get('type')
            name_parts.setdefault(part_type, []).append(name_part_el.text)
        for key, value in name_parts.items():
            name_parts[key] = ' '.join(value)
        return name_parts

    def _get_jargon_term(self, model, title):
        try:
            term = model.objects.get(title=title)
        except model.DoesNotExist:
            raise CommandError(MISSING_TERM_MSG.format(
                model._meta.model_name, title))
        return term

    def _import_control(self, entity):
        control = Control(
            entity=entity, maintenance_status=default_maintenance_status,
            publication_status=default_publication_status,
            language=default_language, script=default_script)
        control.save()

    def _import_entity(self, mads_el, project):
        if not self._is_valid_entity(mads_el):
            return
        entity = Entity(project=project, entity_type=PERSON_ENTITY_TYPE)
        entity.save()
        self._import_identity(entity, mads_el)
        self._import_control(entity)

    def _import_file(self, xml_path, project, xsd):
        tree = self._parse_xml(xml_path, xsd)
        self._xml_path = xml_path
        for mads_el in tree.xpath('/m:madsCollection/m:mads',
                                  namespaces=NS_MAP):
            self._import_entity(mads_el, project)

    def _import_identity(self, entity, mads_el):
        identity = Identity(entity=entity, preferred_identity=True)
        try:
            dob = mads_el.xpath('m:extension/m:dateOfBirth',
                                namespaces=NS_MAP)[0].text or ''
        except IndexError:
            dob = ''
        try:
            dod = mads_el.xpath('m:extension/m:dateOfDeath',
                                namespaces=NS_MAP)[0].text or ''
        except IndexError:
            dod = ''
        identity.date_from = dob
        identity.date_to = dod
        if dob and dod:
            identity.display_date = dob + ' - ' + dod
        elif dob:
            identity.display_date = dob + ' -'
        elif dod:
            identity.display_date = '- ' + dod
        else:
            identity.display_date = ''
        identity.save()
        name_el = mads_el.xpath('m:authority/m:name', namespaces=NS_MAP)[0]
        self._import_name(identity, name_el, is_authorised=True)
        if mads_el.xpath('m:variant[not(@otherType="firstNameUsed")]',
                         namespaces=NS_MAP):
            self.stderr.write(
                'Found variant that is not the useless firstNameUsed.')

    def _import_name(self, identity, name_el, is_authorised=False):
        # Since MADS name may have multiple namePart's with the same
        # type, create a dictionary with the parts of the same type
        # joined together.
        name_parts = self._collate_name_parts(name_el.xpath(
            'm:namePart', namespaces=NS_MAP))
        display_name = self._assemble_display_name(name_parts)
        # MADS has @xml:lang, @lang, and @script on name, with no
        # indication what the values of the latter two might be. Just
        # use our defaults.
        name_entry = NameEntry(
            identity=identity, display_name=display_name,
            authorised_form=is_authorised, language=default_language,
            script=default_script)
        name_entry.save()
        for part_type, part_value in name_parts.items():
            if part_type == 'date':
                name_entry.display_date = part_value
                pieces = part_value.split('-')
                if len(pieces) == 2:
                    name_entry.date_from = pieces[0]
                    name_entry.date_to = pieces[1]
            else:
                self._import_name_part(name_entry, part_type, part_value)
        name_entry.save()

    def _import_name_part(self, name_entry, part_type, part_value):
        name_part_type = self._get_jargon_term(NamePartType,
                                               NAME_PART_TYPE_MAP[part_type])
        name_part = NamePart(
            name_entry=name_entry, name_part_type=name_part_type,
            part=part_value)
        name_part.save()

    def _is_date_within_range(self, date_str):
        try:
            date = datetime.date(*from_iso_format(date_str))
        except ValueError:
            return False
        if date > VALID_START_DATE and date < VALID_END_DATE:
            return True
        return False

    def _is_valid_entity(self, mads_el):
        """Return True if entity represented in `mads_el` is a valid candidate
        for importing.

        Only entities that were born in our period, or died within our
        period, are suitable candidates for importing (anyone born
        before it who died after it is not human and therefore not a
        candidate).

        """
        is_valid = False
        try:
            dob = mads_el.xpath('m:extension/m:dateOfBirth',
                                namespaces=NS_MAP)[0].text
            if self._is_date_within_range(dob):
                is_valid = True
        except IndexError:
            pass
        if not is_valid:
            try:
                dod = mads_el.xpath('m:extension/m:dateOfDeath',
                                    namespaces=NS_MAP)[0].text
                if self._is_date_within_range(dod):
                    is_valid = True
            except IndexError:
                pass
        return is_valid

    def _parse_xml(self, xml_path, xsd):
        try:
            tree = etree.parse(xml_path)
        except etree.XMLSyntaxError as e:
            raise CommandError(NOT_WELL_FORMED_XML_MSG.format(
                xml_path, e))
        try:
            xsd.assertValid(tree)
        except etree.DocumentInvalid as e:
            raise CommandError(INVALID_XML_MSG.format(xml_path, e))
        return tree

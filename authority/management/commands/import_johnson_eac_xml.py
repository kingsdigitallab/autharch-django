"""Import EAC-CPF XML from the Dr Johnson corpus.

The EAC-CPF in use for this corpus uses different type values etc,
meaning that the existing import_eac_xml.py script cannot be used as
is. It isn't worth refactoring that script to pull out common code,
given that this import should in theory be done once. Let's see the
future laugh at this dumb decision.

"""

import logging
import os.path
import re

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lxml import etree

from controlled_vocabulary.utils import search_term_or_none
from geonames_place.models import Place as GeoPlace
from script_codes.models import Script

from archival.models import Project
from authority.models import (
    BiographyHistory, Control, Description, Entity, Event, Function, Identity,
    LanguageScript, LocalDescription, NameEntry, NamePart, Place, Relation,
    Source)
from jargon.models import (
    EntityRelationType, EntityType, Function as JFunction, Gender,
    MaintenanceStatus, NamePartType, PublicationStatus)


EAC_CPF_XSD_FILENAME = 'eac_cpf.xsd'

HELP = 'Imports the entity data in the specified Dr Johnson EAC XML file(s).'
PROJECT_ID_HELP = 'ID of project the imported data is to be associated with.'
XML_PATH_HELP = 'Path to EAC XML file.'

INVALID_XML_ERROR = 'Document {} is not valid EAC-CPF: {}'
MISSING_LANGUAGE_ERROR = ('Document "{}" references language code "{}" that '
                          'does not exist.')
MISSING_SCRIPT_ERROR = ('Document "{}" references script code "{}" that does '
                        'not exist.')
MISSING_TERM_ERROR = 'Document "{}" references {} "{}" that does not exist.'
MULTIPLE_RELATED_ENTITIES_FOUND_ERROR = (
    'Document "{}" references related entity with name "{}" that has '
    'multiple matches.')
NON_EXISTENT_PROJECT_ERROR = 'Project with ID "{}" does not exist.'
NOT_WELL_FORMED_XML_ERROR = 'Document "{}" is not well-formed XML: {}'
PLACE_NOT_FOUND_ERROR = ('Document "{}" references place "{}" that does not '
                         'return a result from a GeoNames lookup.')
RELATED_ENTITY_NOT_FOUND_ERROR = (
    'Document "{}" references related entity with name "{}" that does not '
    'exist.')
UNMAPPED_FUNCTION_ERROR = (
    'Entity {} from document "{}" uses unmapped Function term "{}".')
UPDATE_SEARCH_INDEX_MSG = (
    'Note that the search index has not been updated to incorpoate any new '
    'data imported. Run ./manage.py rebuild_index when appropriate.')

XLINK = '{http://www.w3.org/1999/xlink}'
XML = '{http://www.w3.org/XML/1998/namespace}'
NS_MAP = {'e': 'urn:isbn:1-931666-33-4'}
ENTITY_TYPE_XPATH = (
    '/e:eac-cpf/e:cpfDescription/e:identity[1]/e:entityType/text() |'
    '/e:eac-cpf/e:multipleIdentities/e:cpfDescription/e:identity[1]/'
    'e:entityType/text()'
)
GENDER_XPATH = 'e:term[1]/text()'
IDENTITY_XPATH = (
    '/e:eac-cpf/e:cpfDescription/e:identity | '
    '/e:eac-cpf/e:multipleIdentities/e:cpfDescription/e:identity'
)
LANGUAGE_CODE_XPATH = ('/e:eac-cpf/e:control/e:languageDeclaration/e:language/'
                       '@languageCode')
MAINTENANCE_STATUS_XPATH = '/e:eac-cpf/e:control/e:maintenanceStatus/text()'
NAME_PART_TYPE_XPATH = '@localType'
RELATION_TYPE_XPATH = '@cpfRelationType'
SCRIPT_CODE_XPATH = ('/e:eac-cpf/e:control/e:languageDeclaration/e:script/'
                     '@scriptCode')
SOURCE_XPATH = '/e:eac-cpf/e:control/e:sources/e:source'

FUNCTION_MAP = {
    'actors': 8852,
    'archivists': 848,
    'artists (visual artists)': 11712,
    'authors': 8606,
    'barristers': 14169,
    'biographers': 14202,
    'bishops (prelates)': 4638,
    'book clubs': 4400,
    'booksellers': 4175,
    'botanists': 9698,
    'brewers': 5884,
    'businessmen': 6187,
    'catalogers': 12496,
    'chemists (scientists)': 6278,
    'clergy': 548,
    'clergymen': 548,
    'clubs (associations)': 11467,
    'collectors': 5619,
    'commanders (commissioned officers)': 11600,
    'composers': 6557,
    'curates': 10530,
    'deacons': 12262,
    'deans (clergy)': 548,
    'editors': 10225,
    'financiers': 4068,
    'historians': 171,
    'indexers': 2725,
    'journalists': 5746,
    'judges': 4019,
    'kingdoms': 9029,
    'kings (people)': 10934,
    'lawyers': 14471,
    'librarians': 2725,
    'linguists': 8366,
    'members of Parliament': 9929,
    'members of parliament': 9929,
    'merchants': 14618,
    'military personnel': 11322,
    'milliners': 6686,
    'musicians': 500,
    'naturalists': 279,
    'novelists': 3782,
    'orators': 12567,
    'organists': 14733,
    'painters': 8842,
    'painters (artists)': 8842,
    'pets': 12523,
    'pharmacists': 6014,
    'philanthropists': 10062,
    'philosophers': 11858,
    'physicians': 10110,
    'playwrights': 11996,
    'poets': 1968,
    'politicians': 9579,
    'preachers': 6744,
    'printers': 266,
    'printers (persons)': 266,
    'producers (managers)': 13813,
    'professors (teachers)': 7949,
    'public officers': 1044,
    'publishers': 9127,
    'rectors': 5966,
    'rulers (people)': 7494,
    'scholars': 2596,
    'servants': 13527,
    'singers': 6341,
    'statesmen': 9579,
    'stationers': 11460,
    'stockbrokers': 6441,
    'surgeons': 13569,
    'teachers': 7949,
    'theaters (buildings)': 5751,
    'translators': 3854,
}
LANG_CODE_MAP = {
    'fre': 'fra',
    'ice': 'isl',
}
TERM_MAP = {
    'entity_type': (EntityType, ENTITY_TYPE_XPATH),
    'gender': (Gender, GENDER_XPATH),
    'maintenance_status': (MaintenanceStatus, MAINTENANCE_STATUS_XPATH),
    'name_part_type': (NamePartType, NAME_PART_TYPE_XPATH),
    'relationship_type': (EntityRelationType, RELATION_TYPE_XPATH),
}
# Mapping between terminology used in EAC-CPF and values used in the
# database.
TITLE_MAP = {
    '100b': 'ordinal number',
    '100c': 'proper title',
    'ordinalNumber': 'ordinal number',
    'properTitle': 'proper title',
}

# Order that name parts should be joined together to form a display
# name.
NAME_PARTS_ORDER = ['100a', '100b', '100d', '100c']


default_language = search_term_or_none('iso639-2', 'eng', exact=True)
default_publication_status = PublicationStatus.objects.get(title='published')
default_script = Script.objects.get(name='Latin')
normalise_space = re.compile(r'\s+').sub


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('project_id', help=PROJECT_ID_HELP, type=int)
        parser.add_argument('xml_path', help=XML_PATH_HELP,
                            nargs='+')

    @transaction.atomic
    def handle(self, *args, **options):
        xsd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                EAC_CPF_XSD_FILENAME)
        xsd_doc = etree.parse(xsd_path)
        xsd = etree.XMLSchema(xsd_doc)
        try:
            project = Project.objects.get(pk=options['project_id'])
        except Project.DoesNotExist:
            raise CommandError(NON_EXISTENT_PROJECT_ERROR.format(
                options['project_id']))
        # Since we have potential relationships between entities,
        # follow a two-step import process, in which every entity is
        # first created with its own data, and then every entity's
        # relationships to other entities are imported.
        entity_map = {}
        for xml_path in options['xml_path']:
            entity_import = self._import_entity(xml_path, project, xsd)
            entity_map[xml_path] = entity_import
        for xml_path in options['xml_path']:
            try:
                entity_map[xml_path].import_relations()
            except Exception as e:
                self.stdout.write(xml_path)
                raise e
        management.call_command('createinitialrevisions')
        self.stdout.write(UPDATE_SEARCH_INDEX_MSG)

    def _import_entity(self, xml_path, project, xsd):
        entity_import = EntityImport(xml_path, project)
        try:
            entity_import.import_entity(xsd)
        except Exception as e:
            self.stdout.write(xml_path)
            raise e
        return entity_import


class EntityImport:

    logger = logging.getLogger(__name__)

    def __init__(self, xml_path, project):
        self._xml_path = xml_path
        self._project = project
        # We need to keep track of the order of created identities, in
        # order to match up with the XML identities for the second
        # pass through creating relations (which are associated with
        # an identity). We can rely on document order if we process
        # all identities in document order both times through.
        self._identities = []

    def import_entity(self, xsd):
        """Import the non-relational data for the entity."""
        tree = self._parse_xml(xsd)
        try:
            entity_type = self._get_jargon_term(tree, 'entity_type')
        except CommandError:
            return
        entity = Entity(project=self._project, entity_type=entity_type)
        entity.save()
        self._entity_id = entity.id
        control = Control(entity=entity)
        self._import_control(control, tree)
        for index, identity in enumerate(tree.xpath(IDENTITY_XPATH,
                                                    namespaces=NS_MAP)):
            is_primary = False
            if index == 0:
                is_primary = True
            self._import_identity(entity, identity, is_primary)

    def import_relations(self):
        """Import the relationships this entity has with other entities."""
        tree = etree.parse(self._xml_path)
        if not self._identities:
            return
        for index, identity_el in enumerate(tree.xpath(
                IDENTITY_XPATH, namespaces=NS_MAP)):
            identity = self._identities[index]
            for relation in identity_el.xpath(
                    'following-sibling::e:relations/e:cpfRelation',
                    namespaces=NS_MAP):
                self._import_relation(identity, relation)

    def _get_jargon_term(self, tree, term_type):
        """Return a database object corresponding to a particular term in a
        particular model.

        The `term_type` is looked up in a mapping that provides the
        appropriate model and an XPath expression to get the actual
        term.

        :param tree: XML tree or element
        :type tree: `etree.ElementTree` or `etree.Element`
        :param term_type: type of term to get object for
        :type term_type: `str`
        :rtype: `object`

        """
        model, xpath = TERM_MAP[term_type]
        result = tree.xpath(xpath, namespaces=NS_MAP)
        if type(result) == etree._ElementUnicodeResult:
            title = result
        else:
            try:
                title = result[0]
            except IndexError:
                raise CommandError('"{}" has no "{}"'.format(
                    self._xml_path, term_type))
        real_title = TITLE_MAP.get(title, title)
        try:
            term = model.objects.get(title=real_title)
        except model.DoesNotExist:
            raise CommandError(MISSING_TERM_ERROR.format(
                self._xml_path, term_type, title))
        return term

    def _get_language(self, lang_code):
        """Return the `Language` object corresponding to `lang_code`.

        :param lang_code: three letter ISO 639-3 language code
        :type lang_code: `str`
        :rtype: `Language`

        """
        if not lang_code:
            return default_language
        lang_code = LANG_CODE_MAP.get(lang_code, lang_code)
        language = search_term_or_none('iso639-2', lang_code, exact=True)
        if language is None:
            raise CommandError(MISSING_LANGUAGE_ERROR.format(
                self._xml_path, lang_code))
        return language

    def _get_script(self, script_code):
        """Return the `Script` object corresponding to `script_code`.

        :param script_code: three letter script code
        :type script_code: `str`
        :rtype: `Script`

        """
        try:
            script = Script.objects.get(code=script_code)
        except Script.DoesNotExist:
            raise CommandError(MISSING_SCRIPT_ERROR.format(self._xml_path,
                                                           script_code))
        return script

    def _get_text(self, element, xpath):
        return normalise_space(' ', ''.join(
            element.xpath(xpath, namespaces=NS_MAP))).strip()

    def _import_biog_hist(self, description, biog_hist_el):
        abstract = self._get_text(biog_hist_el, 'e:abstract[1]//text()')
        sources = self._get_text(biog_hist_el, 'e:citation[1]//text()')
        content_parts = []
        for p in biog_hist_el.xpath('e:p', namespaces=NS_MAP):
            content_parts.append('<p>{}</p>'.format(
                self._get_text(p, './/text()')))
        content = ''.join(content_parts)
        copyright_parts = []
        for p in biog_hist_el.xpath(
                '/e:eac-cpf/e:control/e:rightsDeclaration[@localType='
                '"biogHist"]/e:descriptiveNote/e:p', namespaces=NS_MAP):
            copyright_parts.append('<p>{}</p>'.format(
                self._get_text(p, './/text()')))
        copyright = ''.join(copyright_parts)
        biog_hist = BiographyHistory(
            description=description, abstract=abstract, sources=sources,
            content=content, copyright=copyright)
        biog_hist.save()

    def _import_control(self, control, tree):
        control.maintenance_status = self._get_jargon_term(
            tree, 'maintenance_status')
        control.publication_status = default_publication_status
        control.language = self._get_language(tree.xpath(
            LANGUAGE_CODE_XPATH, namespaces=NS_MAP)[0])
        control.script = self._get_script(tree.xpath(
            SCRIPT_CODE_XPATH, namespaces=NS_MAP)[0])
        control.save()
        for source in tree.xpath(SOURCE_XPATH, namespaces=NS_MAP):
            self._import_source(control, source)

    def _import_date(self, holder, date_el):
        date = date_el.get('standardDate')
        if date is not None:
            holder.date_from = date
            holder.date_to = date
            holder.display_date = date_el.text
        else:
            date = date_el.get('notBefore')
            if date is not None:
                holder.date_from = date
                holder.display_date = '{} -'.format(date)

    def _import_date_range(self, holder, date_range_el):
        try:
            from_date = date_range_el.xpath('e:fromDate', namespaces=NS_MAP)[0]
        except IndexError:
            from_date = None
        display_date = ''
        if from_date is not None:
            holder.date_from = from_date.get('standardDate', '')
            display_date = from_date.text
        try:
            to_date = date_range_el.xpath('e:toDate', namespaces=NS_MAP)[0]
        except IndexError:
            to_date = None
        if to_date is not None:
            holder.date_to = to_date.get('standardDate', '')
            if display_date:
                display_date = '{} – {}'.format(display_date, to_date.text)
            else:
                display_date = '– {}'.format(to_date.text)
        holder.display_date = display_date

    def _import_description(self, identity, description_el):
        description = Description(identity=identity)
        description.save()
        for local_description in description_el.xpath(
                'e:localDescription[@localType="gender"]', namespaces=NS_MAP):
            self._import_local_description(description, local_description)
        for place in description_el.xpath('e:places/e:place',
                                          namespaces=NS_MAP):
            self._import_place(description, place)
        for function in description_el.xpath('e:functions/e:function/e:term',
                                             namespaces=NS_MAP):
            self._import_function(description, function)
        for language_used in description_el.xpath(
                'e:languagesUsed/e:languageUsed', namespaces=NS_MAP):
            self._import_language_used(description, language_used)
        for biography_history in description_el.xpath(
                'e:biogHist[1]', namespaces=NS_MAP):
            self._import_biog_hist(description, biography_history)
        for chron_item in description_el.xpath(
                'e:biogHist/e:chronList/e:chronItem', namespaces=NS_MAP):
            self._import_event(description, chron_item)

    def _import_display_name(self, name_entry_el):
        display_name = ''
        for part_type in NAME_PARTS_ORDER:
            part = self._get_text(
                name_entry_el, 'e:part[@localType="{}"]/text()'.format(
                    part_type))
            if not part:
                continue
            if not display_name:
                display_name = part
            elif part_type == '100b':
                display_name = display_name + ', ' + part
            else:
                display_name = display_name + ' ' + part
        return display_name

    def _import_event(self, description, chron_item):
        text = chron_item.xpath('e:event', namespaces=NS_MAP)[0].text
        event = Event(description=description, event=text)
        for date in chron_item.xpath('e:date', namespaces=NS_MAP):
            self._import_date(event, date)
        for date_range in chron_item.xpath('e:dateRange', namespaces=NS_MAP):
            self._import_date(event, date_range)
        event.save()

    def _import_function(self, description, term):
        try:
            function_id = FUNCTION_MAP[term.text]
        except KeyError:
            self.logger.warn(UNMAPPED_FUNCTION_ERROR.format(
                self._entity_id, self._xml_path, term.text))
            return
        function = Function(description=description, title=JFunction(
            pk=function_id))
        function.save()

    def _import_identity(self, entity, identity_el, is_primary):
        identity = Identity(entity=entity, preferred_identity=is_primary)
        for date in identity_el.xpath(
                '../e:description/e:existDates/e:date', namespaces=NS_MAP):
            self._import_date(identity, date)
        for date_range in identity_el.xpath(
                '../e:description/e:existDates/e:dateRange',
                namespaces=NS_MAP):
            self._import_date_range(identity, date_range)
        identity.save()
        self._identities.append(identity)
        for index, name_entry in enumerate(identity_el.xpath(
                'e:nameEntry[not(@localType="directOrder")]'
                '[e:part/@localType="100a"]',
                namespaces=NS_MAP)):
            is_authorised = False
            if index == 0:
                is_authorised = True
            self._import_name_entry(identity, name_entry, is_authorised)
        description = identity_el.xpath('following-sibling::e:description',
                                        namespaces=NS_MAP)[0]
        self._import_description(identity, description)

    def _import_language_used(self, description, language_used_el):
        language_script = LanguageScript(description=description)
        try:
            language_script.language = self._get_language(
                language_used_el.xpath('e:language/@languageCode',
                                       namespaces=NS_MAP)[0])
            language_script.script = self._get_script(
                language_used_el.xpath('e:script/@scriptCode',
                                       namespaces=NS_MAP)[0])
        except CommandError as e:
            self.logger.warn(e)
            return
        language_script.save()

    def _import_local_description(self, description, local_description_el):
        gender = self._get_jargon_term(local_description_el, 'gender')
        local_description = LocalDescription(description=description,
                                             gender=gender)
        for date_range in local_description_el.xpath('e:dateRange',
                                                     namespaces=NS_MAP):
            self._import_date_range(local_description, date_range)
        local_description.citation = self._get_text(local_description_el,
                                                    'e:citation//text()')
        local_description.save()

    def _import_name_entry(self, identity, name_entry_el, is_authorised):
        name_entry = NameEntry(identity=identity,
                               authorised_form=is_authorised)
        if name_entry_el.xpath('e:part[@localType="properTitle"]',
                               namespaces=NS_MAP):
            name_entry.is_royal_name = True
        name_entry.language = self._get_language(
            name_entry_el.get('{}lang'.format(XML)))
        name_entry.script = self._get_script(name_entry_el.get('scriptCode'))
        name_entry.display_name = self._import_display_name(name_entry_el)
        for date_range in name_entry_el.xpath('e:useDates/e:dateRange',
                                              namespaces=NS_MAP):
            # Note that the database model allows only one date range
            # per name entry; if more than one is present in the XML,
            # the last is used.
            self._import_date_range(name_entry, date_range)
        name_entry.save()
        for name_part in name_entry_el.xpath('e:part[@localType]',
                                             namespaces=NS_MAP):
            name_part_text = name_part.text.strip(' ,')
            name_part_type = name_part.get('localType')
            if name_part_type == '100a':
                bits = name_part_text.split(', ')
                self._import_name_part(name_entry, bits[0], 'surname')
                if len(bits) == 2:
                    self._import_name_part(name_entry, bits[1], 'forename')
                elif len(bits) > 2:
                    raise CommandError('Too many parts in 100a name part.')
            elif name_part_type in ('100d', '100q'):
                continue
            else:
                self._import_name_part(name_entry, name_part_text,
                                       TITLE_MAP[name_part_type])

    def _import_name_part(self, name_entry, part, part_type):
        try:
            name_part_type = NamePartType.objects.get(title=part_type)
        except NamePartType.DoesNotExist:
            raise CommandError(MISSING_TERM_ERROR.format(
                self._xml_path, 'NamePartType', part_type))
        name_part = NamePart(name_entry=name_entry, part=part,
                             name_part_type=name_part_type)
        name_part.save()

    def _import_place(self, description, place_el):
        place_entry = place_el.xpath('e:placeEntry', namespaces=NS_MAP)[0]
        if place_entry.text:
            place_name = normalise_space(' ', place_entry.text).strip()
        else:
            return
        geo_place = GeoPlace.get_or_create_from_geonames(place_name)
        if geo_place is None:
            self.logger.warn(PLACE_NOT_FOUND_ERROR.format(self._xml_path,
                                                          place_name))
            return
        role = place_el.xpath('e:placeRole', namespaces=NS_MAP)[0].text
        place = Place(description=description, place=geo_place, role=role)
        for date in place_el.xpath('e:date', namespaces=NS_MAP):
            self._import_date(place, date)
        place.save()

    def _import_relation(self, identity, relation_el):
        details = []
        for detail in relation_el.xpath('e:descriptiveNote/e:p',
                                        namespaces=NS_MAP):
            text = normalise_space(' ', ''.join(detail.xpath('.//text()')))
            details.append(text)
        relation_detail = ' '.join(details)
        relation_type = self._get_jargon_term(relation_el, 'relationship_type')
        name = self._get_text(relation_el, 'e:relationEntry[1]/text()')
        related_entity, created = Entity.get_or_create_by_display_name(
            name, default_language, default_script, self._project)
        if related_entity is None:
            raise CommandError(MULTIPLE_RELATED_ENTITIES_FOUND_ERROR.format(
                self._xml_path, name))
        relation = Relation(
            identity=identity, relation_type=relation_type,
            relation_detail=relation_detail, related_entity=related_entity)
        relation.save()

    def _import_source(self, control, source_el):
        name = source_el.xpath('e:sourceEntry', namespaces=NS_MAP)[0].text
        url = source_el.get('{}href'.format(XLINK), None)
        content_parts = []
        for p in source_el.xpath('e:descriptiveNote/e:p', namespaces=NS_MAP):
            content_parts.append('<p>{}</p>'.format(
                self._get_text(p, './/text()')))
        content = ''.join(content_parts)
        source = Source(control=control, name=name, url=url, notes=content)
        source.save()

    def _parse_xml(self, xsd):
        try:
            tree = etree.parse(self._xml_path)
        except etree.XMLSyntaxError as e:
            raise CommandError(NOT_WELL_FORMED_XML_ERROR.format(
                self._xml_path, e))
        try:
            xsd.assertValid(tree)
        except etree.DocumentInvalid as e:
            raise CommandError(INVALID_XML_ERROR.format(
                self._xml_path, e))
        return tree

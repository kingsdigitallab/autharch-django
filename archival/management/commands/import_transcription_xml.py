import os.path
import re

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lxml import etree

from ...models import ArchivalRecord, ArchivalRecordTranscription


HELP = """\
Import transcription XML files.

Existing transcriptions for the same record will likely cause the
process to fail - delete them first."""
NAMESPACES = {'tei': 'http://www.tei-c.org/ns/1.0'}
XML_PATH_HELP = 'Path to XML transcription file to import.'


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('xml_path', help=XML_PATH_HELP, nargs='+')

    @transaction.atomic
    def handle(self, *args, **options):
        xslt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'tei-to-html.xsl')
        self._transform = etree.XSLT(etree.parse(xslt_path))
        for xml_path in options['xml_path']:
            self._import_transcription(xml_path)
        management.call_command('createinitialrevisions')

    def _convert_transcription(self, xml_path):
        """Return the content and unique details of the transcription at
        `xml_path` converted from TEI into XHTML with the original TEI
        embedded as attributes."""
        tei = etree.parse(xml_path)
        html = str(self._transform(tei))
        xpath = '/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/' \
            'tei:respStmt[tei:resp="{}"]/tei:name/text()'
        transcriber = self._get_tei_metadata(
            tei, xpath.format('Transcribed by'))
        reviewer = self._get_tei_metadata(tei, xpath.format('Reviewed by'))
        corrector = self._get_tei_metadata(tei, xpath.format('Corrected by'))
        return html, transcriber, reviewer, corrector

    def _get_tei_metadata(self, tei, xpath):
        try:
            metadata = str(tei.xpath(xpath, namespaces=NAMESPACES)[0])
        except IndexError:
            metadata = ''
        return metadata

    def _get_record_details(self, xml_path):
        """Return the UUID of the ArchivalRecord the transcription at
        `xml_path` belongs to, and the transcription's page number.

        The filename portion of `xml_path` is expected to be of the
        form "<uuid>_<page number>.xml".

        """
        filename = os.path.basename(xml_path)
        prog = re.compile(r'(?P<uuid>RI.*)_(?P<page>\d{1,4})\.xml')
        match = prog.fullmatch(filename)
        if match is None:
            raise CommandError(
                'Transcription file at "{}" does not conform to expected '
                'filename pattern (<uuid>_<page number>.xml).'.format(
                    xml_path))
        return match.group('uuid'), int(match.group('page'))

    def _import_transcription(self, xml_path):
        uuid, page = self._get_record_details(xml_path)
        try:
            record = ArchivalRecord.objects.get(uuid=uuid)
        except ArchivalRecord.DoesNotExist:
            self.stderr.write(
                'Transcription file at "{}" has no corresponding '
                'ArchivalRecord object (uuid = {}).'.format(xml_path, uuid))
            return
        text, transcriber, reviewer, corrector = self._convert_transcription(
            xml_path)
        ArchivalRecordTranscription.objects.get_or_create(
            record=record, order=page, defaults={
                'transcription': text, 'transcriber': transcriber,
                'reviewer': reviewer, 'corrector': corrector})

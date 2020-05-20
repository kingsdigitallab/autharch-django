import os.path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import ArchivalRecord, ArchivalRecordImage


HELP = 'Import transcription image files.'
IMAGE_PATH_HELP = 'Path to image file.'
REPLACE_HELP = 'Replace existing images (same page on same record only).'

EXISTING_IMAGE_ERROR = ('Image already exists for page {} of record "{}"; '
                        'use --replace to automatically overwrite such.')
NO_ARCHIVAL_RECORD_ERROR = ('Transcription image at "{}" has no corresponding '
                            'ArchivalRecord object.')


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('-r', '--replace', help=REPLACE_HELP,
                            action='store_true')
        parser.add_argument('image_path', help=IMAGE_PATH_HELP, nargs='+')

    @transaction.atomic
    def handle(self, *args, **options):
        for image_path in options['image_path']:
            self._import_transcription(image_path, options['replace'])

    def _get_record(self, filename):
        """Return the ArchivalRecord that the transcription image called
        `filename` belongs to, and the transcription's page number."""
        parts = os.path.splitext(filename)[0].split('_')
        page = parts[-1]
        record = None
        if filename.startswith('GEO_MAIN_'):
            identifier = 'RI{}'.format(parts[2])
            try:
                record = ArchivalRecord.objects.get(uuid=identifier)
            except ArchivalRecord.DoesNotExist:
                record = None
        else:
            identifier = '/'.join(parts[:-1])
            try:
                record = ArchivalRecord.objects.get(
                    references__unitid=identifier)
            except ArchivalRecord.DoesNotExist:
                record = None
        return record, int(page)

    def _import_transcription(self, image_path, replace):
        filename = os.path.basename(image_path)
        record, page = self._get_record(filename)
        if record is None:
            self.stderr.write(NO_ARCHIVAL_RECORD_ERROR.format(image_path))
            return
        try:
            existing_image = ArchivalRecordImage.objects.get(record=record,
                                                             order=page)
        except ArchivalRecordImage.DoesNotExist:
            existing_image = None
        if existing_image is not None:
            if replace:
                existing_image.delete()
            else:
                raise CommandError(EXISTING_IMAGE_ERROR.format(page, record))
        image = ArchivalRecordImage(record=record, order=page)
        with open(image_path, 'rb') as fh:
            image_file = File(fh)
            image.image.save(filename, image_file, save=False)
        image.save()

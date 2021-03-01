import os

from django.core import management
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import ArchivalRecord, ArchivalRecordImage


HELP = 'Import transcription image files.'
IMAGES_PATH_HELP = 'Path to directory containing image files.'
REPLACE_HELP = 'Replace existing images (same page on same record only).'

EXISTING_IMAGE_ERROR = (
    'Cannot import image at "{}"; image already exists for page {} of record '
    '"{}"; use --replace to automatically overwrite such.')
MULTIPLE_PAGES_ERROR = 'Transcription image at "{}" has multiple valid pages.'
NO_ARCHIVAL_RECORD_ERROR = ('Transcription image at "{}" has no corresponding '
                            'ArchivalRecord object.')
NO_VALID_PAGE_ERROR = ('Transcription image at "{}" has no valid page '
                       'component.')


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('-r', '--replace', help=REPLACE_HELP,
                            action='store_true')
        parser.add_argument('images_path', help=IMAGES_PATH_HELP,
                            metavar='DIR')

    @transaction.atomic
    def handle(self, *args, **options):
        replace = options['replace']
        imported_images = 0
        for dirpath, dirnames, filenames in os.walk(options['images_path']):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.jpg':
                    image_path = os.path.join(dirpath, filename)
                    if self._import_transcription(image_path, replace):
                        self.stdout.write(image_path)
                        imported_images += 1
        self.stdout.write('Imported {} images.'.format(imported_images))
        management.call_command('createinitialrevisions')

    def _get_record(self, filename):
        """Return the ArchivalRecord that the transcription image called
        `filename` belongs to, and the transcription's page number."""
        parts = os.path.splitext(filename)[0].split('_')
        record = None
        try:
            page = int(parts[-1])
        except ValueError:
            return record, None
        identifier = '/'.join([part for part in parts[:-1] if part])
        try:
            record = ArchivalRecord.objects.get(
                references__unitid=identifier)
        except ArchivalRecord.DoesNotExist:
            record = None
        except ArchivalRecord.MultipleObjectsReturned:
            self.stderr.write(MULTIPLE_PAGES_ERROR.format(filename))
            record = None
        return record, page

    def _import_transcription(self, image_path, replace):
        filename = os.path.basename(image_path)
        record, page = self._get_record(filename)
        if page is None:
            self.stderr.write(NO_VALID_PAGE_ERROR.format(filename))
            return False
        if record is None:
            self.stderr.write(NO_ARCHIVAL_RECORD_ERROR.format(filename))
            return False
        try:
            existing_image = ArchivalRecordImage.objects.get(record=record,
                                                             order=page)
        except ArchivalRecordImage.DoesNotExist:
            existing_image = None
        if existing_image is not None:
            if replace:
                existing_image.delete()
            else:
                self.stderr.write('Duplicate: {} = {}'.format(
                    os.path.basename(image_path),
                    os.path.basename(existing_image.image.path))
                )
                return False
        image = ArchivalRecordImage(record=record, order=page)
        with open(image_path, 'rb') as fh:
            image_file = File(fh)
            image.image.save(filename, image_file, save=False)
        image.save()
        return True

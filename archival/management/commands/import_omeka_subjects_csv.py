"""Adds subjects to existing ArchivalRecord objects from the Omeka
export CSV.

The Omeka data contains information on records that exist in CALM, so
the records themselves are created via import_archival_data command
from the CALM export spreadsheets. We just need to add the subjects,
which are not part of that export.

"""

import csv

from django.core.management.base import BaseCommand
from django.db import transaction

import reversion

from archival.models import ArchivalRecord
from jargon.models import Function


HELP = 'Add subjects to existing entities from Omeka export CSV.'
CSV_HELP = 'Path to Omeka export CSV file.'

ADDED_SUBJECT_TERMS_MSG = 'Added subject terms from Omeka export CSV.'

NO_MATCHING_RECORD_MSG = \
    'UUID "{}" in row {} does not match an existing record; skipping.'


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('csv', help=CSV_HELP, type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options['csv'], newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for index, row in enumerate(reader):
                self._import_row(row, index)

    def _get_subject(self, term):
        if not term.startswith('http://www.ukat.org.uk'):
            return None
        term_id = term.split('/')[-1]
        try:
            function = Function.objects.get(
                uri__endswith='/{}'.format(term_id))
        except Function.DoesNotExist:
            try:
                function = Function.objects.get(
                    uri__endswith='/{}/'.format(term_id))
            except Function.DoesNotExist:
                return None
        return function

    def _get_subjects(self, row):
        subjects = []
        terms = row.get('ead:p.subject')
        if not terms:
            return []
        for term in terms.split(';'):
            subject = self._get_subject(term)
            if subject is not None:
                subjects.append(subject)
        return subjects

    def _import_row(self, row, index):
        uuid = row['ead:p.otherrecordid'].split(';')[0]
        try:
            record = ArchivalRecord.objects.get(uuid=uuid)
        except ArchivalRecord.DoesNotExist:
            self.stderr.write(NO_MATCHING_RECORD_MSG.format(uuid, index))
            return
        subjects = self._get_subjects(row)
        if subjects:
            with reversion.create_revision():
                reversion.set_comment(ADDED_SUBJECT_TERMS_MSG)
                for subject in subjects:
                    record.subjects.add(subject)

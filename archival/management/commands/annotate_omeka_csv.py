import csv

from django.core.management.base import BaseCommand

from jargon.models import Function


HELP = 'Generate CSV from Omeka export CSV annotated with subject terms.'
INPUT_CSV_HELP = 'Path to Omeka CSV.'
OUTPUT_CSV_HELP = 'Path to output CSV.'


class Command(BaseCommand):

    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('input_csv', help=INPUT_CSV_HELP)
        parser.add_argument('output_csv', help=OUTPUT_CSV_HELP)

    def handle(self, *args, **options):
        data = []
        cols = set()
        with open(options['input_csv'], newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                row_data = {}
                for col, value in row.items():
                    if value:
                        cols.add(col)
                        row_data[col] = value
                data.append(row_data)
        non_ukat_terms = set()
        for i, row in enumerate(data):
            term = row.get('ead:p.subject')
            if term:
                row['function'] = self._look_up_term(term, non_ukat_terms, i)
        fieldnames = sorted(list(cols) + ['function'])
        with open(options['output_csv'], 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        for non_ukat_term in non_ukat_terms:
            self.stderr.write(non_ukat_term)

    def _look_up_term(self, full_term, non_ukat_terms, row_number):
        new_terms = []
        terms = full_term.split(';')
        for term in terms:
            if term.startswith('http://www.ukat.org.uk'):
                term_id = term.split('/')[-1]
                try:
                    function_uri = Function.objects.get(
                        uri__endswith='/{}'.format(term_id)).uri
                    new_terms.append(function_uri)
                except Function.DoesNotExist:
                    # Because of course UKAT is entirely inconsistent
                    # in the URIs it assigns terms.
                    try:
                        function_uri = Function.objects.get(
                            uri__endswith='/{}/'.format(term_id)).uri
                        new_terms.append(function_uri)
                    except Function.DoesNotExist:
                        self.stderr.write(
                            'Could not find term "{}" in Function '
                            'data at row {}.'.format(term, row_number))
            else:
                non_ukat_terms.add(term)
                self.stderr.write('Non-UKAT term used: "{}"'.format(term))
        return ';'.join(new_terms)

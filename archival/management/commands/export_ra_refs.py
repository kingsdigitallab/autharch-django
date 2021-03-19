import json

from django.core.management.base import BaseCommand

from archival.models import File, Item
from jargon.models import ReferenceSource


HELP = """Write a JSON string giving individual RA Reference values for each
ArchivalRecord of the specified level(s), expanding ranges. Eg,
GEO/ADD/32/12-13 becomes GEO/ADD/32/12 and GEO/ADD/32/13. This file is
for use with image import, where images are associated with a single
RA Reference value. Deleted records are not exported."""
LEVEL_HELP = 'Level of records to export.'

FILE_LEVEL = 'file'
ITEM_LEVEL = 'item'
FILE_ITEM_LEVEL = 'both'
LEVEL_CHOICES = [FILE_ITEM_LEVEL, FILE_LEVEL, ITEM_LEVEL]


class Command(BaseCommand):
    help = HELP
    refs_map = {'duplicates': {}, 'errors': {}, 'refs': {}}

    def add_arguments(self, parser):
        parser.add_argument('level', choices=LEVEL_CHOICES, help=LEVEL_HELP)

    def handle(self, *args, **options):
        refs_map = {}
        ra_source = ReferenceSource.objects.get(title="RA")
        if options['level'] in (FILE_ITEM_LEVEL, FILE_LEVEL):
            for record in File.objects.exclude(
                    maintenance_status__title='deleted'):
                refs_map = self._handle_record(record, ra_source, refs_map)
        if options['level'] in (FILE_ITEM_LEVEL, ITEM_LEVEL):
            for record in Item.objects.exclude(
                    maintenance_status__title='deleted'):
                refs_map = self._handle_record(record, ra_source, refs_map)
        self.stdout.write(json.dumps(self.refs_map, indent=True))

    def _clean_ref(self, ref):
        # Full case: "GEO/MAIN/25050-29643, 30724 -32700,
        # 32922A-33264, 33498-34224, 51382a" (complete with improper space)
        refs = []
        parts = ref.split(',')
        # The first part forms the basis for all subsequent parts
        # (including itself, if it is a range; eg:
        # GEO/MAIN/25050-29643).
        #
        # Except when it's not: GEO/ADD/32/2/2-46, GEO/ADD/32/1023-1024
        base = ''
        for part in parts:
            part = part.strip()
            new_base = self._get_base_ref(part, base)
            if '-' in part:
                # If there is a range, use the new base (which may be
                # the old base).
                refs.extend(self._get_range_refs(new_base, part))
            else:
                # If there is no range, use the old base if it is the
                # same as the new base, or no base otherwise. This
                # accounts for "GEO/ADD/32/2/2, 4" and
                # "GEO/ADD/32/2/2, GEO/ADD/32/3/1" respectively.
                if new_base == base:
                    refs.append(base + part)
                else:
                    refs.append(part)
            base = new_base
        return refs

    def _get_base_ref(self, ref, old_base):
        """Returns the base ref from `ref`, suitable for prefixing partial
        refs. Eg, the base ref of GEO/MAIN/25050-29643 is GEO/MAIN/."""
        if '/' in ref:
            base = '/'.join(ref.split('-')[0].strip().split('/')[:-1]) + '/'
        elif ref.startswith('RCIN'):
            # Eg, RCIN 1028949 becomes RCIN.
            base = ref.split(' ')[0] + ' '
        else:
            base = old_base
        return base

    def _get_range_refs(self, base, range_ref):
        try:
            start_part, end_part = range_ref.split('-')
        except ValueError:
            self.refs_map['errors'][range_ref] = self.record_id
            return []
        if start_part.startswith(base):
            start_part = start_part[len(base):]
        try:
            start = int(start_part)
            end = int(end_part)
        except ValueError:
            self.refs_map['errors'][range_ref] = self.record_id
            return []
        return [base + str(i) for i in range(start, end + 1)]

    def _handle_record(self, record, ra_source, refs_map):
        self.record_id = record.pk
        refs = record.references.filter(source=ra_source).values_list(
            "unitid", flat=True)
        clean_refs = []
        for ref in refs:
            clean_refs.extend(self._clean_ref(ref))
        for ref in clean_refs:
            if ref in self.refs_map['duplicates']:
                self.refs_map['duplicates'][ref].append(self.record_id)
                continue
            if ref in self.refs_map['refs']:
                self.refs_map['duplicates'][ref] = [
                    self.refs_map['refs'].pop(ref), self.record_id]
                continue
            self.refs_map['refs'][ref] = self.record_id
        return refs_map

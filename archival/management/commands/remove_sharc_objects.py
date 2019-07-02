import logging

from archival.models import (Item, Project)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports entity data from a spreadsheet or csv file'
    logger = logging.getLogger(__name__)

    project, _ = Project.objects.get_or_create(
        title='Shakespeare in the Royal Collections',
        slug='SHARC')

    def handle(self, *args, **options):
        Item.objects.filter(project=self.project).delete()

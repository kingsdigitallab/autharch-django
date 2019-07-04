import logging

from archival.models import Project
from authority.models import Entity

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports entity data from a spreadsheet or csv file'
    logger = logging.getLogger(__name__)

    project, _ = Project.objects.get_or_create(
        title='Shakespeare in the Royal Collections',
        slug='sharc')

    def handle(self, *args, **options):
        Entity.objects.filter(project=self.project).delete()

from archival.models import ArchivalRecordSet, ArchivalRecord, Project
from authority.models import Entity
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sets the default project to GPP for existing data'
    project_slug = 'gpp'
    project_title = 'Georgian Papers Programme'
    models = [ArchivalRecord, ArchivalRecordSet, Entity]

    def handle(self, *args, **options):
        project_qs = Project.objects.filter(slug=self.project_slug)

        if project_qs.count():
            print("This script appears to have already been run.")
            exit(-1)
        else:
            project = Project()
            project.slug = self.project_slug
            project.title = self.project_title
            project.save()

            for model in self.models:
                self._set_project(model, project)

    def _set_project(self, model, project):
        qs = model.objects.filter(project=None)

        print("Setting project to {} for {} instance of {}".format(
            self.project_title,
            qs.count(),
            model
        )
        )
        for obj in qs:
            obj.project = project
            obj.save()

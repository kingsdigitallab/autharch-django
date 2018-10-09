import reversion
from django.contrib.auth.models import Group
from django.db import models
from reversion.models import Revision


class RevisionEvent(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class RevisionMetadata(models.Model):
    revision = models.OneToOneField(Revision, on_delete=models.CASCADE)
    event_type = models.ForeignKey(RevisionEvent, on_delete=models.PROTECT)
    editor_type = models.ForeignKey(Group, on_delete=models.PROTECT)


class Reference(models.Model):
    title = models.CharField(max_length=128)
    unitid = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Language(models.Model):
    """TODO: ISO639-2b"""
    pass


class Subject(models.Model):
    """TODO: UKAT"""
    pass


class Person(models.Model):
    """TODO: Person"""
    pass


class Organisation(models.Model):
    """TODO: Organisation"""
    pass


class Place(models.Model):
    """TODO: Place"""
    pass


class PublicationStatus(models.Model):
    title = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.title


class CollectionBase(models.Model):
    repository = models.CharField(max_length=512)
    repository_code = models.PositiveIntegerField()
    archival_level = models.CharField(max_length=32, editable=False)

    references = models.ManyToManyField(Reference)

    title = models.CharField(max_length=1024)
    provenance = models.TextField(blank=True, null=True)
    creation_dates = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    language = models.ManyToManyField(Language)
    extent = models.TextField()

    subjects = models.ManyToManyField(Subject)
    persons = models.ManyToManyField(Person)
    organisations = models.ManyToManyField(Organisation)
    places = models.ManyToManyField(Place)

    related_materials = models.TextField(blank=True, null=True)

    rights_declaration = models.TextField()
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)

    class Meta:
        abstract = True


@reversion.register()
class Collection(CollectionBase):
    administrative_history = models.TextField()
    arrangement = models.TextField()

    def __str__(self):
        return self.title


class Publication(models.Model):
    title = models.TextField(unique=True)

    def __str__(self):
        return self.title


class SeriesBase(models.Model):
    publications = models.ManyToManyField(Publication)

    class Meta:
        abstract = True


@reversion.register()
class Series(CollectionBase, SeriesBase):
    parent = models.ForeignKey('self', on_delete=models.CASCADE)
    arrangement = models.TextField()

    def __str__(self):
        return self.title


class RecordType(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class FileBase(models.Model):
    record_type = models.ManyToManyField(RecordType)

    physical_description = models.TextField(blank=True, null=True)

    copyright_status = models.TextField()
    publication_permission = models.TextField(blank=True, null=True)
    whithheld = models.TextField(blank=True, null=True)

    url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


@reversion.register()
class File(CollectionBase, SeriesBase, FileBase):
    parent = models.ForeignKey('self', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


@reversion.register()
class Item(CollectionBase, SeriesBase, FileBase):

    def __str__(self):
        return self.title

import reversion
from django.db import models
from languages_plus.models import Language
from reversion.models import Revision


class RevisionEvent(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class EditorType(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class RevisionMetadata(models.Model):
    revision = models.OneToOneField(Revision, on_delete=models.CASCADE)
    event_type = models.ForeignKey(RevisionEvent, on_delete=models.PROTECT)
    editor_type = models.ForeignKey(EditorType, on_delete=models.PROTECT)


class Reference(models.Model):
    title = models.CharField(max_length=128)
    unitid = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Subject(models.Model):
    """TODO: UKAT"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class Person(models.Model):
    """TODO: Person"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class Organisation(models.Model):
    """TODO: Organisation"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class Place(models.Model):
    """TODO: Place"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class PublicationStatus(models.Model):
    title = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name_plural = 'Publication status'

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
    languages = models.ManyToManyField(Language)
    extent = models.TextField()

    subjects = models.ManyToManyField(Subject)
    persons_as_subjects = models.ManyToManyField(Person)
    organisations_as_subjects = models.ManyToManyField(Organisation)
    places_as_subjects = models.ManyToManyField(Place)

    related_materials = models.TextField(blank=True, null=True)

    cataloguer = models.CharField(max_length=512)
    description_date = models.DateField()

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
    collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    arrangement = models.TextField()

    class Meta:
        verbose_name_plural = 'Series'

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
    series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    creators = models.ManyToManyField(Person, related_name='files_created')
    persons_as_relations = models.ManyToManyField(
        Person, related_name='files_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, related_name='files_as_relations')

    def __str__(self):
        return self.title


@reversion.register()
class Item(CollectionBase, SeriesBase, FileBase):
    f = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name='File')

    creators = models.ManyToManyField(Person, related_name='items_created')
    creation_places = models.ManyToManyField(
        Place, related_name='items_created')
    persons_as_relations = models.ManyToManyField(
        Person, related_name='items_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, related_name='items_as_relations')

    def __str__(self):
        return self.title

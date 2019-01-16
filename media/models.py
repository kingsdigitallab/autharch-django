import mimetypes
import reversion
from django.db import models
from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel


@reversion.register()
class Media(PolymorphicModel, TimeStampedModel):
    mime_type = models.CharField(max_length=32, blank=True, null=True)
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Media'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        mt, _ = mimetypes.guess_type(self.resource.url)
        if mt == self.mime_type:
            return

        self.mime_type = mt
        super().save(*args, **kwargs)


@reversion.register()
class File(Media):
    resource = models.FileField(upload_to='media/files')


@reversion.register()
class Image(Media):
    resource = models.ImageField(upload_to='media/images')

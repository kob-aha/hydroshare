from django.conf import settings
from django.utils.timezone import now
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import DefaultStorage

from django_irods.storage import IrodsStorage

class Bags(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    bag = models.FileField(upload_to='bags', max_length=500, storage=IrodsStorage() if getattr(settings,'USE_IRODS', False) else DefaultStorage(), null=True) # actually never null
    timestamp = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ['-timestamp']
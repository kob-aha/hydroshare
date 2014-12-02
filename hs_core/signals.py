from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.utils.timezone import now
from mezzanine.pages.models import Page, RichText
from mezzanine.pages.page_processors import processor_for
from uuid import uuid4
from mezzanine.core.models import Ownable
from mezzanine.generic.fields import CommentsField
from mezzanine.conf import settings as s
from mezzanine.generic.models import Keyword, AssignedKeyword
import os.path
from django_irods.storage import IrodsStorage
# from dublincore.models import QualifiedDublinCoreElement
from dublincore import models as dc
from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from dateutil import parser
from hs_core.models import AbstractResource
import json

@receiver(post_save)
def resource_creation_signal_handler(sender, instance, created, **kwargs):
    """Create initial dublin core elements"""
    if isinstance(instance, AbstractResource):
        if created:
            from hs_core.hydroshare import utils
            import json
            instance.metadata.create_element('title', value=instance.title)
            if instance.content:
                instance.metadata.create_element('description', abstract=instance.content)
            else:
                instance.metadata.create_element('description', abstract=instance.description)

            # TODO: With the current VM the get_user_info() method fails. So we can't get the resource uri for
            # the user now.
            # creator_dict = users.get_user_info(instance.creator)
            # instance.metadata.create_element('creator', name=instance.creator.get_full_name(),
            #                                  email=instance.creator.email,
            #                                  description=creator_dict['resource_uri'])

            instance.metadata.create_element('creator', name=instance.creator.get_full_name(), email=instance.creator.email)

            # TODO: The element 'Type' can't be created as we do not have an URI for specific resource types yet

            instance.metadata.create_element('date', type='created', start_date=instance.created)
            instance.metadata.create_element('date', type='modified', start_date=instance.updated)

            # res_json = utils.serialize_science_metadata(instance)
            # res_dict = json.loads(res_json)
            instance.metadata.create_element('identifier', name='hydroShareIdentifier', url='http://hydroshare.org/resource{0}{1}'.format('/', instance.short_id))

        else:
            resource_update_signal_handler(sender, instance, created, **kwargs)

    if isinstance(AbstractResource, sender):
        if created:
            instance.dublin_metadata.create(term='T', content=instance.title)
            instance.dublin_metadata.create(term='CR', content=instance.user.username)
            if instance.last_updated_by:
                instance.dublin_metadata.create(term='CN', content=instance.last_updated_by.username)
            instance.dublin_metadata.create(term='DT', content=instance.created)
            if instance.content:
                instance.dublin_metadata.create(term='AB', content=instance.content)
        else:
            resource_update_signal_handler(sender, instance, created, **kwargs)


def resource_update_signal_handler(sender, instance, created, **kwargs):
    """Add dublin core metadata based on the person who just updated the resource. Handle publishing too..."""

@receiver(post_save, sender=User)
def user_creation_signal_handler(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            instance.is_staff = True
            instance.save()
            instance.groups.add(Group.objects.get(name='Hydroshare Author'))





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
from languages_iso import languages as iso_languages
from dateutil import parser
import json

class GroupOwnership(models.Model):
    group = models.ForeignKey(Group)
    owner = models.ForeignKey(User)

class ResourcePermissionsMixin(Ownable):
    creator = models.ForeignKey(User,
                                related_name='creator_of_%(app_label)s_%(class)s',
                                help_text='This is the person who first uploaded the resource',
                                )

    public = models.BooleanField(
        help_text='If this is true, the resource is viewable and downloadable by anyone',
        default=True
    )
    # DO WE STILL NEED owners?
    owners = models.ManyToManyField(User,
                                    related_name='owns_%(app_label)s_%(class)s',
                                    help_text='The person who uploaded the resource'
    )
    frozen = models.BooleanField(
        help_text='If this is true, the resource should not be modified',
        default=False
    )
    do_not_distribute = models.BooleanField(
        help_text='If this is true, the resource owner has to designate viewers',
        default=False
    )
    discoverable = models.BooleanField(
        help_text='If this is true, it will turn up in searches.',
        default=True
    )
    published_and_frozen = models.BooleanField(
        help_text="Once this is true, no changes can be made to the resource",
        default=False
    )

    view_users = models.ManyToManyField(User,
                                        related_name='user_viewable_%(app_label)s_%(class)s',
                                        help_text='This is the set of Hydroshare Users who can view the resource',
                                        null=True, blank=True)

    view_groups = models.ManyToManyField(Group,
                                         related_name='group_viewable_%(app_label)s_%(class)s',
                                         help_text='This is the set of Hydroshare Groups who can view the resource',
                                         null=True, blank=True)

    edit_users = models.ManyToManyField(User,
                                        related_name='user_editable_%(app_label)s_%(class)s',
                                        help_text='This is the set of Hydroshare Users who can edit the resource',
                                        null=True, blank=True)

    edit_groups = models.ManyToManyField(Group,
                                         related_name='group_editable_%(app_label)s_%(class)s',
                                         help_text='This is the set of Hydroshare Groups who can edit the resource',
                                         null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def permissions_store(self):
        return s.PERMISSIONS_DB

    def can_add(self, request):
        return self.can_change(request)

    def can_delete(self, request):
        return self.can_change(request)

    def can_change(self, request):
        user = get_user(request)

        if user.is_authenticated():
            if user.is_superuser:
                ret = True
            elif self.creator and user.pk == self.creator.pk:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            elif self.edit_users.filter(pk=user.pk).exists():
                ret = True
            elif self.edit_groups.filter(pk__in=set(g.pk for g in user.groups.all())):
                ret = True
            else:
                ret = False
        else:
            ret = False

        return ret


    def can_view(self, request):
        user = get_user(request)

        if self.public:
            return True
        if user.is_authenticated():
            if user.is_superuser:
                ret = True
            elif self.creator and user.pk == self.creator.pk:
                ret = True
            elif user.pk in { o.pk for o in self.owners.all() }:
                ret = True
            elif self.view_users.filter(pk=user.pk).exists():
                ret = True
            elif self.view_groups.filter(pk__in=set(g.pk for g in user.groups.all())):
                ret = True
            else:
                ret = False
        else:
            ret = False

        return ret

def short_id():
    return uuid4().hex

class AbstractResource(ResourcePermissionsMixin):
    """
    All hydroshare objects inherit from this mixin.  It defines things that must
    be present to be considered a hydroshare resource.  Additionally, all
    hydroshare resources should inherit from Page.  This gives them what they
    need to be represented in the Mezzanine CMS.

    In some cases, it is possible that the order of inheritence matters.  Best
    practice dictates that you list pages.Page first and then other classes:

        class MyResourceContentType(pages.Page, hs_core.AbstractResource):
            ...
    """
    last_changed_by = models.ForeignKey(User,
                                        help_text='The person who last changed the resource',
                                        related_name='last_changed_%(app_label)s_%(class)s',
                                        null=True
    )
    dublin_metadata = generic.GenericRelation(
        'dublincore.QualifiedDublinCoreElement',
        help_text='The dublin core metadata of the resource'
    )
    files = generic.GenericRelation('hs_core.ResourceFile', help_text='The files associated with this resource')
    bags = generic.GenericRelation('hs_core.Bags', help_text='The bagits created from versions of this resource')
    short_id = models.CharField(max_length=32, default=short_id, db_index=True)
    doi = models.CharField(max_length=1024, blank=True, null=True, db_index=True,
                           help_text='Permanent identifier. Never changes once it\'s been set.')
    comments = CommentsField()

    # this is to establish a relationship between a resource and
    # any metadata container object (e.g., CoreMetaData object)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # this property needs to be overriden by any specific resource type
    # that needs additional metadata elements on top of core metadata data elements
    @property
    def metadata(self):
        md = CoreMetaData() # only this line needs to be changed when you override
        return self._get_metadata(md)

    def _get_metadata(self, metatdata_obj):
        md_type = ContentType.objects.get_for_model(metatdata_obj)
        res_type = ContentType.objects.get_for_model(self)
        self.content_object = res_type.model_class().objects.get(id=self.id).content_object
        if self.content_object:
            return self.content_object
        else:
            metatdata_obj.save()
            self.content_type = md_type
            self.object_id = metatdata_obj.id
            self.save()
            return metatdata_obj

    def extra_capabilites(self):
        """This is not terribly well defined yet, but should return at the least a JSON serializable object of URL
        endpoints where extra self-describing services exist and can be queried by the user in the form of
        { "name" : "endpoint" }
        """
        return None

    class Meta:
        abstract = True
        unique_together = ("content_type", "object_id")

def get_path(instance, filename):
    return os.path.join(instance.content_object.short_id, filename)

class ResourceFile(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    resource_file = models.FileField(upload_to=get_path, max_length=500, storage=IrodsStorage() if getattr(settings,'USE_IRODS', False) else DefaultStorage())

class Bags(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    bag = models.FileField(upload_to='bags', max_length=500, storage=IrodsStorage() if getattr(settings,'USE_IRODS', False) else DefaultStorage(), null=True) # actually never null
    timestamp = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ['-timestamp']



class GenericResource(Page, RichText, AbstractResource):

    class Meta:
        verbose_name = 'Generic Hydroshare Resource'

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)

def resource_processor(request, page):
    extra = page_permissions_page_processor(request, page)
    extra['res'] = page.get_content_model()
    extra['dc'] = { m.term_name : m.content for m in extra['res'].dublin_metadata.all() }
    return extra


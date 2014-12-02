import os.path
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import DefaultStorage

from mezzanine.pages.models import Page, RichText
from mezzanine.core.models import Ownable
from mezzanine.generic.fields import CommentsField
from mezzanine.conf import settings as s

from django_irods.storage import IrodsStorage

# Do NOT import get_user from hs_core.views.utils
# as it will cause a circular import
def get_user(request):
    """
    Determine the user from the request object.

    TODO: Add support for API keys
    :param request: HTTP request object
    :return: Django User object instance representing the user
    """
    user = None
    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.pk)
    else:
        user = request.user
    return user


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




# this should be used as the page processor for anything with pagepermissionsmixin
# page_processor_for(MyPage)(ga_resources.views.page_permissions_page_processor)
def page_permissions_page_processor(request, page):
    page = page.get_content_model()
    user = get_user(request)

    return {
        "edit_groups": set(page.edit_groups.all()),
        "view_groups": set(page.view_groups.all()),
        "edit_users": set(page.edit_users.all()),
        "view_users": set(page.view_users.all()),
        "can_edit": (user in set(page.edit_users.all())) \
                    or (len(set(page.edit_groups.all()).intersection(set(user.groups.all()))) > 0)
    }

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
    short_id = models.CharField(max_length=32, default=short_id(), db_index=True)
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


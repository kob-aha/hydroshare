__author__ = 'Hong Yi'
## Note: this module has been imported in the models.py in order to receive signals
## at the end of the models.py for the import of this module
from django.dispatch import receiver
from hs_core import hydroshare
from hs_core.hydroshare import pre_create_resource, post_create_resource
from hs_core.signals import *
from hs_uri_resource.models import UriResource

res_md_dict = {}
# signal handler to return template contexts
# to populate create-resource.html template page
@receiver(pre_describe_resource, sender=UriResource)
def uri_describe_resource_trigger(sender, **kwargs):
    if(sender is UriResource):
        # create a dict of dicts with the metadata terms in it
        pass
       
# signal handler to validate resource metadata, and if valid, retrieve
# values from create-resource.html page and return a dictionary of metadata_terms to be passed on to
# hydroshare.create_resource() call to use when creating the resource
@receiver(pre_call_create_resource, sender=UriResource)
def raster_pre_call_resource_trigger(sender, **kwargs):
    if(sender is UriResource):
        pass

# signal handler to save metadata after resource is created
@receiver(post_create_resource, sender=UriResource)
def raster_post_trigger(sender, **kwargs):
    if sender is UriResource:
        resource = kwargs['resource']
        resource.metadata.create_element('ReferenceUri', value="http://www.example.com")
from django.db import models
from django.contrib.contenttypes import generic
from hs_core.models import AbstractResource, resource_processor, CoreMetaData
from hs_core.models import AbstractMetaDataElement
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.contenttypes.models import ContentType
from mezzanine.pages.models import Page
from mezzanine.pages.page_processors import processor_for
#
# To create a new resource, use these two super-classes.
#
class UriResource(Page, AbstractResource):
    url_res_link = models.URLField(null=True)  # resolved into the 'relation' metadata element
    class Meta:
        verbose_name = 'URI Link Resource'

    def extra_capabilities(self):
        return None

    @property
    def metadata(self):
        md = UriMetaData()
        return self._get_metadata(md)

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)


processor_for(UriResource)(resource_processor)

@processor_for(UriResource)
def main_page(request, page):
    from dublincore import models as dc
    from django import forms

    class DCTerm(forms.ModelForm):
        class Meta:
            model=dc.QualifiedDublinCoreElement
            fields = ['term', 'content']

    content_model = page.get_content_model()

    return  { 'resource_type' : content_model._meta.verbose_name,
              'link' : content_model.link,
              'dublin_core' : [t for t in content_model.dublin_metadata.all().exclude(term='AB')],
              'dcterm_frm' : DCTerm()
            }

class ReferenceUri(AbstractMetaDataElement):
    term = 'Reference URI'
    value = models.URLField(null=True)

    @classmethod
    def create(cls, **kwargs):
        if 'value' in kwargs:
            if 'content_object' in kwargs:
                content_object = kwargs['content_object']
                metadata_type = ContentType.objects.get_for_model(content_object)
                uri_ref = ReferenceUri.objects.filter(value__iexact=kwargs['value'], object_id=content_object.id, content_type=metadata_type).first()
                if uri_ref:
                    raise ValidationError('Reference URI %s already exists' % kwargs['value'])
                uri_ref = ReferenceUri.objects.create(value=kwargs['value'], content_object=content_object)
                return uri_ref
            else:
                raise ValidationError('Metadata instance for which uri_ref element to be created is missing.')
        else:
            raise ValidationError("Value of uri_ref is missing.")


    @classmethod
    def update(cls, element_id, **kwargs):
        uri_ref = ReferenceUri.objects.get(id=element_id)
        if uri_ref:
            if 'value' in kwargs:
                uri_ref.value = kwargs['value']
                uri_ref.save()
            else:
                raise ValidationError('Value of uri_ref is missing')
        else:
            raise ObjectDoesNotExist("No uri_ref element was found for the provided id:%s" % kwargs['id'])

    @classmethod
    def remove(cls, element_id):
        uri_ref = ReferenceUri.objects.get(id=element_id)
        if uri_ref:
            uri_ref.delete()
        else:
            raise ObjectDoesNotExist("No uri_ref element was found for id:%d." % element_id)


class UriMetaData(CoreMetaData):
    # should be only one reference uri
    reference_uris = generic.GenericRelation(ReferenceUri)
    _uri_resource = generic.GenericRelation(UriResource)

    @classmethod
    def get_supported_element_names(cls):
        # get the names of all core metadata elements
        elements = super(UriMetaData, cls).get_supported_element_names()
        # add the name of any additional element to the list
        elements.append('ReferenceUri') # needs to match the classname
        return elements

    @property
    def resource(self):
        return self._uri_resource.all().first()

    def get_xml(self):
        from lxml import etree
        # get the xml string representation of the core metadata elements
        xml_string = super(UriMetaData, self).get_xml(pretty_print=False)

        # create an etree xml object
        RDF_ROOT = etree.fromstring(xml_string)

        # get root 'Description' element that contains all other elements
        container = RDF_ROOT.find('rdf:Description', namespaces=self.NAMESPACES)

        # inject netcdf resource specific metadata element 'variable' to container element
        # example xml code for one variable metadata based on the following python code
        # <hsterms:netcdfVariable>
        # <rdf:Description>
        # <hsterms:name>SWE</hsterms:name>
        # <hsterms:unit>m</hsterms:unit>
        # <hsterms:type>float</hsterms:type>
        # <hsterms:shape>y,x,time</hsterms:shape>
        # <hsterms:descriptiveName>snow water equivalent</hsterms:descriptiveName>
        # <hsterms:uri_ref>UEB model simulation for TWDEF site</hsterms:uri_ref>
        # <hsterms:missingValue>-9999</hsterms:missingValue>
        # </rdf:Description>
        # </hsterms:netcdfVariable>

        #inject Uri resource specific metadata element "reference uri" into container element
        for ref in self.reference_uris.all():
            hsterms_method = etree.SubElement(container, '{%s}Reference URI' % self.NAMESPACES['hsterms'])
            hsterms_method_rdf_Description = etree.SubElement(hsterms_method, '{%s}Description' % self.NAMESPACES['rdf'])

            hsterms_name = etree.SubElement(hsterms_method_rdf_Description, '{%s}value' % self.NAMESPACES['hsterms'])
            hsterms_name.text = ref.value

        return etree.tostring(RDF_ROOT, pretty_print=True)

import receivers

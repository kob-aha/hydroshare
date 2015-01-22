from django.db import models
from hs_core.models import AbstractResource, resource_processor, CoreMetaData
from mezzanine.pages.page_processors import processor_for
#
# To create a new resource, use these two super-classes.
#
class UriResource(Page, AbstractResource):
    link = models.URLField()
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

class UriMetaData(CoreMetaData):
    @classmethod
    def get_supported_element_names(cls):
        # get the names of all core metadata elements
        elements = super(UriMetaData, cls).get_supported_element_names()
        # add the name of any additional element to the list
        #none
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
        # <hsterms:method>UEB model simulation for TWDEF site</hsterms:method>
        # <hsterms:missingValue>-9999</hsterms:missingValue>
        # </rdf:Description>
        # </hsterms:netcdfVariable>

        return etree.tostring(RDF_ROOT, pretty_print=True)

import receivers

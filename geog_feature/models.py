from django.db import models
from mezzanine.pages.models import Page, RichText
from hs_core.models import AbstractResource
from hs_core.models import resource_processor, CoreMetaData, AbstractMetaDataElement
from mezzanine.pages.page_processors import processor_for
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

# Create your models here.


class GeogFeature(Page, AbstractResource):
    class Meta:
                verbose_name = "Geographic Feature Resource"

    @property
    def metadata(self):
        md = GeogFeatureMetaData()
        return self._get_metadata(md)


    def extra_capabilities(self):
        return None

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)

processor_for(GeogFeature)(resource_processor)


class PositionalAccuracy(AbstractMetaDataElement):
    term = 'Positional Accuracy'
    value = models.CharField(max_length=200)

    def __unicode__(self):
        self.name

    @classmethod
    def create(cls, **kwargs):
        # Check the required attributes and create new variable meta instance
        if 'value' in kwargs:
            # check if the variable metadata already exists
            metadata_obj = kwargs['content_object']
            metadata_type = ContentType.objects.get_for_model(metadata_obj)
            positional_accuracy = PositionalAccuracy.objects.filter(name__iexact=kwargs['name'], object_id=metadata_obj.id,
                                               content_type=metadata_type).first()
            return positional_accuracy
        else:
            raise ValidationError("Positional accuracy is missing.")


    @classmethod
    def update(cls, element_id, **kwargs):
        positional_accuracy = PositionalAccuracy.objects.get(id=element_id)
        if positional_accuracy:
            if 'value' in kwargs:
                positional_accuracy.value = kwargs['value']
                positional_accuracy.save()
            else:
                raise ValidationError('Value of positional accuracy is missing')
        else:
            raise ObjectDoesNotExist("No positional accuracy element was found for the provided id:%s" % kwargs['id'])

    @classmethod
    def remove(cls, element_id):
        positional_accuracy = PositionalAccuracy.objects.get(id=element_id)
        if positional_accuracy:
            positional_accuracy.delete()
        else:
            raise ObjectDoesNotExist("No positional accuracy element was found for id:%d." % element_id)

class GeogFeatureMetaData(CoreMetaData):
    positional_accuracies = generic.GenericRelation(PositionalAccuracy)
    _geog_feature_resource = generic.GenericRelation(GeogFeature)

    @classmethod
    def get_supported_element_names(cls):
        # get the names of all core metadata elements
        elements = super(GeogFeatureMetaData, cls).get_supported_element_names()
        # add the name of any additional element to the list
        elements.append('Positional Accuracy')
        return elements

    @property
    def resource(self):
        return self._geog_feature_resource.all().first()

    def get_xml(self):
        from lxml import etree
        # get the xml string representation of the core metadata elements
        xml_string = super(GeogFeatureMetaData, self).get_xml(pretty_print=False)

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

        for positional_accuracy in self.positional_accuracies.all():
            hsterms_positional_accuracy = etree.SubElement(container, '{%s}PositionalAccuracy' % self.NAMESPACES['hsterms'])
            hsterms_positional_accuracy_rdf_Description = etree.SubElement(hsterms_positional_accuracy, '{%s}Description' % self.NAMESPACES['rdf'])

            hsterms_value = etree.SubElement(hsterms_positional_accuracy_rdf_Description, '{%s}value' % self.NAMESPACES['hsterms'])
            hsterms_value.text = positional_accuracy.value

        return etree.tostring(RDF_ROOT, pretty_print=True)
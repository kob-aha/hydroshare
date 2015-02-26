from django.contrib.contenttypes import generic

from mezzanine.pages.models import Page

from hs_core.models import AbstractResource, CoreMetaData


class RHESSysInstResource(Page, AbstractResource):
    class Meta:
        verbose_name = 'Geographic Raster Resource'

    @property
    def metadata(self):
        md = RHESSysInstMetaData()
        return self._get_metadata(md)

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)

class RHESSysInstMetaData(CoreMetaData):
    pass
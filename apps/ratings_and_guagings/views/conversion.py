__author__ = 'valentin'
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from datetime import datetime
import django_filters
from rest_framework import filters

from ..models import conversions
from ..models import gauging, monintoring_point, parameter

from ..tests import testData

class conversionGroupFilter(filters.BaseFilterBackend):
    #monitoringPoint = django_filters.CharFilter(name="id",)
    paramFrom = django_filters.CharFilter(name="paramFrom__id")
    paramTo = django_filters.CharFilter(name="paramTo__id")

    def filter_queryset(self, request, queryset, view):
       return queryset
    #    return queryset.filter(owner=request.user)

    class Meta:
        model = conversions.conversionGroup
        fields = ('paramFrom', 'paramTo')


class conversionsView(viewsets.GenericViewSet):
#     """
#     Returns conversions.
#     """
    serializer_class = conversions.conversionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('monitoringPoint', 'in_stock')

    paginate_by = None
    page_kwarg = None
    paginate_by_param=None
#    filter_backends = (filters.DjangoFilterBackend,)


    # For GET Requests
    #@list_route
    def list(self, request,a=None):
        """ Returns a list of location objects somehow related to MyObject """
        objects = testData.conversionList1
        serializer = self.serializer_class(objects, many=True, context={'request': request})
        return Response(serializer.data)

class conversionGroupView(viewsets.GenericViewSet):
#     """
#     Returns conversions.
#     """
    serializer_class = conversions.conversionGroupSerializer
    filter_class = conversionGroupFilter
    paginate_by = None
    page_kwarg = None
    paginate_by_param=None
    filter_fields = ('monitoringPoint', 'paramFrom', 'paramTo')
    # For GET Requests
    #@list_route
    def list(self, request, monitoringPoint=None):
        """ Returns a list of location objects somehow related to MyObject """
        objects = testData.cg1
        serializer = self.serializer_class(objects, many=True, context={'request': request})
        return Response(serializer.data)
__author__ = 'valentin'
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
import django_filters

from ..models import monintoring_point


from ..tests import testData


class MonitoringPointView(viewsets.GenericViewSet):
#     """
#     Returns MonitoringPoints.
#     """

    serializer_class = monintoring_point.MonitoringPointSerializer
    paginate_by = None
    page_kwarg = None
    paginate_by_param=None

#lookup_field = 'id'

    # For GET Requests
    #@list_route
    def list(self, request):
        """ Returns a list of location objects somehow related to MyObject """
        locations = testData.mpList1
        serializer = self.serializer_class(locations, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None,):
        """ Returns a list of location objects somehow related to MyObject """
        locations = testData.mp1
        serializer = self.serializer_class(locations)
        return Response(serializer.data)


__author__ = 'valentin'
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets,mixins
from rest_framework.decorators import detail_route, list_route
from datetime import datetime

from ..models import gauging, monintoring_point, parameter

from ..tests import testData

mp = monintoring_point.MonitoringPoint(id="1",name="a",cease_to_flow=24,verticalDatum="NAD",shape=None)



class GaugingView(viewsets.GenericViewSet):
#     """
#     Returns Gauging.
#     """
    serializer_class = gauging.gaugingSerializer
    paginate_by = None
    page_kwarg = None
    paginate_by_param=None


    # For GET Requests
    #@list_route
    def list(self, request):
        """ Returns a list of location objects somehow related to MyObject """
        objects = testData.gaugingList1
        serializer = self.serializer_class(objects, many=True)
        return Response(serializer.data)

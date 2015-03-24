__author__ = 'valentin'
from rest_framework import serializers
from .point import PointSerializer, Point
from ..serializer_utils import CustomHyperlinkedField

#from django.db import models
from django.contrib.gis.db import models

class MonitoringPoint(models.Model):
    id = models.AutoField()
    name = models.CharField(max_length=200)
    cease_to_flow = models.DecimalField( decimal_places=2)
    verticalDatum = models.CharField(max_length=30)
    shape = models.GeometryField(srid='EPSG:4326', geography=True)
    #conversiongroup_set= conversiongroup_set
    control = models.CharField(max_length=200)
    #rangeGroups = rangeGroups
    objects = models.GeoManager()
  #
#     def __init__(self, id, name, cease_to_flow, verticalDatum, shape,  conversiongroup_set=None, control=None,rangeGroups=None ):
# #    def __init__(self):
#         self.id = id
#         self.name = name
#         self.cease_to_flow = cease_to_flow
#         self.verticalDatum = verticalDatum
#         self.shape = shape
#         self.conversiongroup_set= conversiongroup_set
#         self.control = control
#         self.rangeGroups = rangeGroups
    #
    # def create( id, name, cease_to_flow, verticalDatum, shape,  conversiongroup_set=None, control=None,rangeGroups=None ):
    #     id = id
    #     name = name
    #     cease_to_flow = cease_to_flow
    #     verticalDatum = verticalDatum
    #     shape = shape
    #     conversiongroup_set= conversiongroup_set
    #     control = control
    #     rangeGroups = rangeGroups
    # pass


class MonitoringPointSerializer(serializers.Serializer):
        id = serializers.CharField(max_length=200)
        name = serializers.CharField(max_length=200)
        #cease_to_flow = cease_to_flow
        verticalDatum = serializers.CharField(max_length=200)
        shape = PointSerializer()

        conversiongroup_set= CustomHyperlinkedField(
            view_name='conversiongroup-detail',
            lookup_field='id',
            many=True,
            read_only=True
        )
        class Meta:
            model=MonitoringPoint
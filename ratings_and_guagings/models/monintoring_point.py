__author__ = 'valentin'
from rest_framework import serializers

class MonitoringPoint(object):
    def __init__(self, id, name, cease_to_flow, verticalDatum, shape,  conversiongroup_set=None, control=None,rangeGroups=None ):
        self.id = id
        self.name = name
        self.cease_to_flow = cease_to_flow
        self.verticalDatum = verticalDatum
        self.shape = shape
        self.conversiongroup_set= conversiongroup_set
        self.control = control
        self.rangeGroups = rangeGroups

class MonitoringPointSerialier(serializers.HyperlinkedModelSerializer):
        id = serializers.CharField(max_length=200)
        name = serializers.CharField(max_length=200)
        cease_to_flow = cease_to_flow
        verticalDatum = serializers.CharField(max_length=200)
        shape = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            lookup_field='username',
            many=True,
            read_only=True
        )
        conversiongroup_set= serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            lookup_field='username',
            many=True,
            read_only=True
        )
__author__ = 'valentin'
from rest_framework import serializers

class Point (object):
    def __init__(self, lat,  lon,  ):
         self.type = "Point"
         self.coordinates = [lon,lat]

class PointSerializer(serializers.Serializer):
    type= serializers.CharField(max_length=24)
    coordinates = serializers.ListField(
        child=serializers.IntegerField(min_value=-360, max_value=360)
    )



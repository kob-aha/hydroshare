__author__ = 'valentin'

from rest_framework import serializers
from ..models import monintoring_point, parameter

from django.db import models

import parameter
import monintoring_point

class gauging(object):
    featureOfInterest = models.ForeignKey(monintoring_point.MonitoringPoint, )
        # 	"title":"featureOfInterest",
        # 	"format":"uri",
        # 	"required":true
    id =  models.AutoField(primary_key=True)
    # 		"title":"id",
    # 		"required":true
    phenomenonTime = models.DateTimeField()
    # 					"title":"phenomenonTime",
    # 					"type":"string",
    # 					"required":true
    quality = models.ForeignKey(parameter.parameter, )
    # 					"title":"quality",
    # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    observedPropertyFrom = models.ForeignKey(parameter.parameter, )
    # 		"title":"observedPropertyFrom",
    # 		"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    observedPropertyTo = models.ForeignKey(parameter.parameter, )
    # 					"title":"observedPropertyTo",
    # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    fromValue =  models.DecimalField( decimal_places=2)
    # 					"title":"fromValue",
    # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
    # 					"required":true
    toValue =  models.DecimalField( decimal_places=2)
    # 					"title":"toValue",
    # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
    # 					"required":true

    # def __init__(self, id, featureOfInterest, phenomenonTime, observedPropertyFrom, observedPropertyTo, fromValue, toValue, quality=None ):
    #     self.featureOfInterest = featureOfInterest
    #         # 	"title":"featureOfInterest",
    #         # 	"format":"uri",
    #         # 	"required":true
    #     self.id = id
    #     # 		"title":"id",
    #     # 		"required":true
    #     self.phenomenonTime = phenomenonTime
    #     # 					"title":"phenomenonTime",
    #     # 					"type":"string",
    #     # 					"required":true
    #     self.quality = quality
    #     # 					"title":"quality",
    #     # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    #     self.observedPropertyFrom = observedPropertyFrom
    #     # 		"title":"observedPropertyFrom",
    #     # 		"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    #     self.observedPropertyTo = observedPropertyTo
    #     # 					"title":"observedPropertyTo",
    #     # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    #     self.fromValue = fromValue
    #     # 					"title":"fromValue",
    #     # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
    #     # 					"required":true
    #     self.toValue = toValue
    #     # 					"title":"toValue",
    #     # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
    #     # 					"required":true



class gaugingSerializer(serializers.Serializer):
    featureOfInterest = monintoring_point.MonitoringPointSerializer()
    id = serializers.CharField(max_length=50)
    quality = parameter.ParameterSerializer()
    observedPropertyFrom = parameter.ParameterSerializer()
    observedPropertyTo = parameter.ParameterSerializer()
    fromValue = serializers.DecimalField(max_digits=5, decimal_places=2)
    toValue = serializers.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        model=gauging
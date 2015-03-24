__author__ = 'valentin'

from rest_framework import serializers


from .parameter import  ParameterSerializer
from  ..serializer_utils import CustomHyperlinkedField

from django.db import models

import parameter
import monintoring_point

class conversionGroup(object):
    id = models.AutoField()
                # "title":"id",
                # "type":"string",
                # "required":true
    fullConversion = models.BooleanField()
            # "title":"fullConversion",
            # "type":"boolean",
            # "required":true
    paramFrom = models.ForeignKey(parameter.parameter, )
            # "title":"paramFrom",
            # "$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    paramTo = models.ForeignKey(parameter.parameter, )
            # "title":"paramTo",
            # "$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
    conversionPeriods = models.ForeignKey('conversionPeriod', )
            # "title":"conversionPeriods",
            # "type":"array",
            # "items":{
            # 	"type":"any",
            # 	"minItems":"1"

#      def __init__(self, id, monitoringPoint,fullConversion, paramFrom, paramTo, conversionPeriods = None, ):
# #    def create(self, id, monitoringPoint,fullConversion, paramFrom, paramTo, conversionPeriods = None, ):
# 			self.id = id
# 					# "title":"id",
# 					# "type":"string",
# 					# "required":true
# 			self.fullConversion = fullConversion
# 					# "title":"fullConversion",
# 					# "type":"boolean",
# 					# "required":true
# 			self.paramFrom = paramFrom
# 					# "title":"paramFrom",
# 					# "$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
# 			self.paramTo = paramTo
# 					# "title":"paramTo",
# 					# "$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
# 			self.conversionPeriods = conversionPeriods
# 					# "title":"conversionPeriods",
# 					# "type":"array",
# 					# "items":{
# 					# 	"type":"any",
# 					# 	"minItems":"1"



class conversion (object): # applicableConversion
        monitoringPoint = models.ForeignKey(monintoring_point.MonitoringPoint, )
        # 		"title":"monitoringPoint",
        # 		"type":"string",
        # 		"format":"uri",
        # 		"required":true
        id = models.AutoField()
        # 			"title":"id",
		# 			"type":"string",
		# 			"required":true
        paramFrom = models.ForeignKey(parameter.parameter, )
        # 					"title":"paramFrom",
        # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
        # 				},
        paramTo = models.ForeignKey(parameter.parameter, )
        # 					"title":"paramTo",
        # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
     # def __init__(self, id, monitoringPoint, paramFrom, paramTo ):
     #    self.monitoringPoint =monitoringPoint
     #    # 		"title":"monitoringPoint",
     #    # 		"type":"string",
     #    # 		"format":"uri",
     #    # 		"required":true
     #    self.id = id
		# # 			"title":"id",
		# # 			"type":"string",
		# # 			"required":true
     #    self.paramFrom = paramFrom
     #    # 					"title":"paramFrom",
     #    # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
     #    # 				},
     #    self.paramTo = paramTo
     #    # 					"title":"paramTo",
     #    # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"

class conversionPeriod (object):

     periodStart = models.DateTimeField()
     periodEnd = models.DateTimeField()
     applicableConversion = models.ForeignKey(conversion, )

    # {
    # def __init__(self, applicableConversion,  periodStart,periodEnd=None,  ):
    #      self.periodStart = periodStart
    #      self.periodEnd = periodEnd
    #      self.applicableConversion = applicableConversion
    # # {
    #   "periodStart": "1998-07-27T00:00:00",
    #   "periodEnd": null,
    #   "applicableConversion": "http://waterml2.csiro.au/rgs-api/v1/conversion/419009-100.00-141-100/"
    # },

class table_point(object):

        fromValue=models.DecimalField()

        quality= models.URLField()

    #             "allowableValues": {
    #                 "defaultValue": null,
    #                 "readOnly": false,
    #                 "valueType": "RANGE",
    #             },
    #             "required": true,
    #             "type": "string"
        toValue = models.DecimalField()

#                 "allowableValues": {
#                     "defaultValue": null,
#                     "readOnly": false,
#                     "valueType": "RANGE",
#                 },
#                 "required": true,
#                 "type": "decimal"

#     def __init__(self, fromValue,  toValue,quality="http://www.kisters.com.au/hydstra/quality-codes/140",  ):
#         self.fromValue=fromValue
#
#         self.quality= quality
#
#     #             "allowableValues": {
#     #                 "defaultValue": null,
#     #                 "readOnly": false,
#     #                 "valueType": "RANGE",
#     #             },
#     #             "required": true,
#     #             "type": "string"
#         self.toValue = toValue
#
# #                 "allowableValues": {
# #                     "defaultValue": null,
# #                     "readOnly": false,
# #                     "valueType": "RANGE",
# #                 },
# #                 "required": true,
# #                 "type": "decimal"


class conversionSerializer (serializers.Serializer):
    monitoringPoint = CustomHyperlinkedField(
        view_name='monitoringpoint-detail',
        read_only=True,
        lookup_field='id',
        lookup_url_kwarg='pk',
        )
    id = serializers.CharField()
    paramFrom = ParameterSerializer()
    paramTo = ParameterSerializer()

    class Meta:
        model=conversion


class conversionGroupSerializer (serializers.Serializer):
    id = serializers.CharField()
    fullConversion = serializers.BooleanField()
    paramFrom = ParameterSerializer()
    paramTo = ParameterSerializer()
    conversionPeriods = conversionSerializer(many=True)
    class Meta:
        model=conversionGroup

class converionPeriodSerializer (object):
    periodStart = serializers.DateTimeField()
    periodEnd  = serializers.DateTimeField()
    applicableConversion = serializers.HyperlinkedIdentityField(view_name='MonitoringPointView',
        lookup_field='id',
        )
    # {
    #   "periodStart": "1998-07-27T00:00:00",
    #   "periodEnd": null,
    #   "applicableConversion": "http://waterml2.csiro.au/rgs-api/v1/conversion/419009-100.00-141-100/"
    # },
    class Meta:
        model=conversionPeriod
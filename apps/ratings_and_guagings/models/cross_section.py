__author__ = 'valentin'
from django.db import models

# {"id": "419009", "name": "Peel River At Tamworth", "shape": {
#     "type": "Point",
#     "coordinates": [150.9264, -31.0908]
# }, "cease_to_flow": "-0.25",
#     "control": "Gravel",
#     "verticalDatum": "AHD",
#     "conversiongroup_set": ["http://waterml2.csiro.au/rgs-api/v1/conversion-group/8/"],
#     "rangeGroups": []}

class MonitoringPoint(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    cease_to_flow = models.FloatField()
    control = models.CharField()
    verticalDatum = models.CharField()
# rangeGroups relationship
# conversionGroup relationship

class rangeGroups(models.Model):
    pass

class conversionGroup(models.Model):
    # by reference class
    pass

class Point(models.Model):
    id = models.AutoField(primary_key=True)
    monitoringPoint = models.ForeignKey('MonitoringPoint',to='location')
    coordinates = models.CharField();



    # <wmlrgs:period>
    #   <wmlrgs:ConversionPeriod>
    #     <wmlrgs:periodStart>
    #       <gml:TimeInstant gml:id="ti-1-371">
    #         <gml:timePosition>1998-07-27T00:00:00</gml:timePosition>
    #       </gml:TimeInstant>
    #     </wmlrgs:periodStart>
    #
    #     <wmlrgs:applicableConversion xlink:href="http://waterml2.csiro.au/rgs-api/v1/conversion/419009-100.00-141-100/"
    #       xlink:title="100.00 to 141"/>
    #   </wmlrgs:ConversionPeriod>
    # </wmlrgs:period>

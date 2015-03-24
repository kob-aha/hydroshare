__author__ = 'valentin'
# from django.conf import settings
# settings.configure()
from mock_django.query import QuerySetMock

from datetime import datetime
from ratings_and_guagings.models import parameter, monintoring_point, gauging, conversions, point

pnt1 = point.Point(34,-118)

mp1 = monintoring_point.MonitoringPoint(id="1",name="a",cease_to_flow='0',verticalDatum='WGS84', shape=pnt1         )

mpList1 = [ mp1 ]

ps1= parameter.parameter(id="ps1",description="ps1")
pe1= parameter.parameter(id="pe1",description="pe1")
g1= gauging.gauging(id="g1",featureOfInterest=mp1,phenomenonTime=datetime.now(),
                    observedPropertyFrom=ps1,observedPropertyTo=pe1,
                   fromValue=0,
                    toValue=1)
gaugingList1 = [g1]

c1 = conversions.conversion(id="c1", monitoringPoint=mp1, paramFrom=ps1,paramTo=pe1)

conversionList1 = [c1]


cg1= conversions.conversionGroup(id="cg1",monitoringPoint=mp1, fullConversion=True,paramFrom=ps1, paramTo=pe1,
                                 conversionPeriods=[c1])


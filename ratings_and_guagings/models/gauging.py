__author__ = 'valentin'


class guaging(object):
    def __init__(self, id, featureOfInterest, phenomenonTime, observedPropertyFrom, observedPropertyTo, fromValue, toValue, quality=None ):
        self.featureOfInterest = featureOfInterest
            # 	"title":"featureOfInterest",
            # 	"format":"uri",
            # 	"required":true
        self.id = id
        # 		"title":"id",
        # 		"required":true
        self.phenomenonTime = phenomenonTime
        # 					"title":"phenomenonTime",
        # 					"type":"string",
        # 					"required":true
        self.quality = quality
        # 					"title":"quality",
        # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
        self.observedPropertyFrom = observedPropertyFrom
        # 		"title":"observedPropertyFrom",
        # 		"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
        self.observedPropertyTo = observedPropertyTo
        # 					"title":"observedPropertyTo",
        # 					"$ref":"http://waterml2.csiro.au/part2/json/rgs-ie/Parameter.json"
        self.fromValue = fromValue
        # 					"title":"fromValue",
        # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
        # 					"required":true
        self.toValue = toValue
        # 					"title":"toValue",
        # 					"type":"http://shapechange.net/tmp/ows9/json/measure.json",
        # 					"required":true




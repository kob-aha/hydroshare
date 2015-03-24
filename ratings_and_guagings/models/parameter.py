__author__ = 'valentin'
from rest_framework import serializers

class parameter(object):
     def __init__(self, id, description, external_definition=None ):
        self.id = id
        self.description= description
        self.external_definition = external_definition

class ParamterSerialier(serializers.ModelSerializer):
    class Meta:
        model = parameter
        fields = ('id', 'description', 'external_definition')
__author__ = 'valentin'
from rest_framework import serializers

from django.db import models

class parameter(models.Model):
     id =  models.AutoField()
     description= models.TextField()
     external_definition = models.URLField()
     # def __init__(self, id, description, external_definition=None ):
     #    self.id = id
     #    self.description= description
     #    self.external_definition = external_definition
     # pass


class ParameterSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    description= serializers.CharField(max_length=255)
    external_definition =  serializers.CharField(max_length=255)
    class Meta:
        model=parameter


__author__ = 'valentin'
from rest_framework.reverse import reverse
from rest_framework import serializers


class CustomHyperlinkedField(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, queryset, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {self.lookup_field: lookup_value}
        return self.get_queryset().get(**lookup_kwargs)
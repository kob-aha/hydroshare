from django.db import models


class NetcdfTools(models.Model):
    short_id = models.CharField(max_length=50, unique=True)
    meta_edit_file = models.FileField(blank=True, null=True)
    data_subset_file = models.FileField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        super(NetcdfTools, self).delete(*args, **kwargs)
        fields = ['meta_edit_file', 'data_subset_file']
        for field in fields:
            if hasattr(self, field):
                field_obj = getattr(self, field)
                if field_obj:
                    storage, path = field_obj.storage, field_obj.path
                    storage.delete(path)
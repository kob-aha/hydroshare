from django.db import models


class NetcdfTools(models.Model):
    short_id = models.CharField(max_length=50, unique=True)
    meta_edit_file = models.FileField(blank=True)

    def delete(self, *args, **kwargs):
        super(NetcdfTools, self).delete(*args, **kwargs)
        if self.meta_edit_file:
            storage, path = self.meta_edit_file.storage, self.meta_edit_file.path
            storage.delete(path)
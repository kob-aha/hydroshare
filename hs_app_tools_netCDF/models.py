from django.db import models


class NetcdfTools(models.Model):
    short_id = models.CharField(max_length=50,unique=True)
    meta_edit_file = models.FileField(blank=True, max_length=1)
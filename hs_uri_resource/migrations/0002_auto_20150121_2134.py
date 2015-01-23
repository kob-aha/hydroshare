# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hs_uri_resource', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uriresource',
            name='link',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
    ]

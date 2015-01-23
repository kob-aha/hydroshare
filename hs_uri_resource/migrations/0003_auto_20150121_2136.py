# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hs_uri_resource', '0002_auto_20150121_2134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uriresource',
            name='link',
            field=models.URLField(default=b'None'),
            preserve_default=True,
        ),
    ]

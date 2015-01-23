# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hs_uri_resource', '0003_auto_20150121_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uriresource',
            name='link',
        ),
        migrations.AddField(
            model_name='uriresource',
            name='url_res_link',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hs_uri_resource', '0005_referenceuri'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uriresource',
            name='url_res_link',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('hs_uri_resource', '0004_auto_20150121_2140'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceUri',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('value', models.URLField(null=True)),
                ('content_type', models.ForeignKey(related_name='hs_uri_resource_referenceuri_related', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]

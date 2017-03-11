# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-11 23:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='latitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='person',
            name='longitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='person',
            name='state_name',
            field=models.CharField(default='', max_length=2),
        ),
        migrations.AddField(
            model_name='person',
            name='town_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='zip_code_cached',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='cached_zip_code',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='latitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='team',
            name='longitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='team',
            name='state_name',
            field=models.CharField(default='', max_length=2),
        ),
        migrations.AddField(
            model_name='team',
            name='town_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='looking_request_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='person',
            name='requested_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='person',
            name='update_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='person',
            name='username',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='team',
            name='looking_request_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='team',
            name='requested_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='team',
            name='update_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='team',
            name='username',
            field=models.CharField(default='', max_length=200),
        ),
    ]

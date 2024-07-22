# Generated by Django 4.2 on 2024-07-22 05:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shortURL', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='creDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='url',
            name='oriUrl',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='url',
            name='srtUrl',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
# Generated by Django 4.2 on 2024-07-29 02:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shortURL', '0003_url_srtstr_alter_url_srturl'),
    ]

    operations = [
        migrations.RenameField(
            model_name='url',
            old_name='creDate',
            new_name='create_date',
        ),
        migrations.RenameField(
            model_name='url',
            old_name='oriUrl',
            new_name='orign_url',
        ),
        migrations.RenameField(
            model_name='url',
            old_name='srtStr',
            new_name='short_string',
        ),
        migrations.RenameField(
            model_name='url',
            old_name='srtUrl',
            new_name='short_url',
        ),
    ]
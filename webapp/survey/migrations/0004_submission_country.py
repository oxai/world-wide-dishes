# Generated by Django 5.0.1 on 2024-02-11 10:06

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_submission_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='country',
            field=django_countries.fields.CountryField(default=None, max_length=746, multiple=True),
            preserve_default=False,
        ),
    ]
# Generated by Django 5.0.1 on 2024-03-06 09:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_remove_submission_acknowledgement_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='year_of_birth',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2006)], verbose_name='year of birth'),
        ),
    ]
# Generated by Django 5.0.1 on 2024-02-08 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_has_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='acknowledgement',
            field=models.BooleanField(default=False, verbose_name='acknowledgement'),
        ),
    ]
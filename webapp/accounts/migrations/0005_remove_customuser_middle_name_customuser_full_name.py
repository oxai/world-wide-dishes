# Generated by Django 5.0.1 on 2024-02-08 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_customuser_acknowledgement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='middle_name',
        ),
        migrations.AddField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='full name'),
        ),
    ]

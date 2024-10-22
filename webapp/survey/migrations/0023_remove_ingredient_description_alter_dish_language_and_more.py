# Generated by Django 5.0.1 on 2024-03-07 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0022_alter_dish_time_of_day_alter_dish_type_of_dish'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='description',
        ),
        migrations.AlterField(
            model_name='dish',
            name='language',
            field=models.CharField(max_length=200, verbose_name='What is the name of the local language?'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='local_name',
            field=models.CharField(max_length=200, verbose_name='What is the name of the dish in the local language?'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='name',
            field=models.CharField(max_length=200, verbose_name='What is the name of the dish in English?'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Name'),
        ),
    ]

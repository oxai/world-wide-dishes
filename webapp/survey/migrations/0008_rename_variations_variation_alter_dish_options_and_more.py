# Generated by Django 5.0.1 on 2024-02-12 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_ingredient_dishcategory_variations_dish'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Variations',
            new_name='Variation',
        ),
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name_plural': 'dishes'},
        ),
        migrations.AlterModelOptions(
            name='dishcategory',
            options={'verbose_name_plural': 'dish categories'},
        ),
        migrations.AlterField(
            model_name='dish',
            name='description',
            field=models.TextField(blank=True, max_length=500, verbose_name='description'),
        ),
    ]
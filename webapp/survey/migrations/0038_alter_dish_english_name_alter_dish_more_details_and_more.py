# Generated by Django 5.0.1 on 2024-03-23 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0037_alter_dish_ingredients_alter_dish_utensils_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='english_name',
            field=models.CharField(blank=True, help_text="You may leave this blank if the local name of the dish you've provided is in English and/or Roman alphabets. If you aren't sure about an English translation for the name, please write a phonetic approximation of how it is pronounced.", max_length=200, verbose_name='Is there an English name, or is there a phonetic approximation using Roman alphabets?'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='more_details',
            field=models.TextField(blank=True, max_length=600, verbose_name='More details'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='recipe',
            field=models.TextField(blank=True, help_text='If you have multiple URLs, please provide them in a new line.', max_length=400, verbose_name='Do you know of any online recipes for this? If so, please provide the URL.'),
        ),
    ]
# Generated by Django 5.0.1 on 2024-03-18 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0033_alter_dish_ingredients_alter_ingredient_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='image',
            field=models.ImageField(blank=True, upload_to='dishes/', verbose_name='Upload your food photo'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='ingredients',
            field=models.ManyToManyField(blank=True, help_text="Please select ingredients from the available options by starting typing. If any ingredients are missing from the list, please add them using the '+ add ingredients' button. A popup window will appear. This information can help us imagine what the dish looks like or try test an AI output.", to='survey.ingredient', verbose_name='Tell us more about the components, elements and / or ingredients of the dish'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='more_details',
            field=models.TextField(blank=True, help_text='Tell us what the dish looks like or tastes like, any fusion influences, its cultural importance, or anything else!', max_length=600, verbose_name='Anything we’ve missed about the dish that you want to tell us?'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='occasions_more',
            field=models.CharField(blank=True, max_length=200, verbose_name='If this dish is eaten on special occasions, please tell us the occasions.'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text="Please enter a name in singular form where possible. If there isn't a name for the ingredient in English, please feel free to add this in the local language.", max_length=200, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='national_identity',
            field=models.CharField(blank=True, help_text='Optional. Including this information helps us learn from you as well!', max_length=200, verbose_name="If we weren't able to capture your nationality in this list, please describe it below."),
        ),
    ]
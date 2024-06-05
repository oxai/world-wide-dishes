from django.contrib import admin
from .models import Submission, Ingredient, Dish, Country

for model in [Dish, Submission, Ingredient, Country]:
    admin.site.register(model)

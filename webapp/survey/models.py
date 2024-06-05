from datetime import timezone

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from main.settings import STATIC_URL

User = get_user_model()


class Country(models.Model):
    name = models.CharField(_("Name"), max_length=250)
    official_name = models.CharField(_("Official name"), max_length=250, blank=True, null=True)
    association = models.CharField(_("Association"), max_length=250, blank=True, null=True)
    code = models.CharField(_("Country code"), max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


class Submission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    year_of_birth = models.PositiveIntegerField(_("year of birth"), blank=True, null=True, validators=[MinValueValidator(1900), MaxValueValidator(2006)])
    countries = models.ManyToManyField(Country, blank=True)
    national_identity = models.CharField(_("If we weren't able to capture your nationality in this list, please describe it below."),
                                         help_text="Optional. Including this information helps us learn from you as well!", blank=True, max_length=200)
    over_aged = models.BooleanField(_("I confirm that I am or over 18 years old"), blank=False, null=True)

    @property
    def profile_filled(self):
        return self.year_of_birth is not None and self.countries.exists()

    def __str__(self):
        return f"Submission by {self.user}"


class Ingredient(models.Model):
    name = models.CharField(_("name"), help_text="Please enter a name in singular form where possible. If there isn't a name for the ingredient in English, please feel free to add this in the local language. Once this step is done, please re-enter this ingredient in the box on the main website.", max_length=200, unique=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="dishes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    english_name = models.CharField(_("English name"), max_length=200, blank=True)
    local_name = models.CharField(_("What is the name of the dish (in the local language)?"), max_length=200, blank=False, null=False)
    language = models.CharField(_("What is the name of the local language?"), max_length=200, blank=False, null=False)
    countries = models.ManyToManyField(Country, blank=True)
    countries_more = models.CharField(_("If we weren't able to capture all the countries you’d expect in this list, please add more below! (optional)"), max_length=200, blank=True)
    regions = models.TextField(_("Which regions in that country / countries does the dish come from, if you know?"), help_text="If you've selected multiple countries, please also indicate the corresponding country in brackets for each region.", max_length=500, blank=True)
    cultures = models.CharField(_("Is this dish attributed to a specific cultural, social, or ethnic group? If you know, could you list these below? "), max_length=200, blank=True)
    time_of_day = models.CharField(_("Time of day"), max_length=255, blank=False, null=False)
    time_of_day_more = models.CharField("", help_text="Please feel free to add any more information (optional)", max_length=200, blank=True)
    type_of_dish = models.CharField(_("Type of dish"), max_length=255, blank=False, null=False)
    type_of_dish_more = models.CharField("", help_text="Please feel free to add any more information (optional)", max_length=200, blank=True)
    ingredients = models.ManyToManyField(Ingredient, blank=False)
    ingredients_more = models.CharField("", help_text="Please feel free to add any ingredients that are missing from the above (optional)", max_length=200, blank=True)
    utensils = models.CharField(_("What utensils are used to eat this dish? "), help_text=_("For example, spoon; knife and fork; fingers; right hand; left hand; chopsticks"), max_length=200, blank=True)
    drink = models.CharField(_("Is it typically accompanied by a drink? What kind?"), max_length=200, blank=True)
    occasions = models.CharField(_("Is this dish eaten regularly, only on special occasions, or both?"), max_length=200, blank=False, null=False)
    occasions_more = models.CharField(_("If this dish is eaten on special occasions, please tell us the occasions."), max_length=200, blank=True)
    more_details = models.TextField(_("More details"), max_length=600, blank=True)
    recipe = models.TextField(_("Do you know of any online recipes for this? If so, please provide the URL."),
                              help_text=_("If you have multiple URLs, please provide them in a new line."), max_length=400, blank=True)
    image_url = models.URLField(_("Image URL"), null=True, blank=True)
    image = models.ImageField(_("Upload your food photo"), upload_to="dishes/", blank=True)
    image_details = models.TextField(_("Image details"), max_length=600, blank=True)

    def __str__(self):
        return self.local_name or self.english_name or "(No name provided)"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def readonly_image_url(self):
        return self.image_url or (self.image and self.image.url) or STATIC_URL + 'assets/img/dish_image_placeholder.svg'

    class Meta:
        verbose_name_plural = "dishes"


class DishRating(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_upvote = models.BooleanField(default=False, null=True)
    comment = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name_plural = "dish_ratings"
        unique_together = ('created_by', 'dish')

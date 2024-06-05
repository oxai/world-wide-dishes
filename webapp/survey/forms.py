from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Case, When, Value
from django.forms import CheckboxSelectMultiple
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2.forms import ModelSelect2MultipleWidget
from .models import Submission, Dish, Country, Ingredient

User = get_user_model()


class CountriesWidget(ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
        "official_name__icontains",
        # "association__icontains",
    ]

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        qs = super().filter_queryset(request, term, queryset, **dependent_fields)
        return qs.order_by(- Case(When(name__istartswith=term, then=Value(1)), default=Value(0)), "name")


class ProfileUpdateForm(forms.ModelForm):
    year_of_birth = forms.IntegerField(required=True, label=_("What year were you born?"), min_value=1900, max_value=2006,
                                       help_text=_("A 4 digit number between 1900 and 2006."))

    countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=CountriesWidget,
        required=True,
        label=_("Country (countries) you identify your nationality with"),
        help_text=_(
            "We encourage you to describe your nationality(ies) as you define them. The drop-down list might not adequately capture your preferred nationality name at all, in the case of border or sovereignty disputes. Please use the free text box to define yourself as you prefer."
        ),
    )

    over_aged = forms.BooleanField(
        required=True,
        label=_("I confirm that I am or over 18 years old"),
    )

    class Meta:
        model = Submission
        fields = ("year_of_birth", "over_aged", "countries", "national_identity")


class IngredientsWidget(ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        qs = super().filter_queryset(request, term, queryset, **dependent_fields)
        return qs.order_by(- Case(When(name__istartswith=term, then=Value(1)), default=Value(0)), "name")


TIME_OF_DAY_CHOICES = (
    ("breakfast", _("Breakfast")),
    ("lunch", _("Lunch")),
    ("dinner", _("Dinner")),
    ("snack", _("Snack")),
    ("anytime", _("Any time")),
    ("other", _("Other")),
)


TYPE_OF_DISH_CHOICES = (
    ("starter", _("Starter")),
    ("soup", _("Soup")),
    ("salad", _("Salad")),
    ("sauce", _("Sauce")),
    ("side_dish", _("Side dish")),
    ("main_stand_alone", _("Main dish - stand alone (e.g. one pot meal)")),
    ("main", _("Main dish - eaten with sides")),
    ("tapas", _("Small plate / bowl for sharing")),
    ("small_plate", _("Small plate / bowl served as a part of a collection")),
    ("dessert", _("Dessert")),
    ("other", _("Other")),
)


OCCASIONS_CHOICES = (
    ("regular", _("Regularly")),
    ("special", _("Only on special occasions")),
    ("both", _("Both")),
)


class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        print(name, value, attrs)
        if attrs.get('aria-invalid') == 'true':
            context["widget"]["form_valid"] = "is-invalid"
        elif value:
            context["widget"]["form_valid"] = "is-valid"
        else:
            context["widget"]["form_valid"] = ""
        return context


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name',)


class DishForm(forms.ModelForm):
    english_name = forms.CharField(
        label=_("Is there an English name, or is there a phonetic approximation using English letters?"),
        help_text=_(
            "You may leave this blank if the local name of the dish you've provided is in English alphabets. "
            "If you aren't sure about an English translation for the name, please write a phonetic approximation of how it is pronounced. "
            "For example, Falafel (فلافل), Ma-po-dou-fu (麻婆豆腐), Udon (うどん), Injera (እንጀራ), Lassi (लस्सी), Kimchi (김치), etc."
        ),
        max_length=200,
        required=False,
    )

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=AddAnotherWidgetWrapper(IngredientsWidget, reverse_lazy('survey:ingredient_create')),
        required=True,
        label=_("Tell us more about the components, elements and / or ingredients of the dish"),
        help_text=_(
            "Please select ingredients from the available options by starting to type at least two letters. If any ingredients are missing from the list, please add them using the '+ add ingredients' button. A popup window will appear. Please re-enter the ingredient in the box above once you are done. Please add the ingredients and/or components of the dish to help someone understand what this dish looks like, or help us test an AI image."
        ),
    )

    countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=CountriesWidget,
        required=True,
        label=_("Which country / countries does the dish come from, or which country do you associate the dish with?"),
        help_text=_(
            "You can select multiple countries if the dish is associated with more than one country."
        ),
    )

    time_of_day = forms.MultipleChoiceField(choices=TIME_OF_DAY_CHOICES, required=True, label=_("Is this dish typically eaten at a certain time of day?"), widget=MyCheckboxSelectMultiple)
    type_of_dish = forms.MultipleChoiceField(choices=TYPE_OF_DISH_CHOICES, required=True, label=_("How would you classify this dish?"), widget=MyCheckboxSelectMultiple)
    occasions = forms.ChoiceField(choices=OCCASIONS_CHOICES, required=True, label=_("Is this dish eaten regularly, only on special occasions, or both?"), widget=forms.RadioSelect)

    class Meta:
        model = Dish
        fields = (
        'local_name', 'english_name', 'language', 'countries', 'countries_more', 'regions', 'cultures',
        'time_of_day', 'time_of_day_more', 'type_of_dish', 'type_of_dish_more',
        'ingredients', 'utensils', 'drink', 'occasions', 'occasions_more')
        widgets = {
                'regions': forms.Textarea(attrs={'rows': 1}),
        }


class DishFormPhoto(forms.ModelForm):
    image_details = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    class Meta:
        model = Dish
        fields = ('image', 'image_details')


class DishFormExtra(forms.ModelForm):
    more_details = forms.CharField(
        label=_("Would you like to tell us anything else about the dish?"),
        help_text=_(
            "Tell us what the dish looks like or tastes like, or if you know of any fusion influences. Perhaps you’d like to share more about its historical significance or cultural importance. You are free to tell us as much as you would like!"
        ),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    image_details = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )


    class Meta:
        model = Dish
        fields = ('image_url', 'image_details', 'recipe', 'more_details')
        widgets = {
            'image_url': forms.URLInput(attrs={'placeholder': 'http://example.com/image.jpg'}),
            'image_details': forms.Textarea(attrs={'rows': 3}),
            'recipe': forms.Textarea(attrs={'rows': 2}),
        }

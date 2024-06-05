from typing import Any

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import CharField, BooleanField
from django.utils.translation import gettext_lazy as _
from django_countries import widgets
from django_countries.fields import CountryField, LazyTypedMultipleChoiceField, LazyChoicesMixin
from django_countries.widgets import CountrySelectWidget, LazySelectMultiple


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    full_name = CharField(
        required=True,
        label=_("Full name"),
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_(
            "Your password must contain at least 8 characters."
        ),
    )

    password2 = None

    acknowledgement = BooleanField(
        required=False,
        label=_("I would like to have my name shared in any acknowledgements of publications and online research outputs."),
        help_text=_(
            "This is our way of saying thank you for your valuable contributions!"
        ),
    )

    followup_consent = BooleanField(
        required=False,
        label=_("I am open to being contacted in relation to my answers on this form."),
        help_text=_(
            "For example, if any of my answers are unclear or if the researchers have follow-up questions about my answers."
        ),
    )

    future_contact = BooleanField(
        required=False,
        label=_("I am open to being contacted by the researchers in relation to future additional questions on this topic. "),
        help_text=_(
            ""
        ),
    )

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password1")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password1", error)

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "acknowledgement", "followup_consent", "future_contact")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)


class SelectMultipleCountries(LazyChoicesMixin, forms.TypedMultipleChoiceField):
    """
    A form TypedMultipleChoiceField that respects choices being a lazy object.
    """

    choices: Any
    widget = forms.CheckboxSelectMultiple


AGE_CHOICES = (
    ("", "Select age group"),
    # ("0-10", "0-10"),
    ("11-20", "11-20"),
    ("21-30", "21-30"),
    ("31-40", "31-40"),
    ("41-50", "41-50"),
    ("51-60", "51-60"),
    ("61-70", "61-70"),
    ("71-80", "71-80"),
    ("81-90", "81-90"),
    ("91-100", "91-100")
)


class ProfileUpdateForm(forms.ModelForm):
    full_name = CharField(
        required=False,
        label=_("Full name"),
        help_text=_(
            "Optional. Please include if you want to be mentioned in the acknowledgements (spelt in English)."
        ),
    )

    acknowledgement = BooleanField(
        required=False,
        label=_("I would like to have my name shared in any acknowledgements of publications and online research outputs."),
        help_text=_(
            "This is our way of saying thank you for your valuable contributions!"
        ),
    )

    followup_consent = BooleanField(
        required=False,
        label=_("I am open to being contacted in relation to my answers on this form."),
        help_text=_(
            "For example, if any of my answers are unclear or if the researchers have follow-up questions about my answers."
        ),
    )

    future_contact = BooleanField(
        required=False,
        label=_("I am open to being contacted by the researchers in relation to future additional questions on this topic. "),
        help_text=_(
            ""
        ),
    )

    class Meta:
        model = User
        fields = ("full_name", "acknowledgement", "followup_consent", "future_contact")
import random

from django.contrib.auth.forms import UserCreationForm
from django.urls import path
from django.shortcuts import render


def home(request):
    members = [
            # {"name": "", "img": ""},
        ]
    random.shuffle(members)
    return render(request, "pages/home.html", context={"members": members})


def faq(request):
    context = {
        "timeline": [
            {"date": "March 2024", "text": "The survey is open for data collection."},
            {"date": "20th April 2024", "text": 'You can withdraw the submitted personal identifiable information, as well as your information about food. '
                                               'Simply navigate to your profile page, scroll down, and click "delete account and data"'},
            {"date": "1st May 2024", "text": "You will not able to withdraw names from the publication, but it possible to withdraw it from our database."},
            {"date": "Once the study closes (30 May 2024)", "text": "You will be able to withdraw personal identifiable information (name, email) by sending us an email."},
            {"date": "3 years from completion (May 2027)", "text": "All your data not currently in public domain will be deleted at this point."},
        ]
    }
    return render(request, "pages/faq.html", context=context)


def path_to_page_view(name, url_path=None):
    if url_path is None:
        url_path = name + '/'
    return path(url_path, lambda request: render(request, f'pages/{name}.html'), name=name)

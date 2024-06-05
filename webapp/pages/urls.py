from django.urls import path

from .views import home, path_to_page_view, faq

app_name = "pages"
urlpatterns = [
    path("", home, name="home"),
    path("faq/", faq, name="faq"),
    path_to_page_view("contact"),
    path_to_page_view("data_protection"),
]

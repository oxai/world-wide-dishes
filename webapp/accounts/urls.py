from django.urls import path

from .views import signup, profile, delete_user, export_csv

app_name = "accounts"
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('delete/', delete_user, name='delete_user'),
    path('profile/', profile, name='profile'),
    path('export/', export_csv, name='export_csv')
]

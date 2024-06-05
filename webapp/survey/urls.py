from django.urls import path

from accounts.views import signup
from .views import path_to_page_view, profile, account, DishListView, DishCreateView, \
    DishExtraUpdateView, \
    DishUpdateDetailsView, ReviewDishesListView, delete_dish, rate_dish, comment_dish, dishes_view, IngredientCreateView, \
    LeaderboardView, weekly_dishes_view, country_dishes_view, get_country_details, DishUpdatePhotoView, CountryDetailView

app_name = "survey"
urlpatterns = [
    path_to_page_view("home", ""),
    path('account/', account, name='account'),
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    path('dish/create/', DishCreateView.as_view(), name='dish_create'),
    path('ingredient/create/', IngredientCreateView.as_view(), name='ingredient_create'),
    path('dish/<int:pk>/update/', DishUpdatePhotoView.as_view(), name='dish_update'),
    path('dish/<int:pk>/details/', DishUpdateDetailsView.as_view(), name='dish_update_details'),
    path('dish/<int:pk>/extra/', DishExtraUpdateView.as_view(), name='dish_extra_update'),
    path('dish/', DishListView.as_view(), name='dish_list'),
    path('delete-dish/<int:dish_id>/', delete_dish, name='dish_delete'),
    path('review', ReviewDishesListView.as_view(), name="dish_review"),
    path('vote/', rate_dish, name='rate_dish'),
    path('comment/', comment_dish, name='comment_dish'),
    path('leaderboard', LeaderboardView.as_view(), name='leaderboard'),
    path('daily-content', dishes_view, name='daily_content'),
    path('weekly_dishes', weekly_dishes_view, name='weekly_dishes'),
    path('country_dishes', country_dishes_view, name='country_dishes'),
    path('get-country-details', get_country_details, name='get-country-details'),
    path('country/<int:country_id>/', CountryDetailView.as_view(), name='country_details'),
    path_to_page_view("thank_you", context={"progress": 3}),
    path_to_page_view("thank_you_no_consent", "no_consent/"),
]

import datetime
from django.core.paginator import Paginator
from django.urls import path, reverse, reverse_lazy
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView
from django_addanother.views import CreatePopupMixin
from guest_user.decorators import allow_guest_user
from guest_user.functions import is_guest_user
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import logging
import ast
import json
from django.db.models import Count, Q, OuterRef, Subquery
from .forms import ProfileUpdateForm, DishForm, DishFormExtra, IngredientForm, DishFormPhoto
from .models import Dish, DishRating, Ingredient, Country
from django.core.cache import cache

logger = logging.getLogger('dish_logger')


def path_to_page_view(name, url_path=None, **kwargs):
    if url_path is None:
        url_path = name + '/'
    return path(url_path, lambda request: render(request, f'survey/{name}.html', **kwargs), name=name)


def account(request):
    if request.user.is_authenticated and not is_guest_user(request.user):
        return redirect('survey:profile')
    return render(request, f'survey/account.html')


@allow_guest_user
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.submission)
        if form.is_valid():
            form.save()
            return redirect('survey:dish_list')  # Redirect back to profile page
    else:
        form = ProfileUpdateForm(instance=request.user.submission)
    # breadcrumbs = [('Profile', 'survey:profile')]
    return render(request, 'survey/profile.html', {'form': form, 'progress': 1})


@require_POST
def delete_dish(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    if not dish.is_deleted():
        dish.soft_delete()
    else:
        return redirect('survey:dish_list')
    return redirect('survey:dish_list')


class IngredientCreateView(CreatePopupMixin, CreateView):
    model = Ingredient
    context_object_name = "ingredient"
    template_name = "survey/ingredient_form.html"
    form_class = IngredientForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.cleaned_data['name'] = form.cleaned_data['name'].lower().strip()
        self.object = form.save()
        return HttpResponse('<script type="text/javascript">window.close()</script>')


class RestrictedFormViewMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('survey:home'))
        if not request.user.submission.profile_filled:
            return HttpResponseRedirect(reverse('survey:profile'))

        return super().dispatch(request, *args, **kwargs)


class DishCreateView(RestrictedFormViewMixin, CreateView):
    model = Dish
    context_object_name = "dish"
    template_name = "survey/dish_form_image.html"
    form_class = DishFormPhoto

    # Overide to save dish with current user
    def form_valid(self, form):
        # Assign current user as creator of dish
        form.instance.created_by = self.request.user
        return super(DishCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('survey:dish_update_details', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 2}


class DishUpdatePhotoView(RestrictedFormViewMixin, UpdateView):
    model = Dish
    context_object_name = "dish"
    template_name = "survey/dish_form_image.html"
    form_class = DishFormPhoto

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user, deleted_at__isnull=True)

    def get_success_url(self, **kwargs):
        # Ensure you have imported reverse_lazy at the top
        return reverse_lazy('survey:dish_update_details', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 2}


class DishUpdateDetailsView(RestrictedFormViewMixin, UpdateView):
    model = Dish
    context_object_name = "dish"
    template_name = "survey/dish_form.html"
    form_class = DishForm

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super().get_form_kwargs()

        # Safely evaluate the 'time_of_day' field's string list to a Python list
        if self.object.time_of_day:
            try:
                time_of_day_initial = ast.literal_eval(self.object.time_of_day)
                type_of_dish = ast.literal_eval(self.object.type_of_dish)
            except (ValueError, SyntaxError):
                # Handle the error or set to a default empty list if the string is malformed
                time_of_day_initial = []
                type_of_dish = []
        else:
            time_of_day_initial = []
            type_of_dish = []

        # Update the 'initial' dict in kwargs with the converted list
        kwargs['initial']['time_of_day'] = time_of_day_initial
        kwargs['initial']['type_of_dish'] = type_of_dish
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user, deleted_at__isnull=True)

    def get_success_url(self, **kwargs):
        # Ensure you have imported reverse_lazy at the top
        return reverse_lazy('survey:dish_extra_update', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 2}


class DishExtraUpdateView(RestrictedFormViewMixin, UpdateView):
    model = Dish
    context_object_name = "dish"
    template_name = "survey/dish_form_extra.html"
    form_class = DishFormExtra
    success_url = reverse_lazy("survey:dish_list")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user, deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 2}


class DishListView(RestrictedFormViewMixin, ListView):
    model = Dish
    template_name = "survey/dish_list.html"
    context_object_name = "dishes"

    def get_queryset(self):
        dishes_list = Dish.objects.filter(created_by=self.request.user, deleted_at__isnull=True,
                                          local_name__isnull=False, local_name__gt='').order_by('-updated_at')
        return dishes_list

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 2}


class ReviewDishesListView(RestrictedFormViewMixin, ListView):
    model = Dish
    template_name = "survey/dish_review.html"
    context_object_name = "dishes"

    def get_queryset(self):
        current_user = self.request.user
        user_dishes = Dish.objects.filter(created_by=current_user)
        user_countries_ids = user_dishes.values_list('countries', flat=True).distinct()

        ratings_subquery = DishRating.objects.filter(
            created_by=current_user,
            dish=OuterRef('pk')
        ).values('is_upvote')[:1]

        comment_subquery = DishRating.objects.filter(
            created_by=current_user,
            dish=OuterRef('pk')
        ).values('comment')[:1]

        dishes_to_review = (Dish.objects.filter(countries__in=user_countries_ids, deleted_at__isnull=True,
                                                local_name__isnull=False, local_name__gt='')
                            .exclude(created_by=current_user)
                            .order_by('-updated_at')
                            .annotate(user_upvote=Subquery(ratings_subquery))
                            .annotate(user_comment=Subquery(comment_subquery))
                            .distinct())
        return dishes_to_review

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "progress": 3}


class LeaderboardView(ListView):
    model = Dish
    template_name = "survey/leaderboard.html"
    context_object_name = "dishes"


class CountryDetailView(ListView):
    model = Dish
    template_name = "survey/country_details.html"
    context_object_name = "dishes"
    paginate_by = 5

    def get_queryset(self):
        # Retrieve the country id
        country_id = self.kwargs.get("country_id")

        if country_id:
            query_set = Dish.objects.filter(countries__id=country_id, deleted_at__isnull=True,
                                            local_name__isnull=False, local_name__gt='').order_by('-updated_at')
        else:
            query_set = Dish.objects.none()

        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Retrieve the country object based on the country_id
        country_id = self.kwargs.get("country_id")
        country = Country.objects.filter(id=country_id).first()

        context['page_obj'] = page_obj
        context['country'] = country
        return context


@require_POST
def rate_dish(request):
    data = json.loads(request.body)
    dish_id = data.get('dish_id')
    vote_type = data.get('vote_type')

    dish_rating, created = DishRating.objects.get_or_create(dish_id=dish_id, created_by=request.user)
    if vote_type == 'upvote':
        dish_rating.is_upvote = True
    elif vote_type == 'downvote':
        dish_rating.is_upvote = False
    dish_rating.save()

    return JsonResponse({"success": True, "message": "Vote recorded"})


def dishes_view(request):
    # Get the current date in a timezone-aware format
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_dishes = (Dish.objects.filter(created_at__gte=today_start, deleted_at__isnull=True,
                                         local_name__isnull=False, local_name__gt='')
                     .order_by('-updated_at'))
    # Set up pagination
    paginator = Paginator(todays_dishes, 5)  # Show 10 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object to the context
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'survey/today_dishes.html', context)


def weekly_dishes_view(request):
    one_week_ago = timezone.now() - datetime.timedelta(days=30)
    past_week_dishes = (Dish.objects.filter(created_at__gte=one_week_ago, local_name__isnull=False, local_name__gt='')
                        .order_by('-updated_at'))
    # Set up pagination
    paginator = Paginator(past_week_dishes, 5)  # Show 10 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object to the context
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'survey/weekly_dishes.html', context)


def get_country_dish_stats():
    countries_dishes = Country.objects.annotate(
        num_dishes=Count('dish', filter=Q(dish__deleted_at__isnull=True)),
        num_contributors=Count('dish__created_by', filter=Q(dish__deleted_at__isnull=True), distinct=True)
    ).order_by('-num_dishes', 'name')

    # Prepare the data for ranking and HTML display
    ranked_countries = [
        {
            "rank": idx + 1,
            "id": country.id,
            "name": country.name,
            "code": country.code,
            "num_dishes": country.num_dishes,
            "num_contributors": country.num_contributors
        }
        for idx, country in enumerate(countries_dishes)
    ]

    return ranked_countries


def country_dishes_view(request):
    # Fetch from cache if already exists
    countries = cache.get('all_countries')

    # If cache miss, query the database and cache the result
    if countries is None:
        countries = Country.objects.all().order_by('name')
        cache.set('all_countries', countries, 3600)  # Cache for 1 hour

    ranked_countries = get_country_dish_stats()
    # Set up pagination
    paginator = Paginator(ranked_countries, 50)  # Show 10 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Pass the page object to the context
    context = {
        'countries': countries,
        'page_obj': page_obj,
    }
    return render(request, 'survey/country_dishes.html', context)


@require_POST
def comment_dish(request):
    data = json.loads(request.body)
    dish_id = data.get('dish_id')
    # Logic to create or update DishRating here
    dish_rating, created = DishRating.objects.get_or_create(dish_id=dish_id, created_by=request.user)
    dish_rating.comment = data.get('comment')
    dish_rating.save()

    return JsonResponse({"success": True, "message": "Vote recorded"})


def get_country_details(request):
    country_id = request.GET.get('country_id')
    countries_dishes = Country.objects.filter(id=country_id).annotate(
        num_dishes=Count('dish', filter=Q(dish__deleted_at__isnull=True)),
        num_contributors=Count('dish__created_by', filter=Q(dish__deleted_at__isnull=True), distinct=True)
    ).order_by('-num_dishes')

    # Prepare the data for ranking and HTML display
    country = [
        {
            "rank": idx + 1,
            "id": country.id,
            "name": country.name,
            "code": country.code,
            "num_dishes": country.num_dishes,
            "num_contributors": country.num_contributors,
            "detailUrl": reverse('survey:country_details', args=[country.id]),
        }
        for idx, country in enumerate(countries_dishes)
    ]

    return JsonResponse({'status': 'success', 'country': country})

import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from guest_user.functions import is_guest_user

from survey.models import Dish
from .forms import CustomUserCreationForm, ProfileUpdateForm


# Create your views here.
def signup(request):
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, "pages:home"))
    if request.user.is_authenticated and not is_guest_user(request.user):
        return redirect(redirect_to)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If the user is a guest user, we need to transfer the submission to the new user
            if is_guest_user(request.user):
                old_user = request.user
                submission = user.submission
                submission.delete()
                old_user.submission.user = user
                old_user.submission.save()
                old_user.delete()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(redirect_to)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# Update it here
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('accounts:profile')  # Redirect back to profile page
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect("pages:home")


@login_required
def export_csv(request):
    # check if the user is staff
    if not request.user.is_staff:
        # if not staff, return django exception
        return HttpResponse(status=403)
    # Create the HttpResponse object with the appropriate CSV header.

    datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="WWD_dishes_export_{datetime_str}.csv"'},
    )

    # get all the dishes
    dishes = Dish.objects.filter(~Q(local_name="") & Q(deleted_at=None))

    fields = ('id',
              'local_name', 'english_name', 'language', 'countries', 'countries_more', 'regions', 'cultures',
              'image', 'image_url', 'image_details',
              'time_of_day', 'time_of_day_more', 'type_of_dish', 'type_of_dish_more',
              'ingredients', 'utensils', 'drink', 'occasions', 'occasions_more',
              'more_details', 'recipe', 'created_at', 'updated_at')

    model_fields = {field.name: field for field in Dish._meta.fields + Dish._meta.many_to_many}

    writer = csv.writer(response, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(fields)

    for dish in dishes:
        row = []
        for field in fields:
            if not model_fields[field].many_to_many:
                value = getattr(dish, field)
                if callable(value):
                    try:
                        value = value()  # if it's a method, call it
                    except:
                        value = None
                row.append(value)
            else:  # handle many-to-many fields
                m2m_value = ', '.join([str(item) for item in getattr(dish, field).all()])
                row.append(m2m_value)

        writer.writerow(row)

    return response

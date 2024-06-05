from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from survey.models import Submission
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class SubmissionInline(admin.TabularInline):
    model = Submission


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active", "is_guest", "submission")
    list_filter = ("email", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    inlines = [SubmissionInline]
    actions = ("mark_staff", "unmark_staff")

    @admin.action(description='Mark as staff')
    def mark_staff(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_staff = True
            obj.save()

    @admin.action(description='Unmark as staff')
    def unmark_staff(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_staff = False
            obj.save()


admin.site.register(CustomUser, CustomUserAdmin)

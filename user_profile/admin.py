from django.contrib import admin
from .models import UserProfile
# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'registration_no', 'course', 'current_year', 'ms_teams_id')


admin.site.register(UserProfile, UserProfileAdmin)

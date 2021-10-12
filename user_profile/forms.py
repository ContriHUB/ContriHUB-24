from django import forms

from .models import UserProfile


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('registration_no', 'course', 'current_year', 'ms_teams_id')

class EditProfileForm(forms.ModelForm):

    class Meta:
        model=UserProfile
        fields=('registration_no','course','current_year')
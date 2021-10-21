from django import forms
from .models import UserProfile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class UserProfileForm(forms.ModelForm):
    whats_app_no = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(initial='IN')
    )

    class Meta:
        model = UserProfile
        fields = ('registration_no', 'course', 'current_year', 'ms_teams_id', 'whats_app_no')


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('registration_no', 'course', 'current_year')


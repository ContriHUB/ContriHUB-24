from django import forms
from .models import UserProfile
from project.models import Issue
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class UserProfileForm(forms.ModelForm):
    whatsapp_no = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(initial='IN')
    )
    class Meta:
        model = UserProfile
        fields = ('registration_no', 'course', 'current_year', 'ms_teams_id','whatsapp_no')

class EditProfileForm(forms.ModelForm):

    class Meta:
        model=UserProfile
        fields=('registration_no','course','current_year')


class CreateIssueForm(forms.ModelForm):

    class Meta:
        model = Issue
        fields = ('title','description','mentor','project','level','points','is_restricted')

from django import forms
from .models import PullRequest


class PRSubmissionForm(forms.ModelForm):

    class Meta:
        model = PullRequest
        fields = ('html_url',)

from django import forms
from .models import PullRequest


class PRSubmissionForm(forms.ModelForm):

    class Meta:
        model = PullRequest
        fields = ('pr_link',)

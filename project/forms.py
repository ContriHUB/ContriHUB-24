from django import forms
from .models import PullRequest, Issue


class PRSubmissionForm(forms.ModelForm):
    class Meta:
        model = PullRequest
        fields = ('pr_link',)


class CreateIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ('title', 'description', 'mentor', 'project', 'level', 'points', 'is_restricted')

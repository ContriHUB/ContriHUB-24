from django import forms


class PRSubmissionForm(forms.Form):

    pr_html_url = forms.URLField(required=True, widget=forms.TextInput(attrs={'required': 'true'}))

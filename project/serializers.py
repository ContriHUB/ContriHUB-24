from rest_framework import serializers
from .models import Project, Issue, PullRequest


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'


class PullRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PullRequest
        fields = '__all__'

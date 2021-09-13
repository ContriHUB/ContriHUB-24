from django.contrib import admin
from .models import Project, Issue, PullRequest


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url', 'html_url')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'mentor', 'level', 'points', 'state', 'assignee')


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('html_url', 'user', 'issue', 'state')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(PullRequest, PullRequestAdmin)

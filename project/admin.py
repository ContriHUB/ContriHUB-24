from django.contrib import admin
from .models import Project, Issue, PullRequest, IssueAssignmentRequest, ActiveIssue


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url', 'html_url')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'mentor', 'level', 'points', 'state')


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'html_url', 'state', 'bonus', 'penalty')


class IssueAssignmentRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'issue', 'state')


class ActiveIssueAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'issue', 'assigned_at')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(IssueAssignmentRequest, IssueAssignmentRequestAdmin)
admin.site.register(ActiveIssue, ActiveIssueAdmin)

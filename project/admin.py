from django.contrib import admin
from .models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'html_url')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'project', 'mentor', 'level', 'points', 'state')


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'pr_link', 'state', 'bonus', 'penalty', 'submitted_at')


class IssueAssignmentRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'issue', 'state')


class ActiveIssueAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'issue', 'assigned_at')


class LikesAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user')

class DislikesAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user')

    
admin.site.register(Likes, LikesAdmin)
admin.site.register(Dislikes, DislikesAdmin)
admin.site.register(Project, ProjectAdmin)

admin.site.register(Issue, IssueAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(IssueAssignmentRequest, IssueAssignmentRequestAdmin)
admin.site.register(ActiveIssue, ActiveIssueAdmin)
admin.site.register(Domain)
admin.site.register(SubDomain)

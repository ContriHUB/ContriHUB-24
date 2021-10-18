from django.contrib import admin
from django.contrib.admin import display

from .models import Project, Issue, PullRequest, IssueAssignmentRequest, ActiveIssue


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domain','subdomain1','subdomain2','subdomain3','html_url')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'project', 'mentor', 'level', 'points', 'state', 'get_upvotes_cnt', 'get_downvotes_cnt')

    @display(ordering='issue__upvotes', description='Count of Upvotes')
    def get_upvotes_cnt(self, obj):
        return obj.upvotes.all().count()


    @display(ordering='issue__downvotes', description='Count of Downvotes')
    def get_downvotes_cnt(self, obj):
        return obj.downvotes.all().count()


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'contributor', 'get_id', 'issue', 'get_project_name', 'pr_link', 'state', 'bonus', 'penalty', 'submitted_at')

    @display(ordering='issue__id', description='Issue_ki_id')
    def get_id(self, obj):
        return obj.issue.id

    @display(ordering='issue__project', description='Project_ka_naam')
    def get_project_name(self, obj):
        return obj.issue.project


class IssueAssignmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'issue', 'state', 'get_id', 'get_project_name', 'created_on')

    @display(ordering='issue__id', description='Issue_ki_id')
    def get_id(self, obj):
        return obj.issue.id

    @display(ordering='issue__project', description='Project_ka_naam')
    def get_project_name(self, obj):
        return obj.issue.project


class ActiveIssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'contributor', 'issue', 'assigned_at', 'get_id', 'get_project_name')

    @display(ordering='issue__id', description='Issue_ki_id')
    def get_id(self, obj):
        return obj.issue.id

    @display(ordering='issue__project', description='Project_ka_naam')
    def get_project_name(self, obj):
        return obj.issue.project


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(IssueAssignmentRequest, IssueAssignmentRequestAdmin)
admin.site.register(ActiveIssue, ActiveIssueAdmin)

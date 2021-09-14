from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse, Http404
from project.models import Project, Issue, IssueAssignmentRequest, ActiveIssue, PullRequest
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from helper import complete_profile_required
from .forms import PRSubmissionForm


@complete_profile_required
def home(request):
    project_qs = Project.objects.all()
    issues_qs = Issue.objects.all()
    context = {
        'projects': project_qs,
        'issues': issues_qs
    }
    return render(request, 'home/index.html', context=context)


def authorize(request):
    """
    Used for rendering authorize.html which is responsible for both LogIn and SignUp
    :param request:
    :return:
    """
    return render(request, 'home/authorize.html', {})


def logout_(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
@complete_profile_required
def request_issue_assignment(request, issue_pk):
    issue = Issue.objects.get(pk=issue_pk)
    requester = request.user

    is_already_requested = IssueAssignmentRequest.objects.filter(issue=issue, requester=requester)

    if is_already_requested:
        message = f"{requester.userprofile} Hold your horses! You have already requested for assignment of Issue " \
                  f"<a href={issue.html_url}>#{issue.number}</a> of <a href={issue.project.html_url}>{issue.project.name}</a>"
        raise Http404(message)

    if issue.is_assignable(requester=requester):
        IssueAssignmentRequest.objects.create(issue=issue, requester=requester)
        message = f"Assignment Request for Issue <a href={issue.html_url}>#{issue.number}</a> of " \
                  f"<a href={issue.project.html_url}>{issue.project.name}</a> submitted successfully. "
        return HttpResponse(message)

    message = f"Issue <a href={issue.html_url}>#{issue.number}</a> of <a href={issue.project.html_url}>" \
              f"{issue.project.name}</a> cannot be assigned to you."
    raise Http404(message)


@login_required
def accept_issue_request(request, issue_req_pk):
    user = request.user
    issue_request = IssueAssignmentRequest.objects.get(pk=issue_req_pk)
    issue = issue_request.issue
    requester = issue_request.requester
    if issue_request.is_acceptable(mentor=user):
        ActiveIssue.objects.create(issue=issue, contributor=requester)
        issue_request.state = IssueAssignmentRequest.ACCEPTED
        issue_request.save()
        # TODO:ISSUE Send Email to Student that their request is accepted
        message = f"Issue <a href={issue.html_url}>#{issue.number}</a> of Project <a href={issue.project.html_url}>" \
                  f"{issue.project.name}</a> successfully assigned to {requester}"
        return HttpResponse(message)
    else:
        message = f"This Issue Cannot be accepted by you!"
        raise Http404(message)


def reject_issue_request():
    pass  # TODO: ISSUE: Implement Reject Issue Request


@login_required
@complete_profile_required
def submit_pr_request(request, active_issue_pk):
    if request.method == 'GET':
        contributor = request.user
        active_issue_qs = ActiveIssue.objects.filter(pk=active_issue_pk, contributor=contributor)
        if active_issue_qs:
            form = PRSubmissionForm(request.GET)
            active_issue = active_issue_qs[0]
            issue = active_issue.issue
            if active_issue.can_raise_pr(contributor=contributor) and form.is_valid():
                pr_html_url = form.cleaned_data.get('pr_html_url')
                PullRequest.objects.create(html_url=pr_html_url, issue=issue, contributor=request.user)
                # TODO:ISSUE Create Check on URL in backend so that it is a Valid Github PR URL.

                # TODO: Send Email to Mentor

                message = f"PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                return HttpResponse(message)

    message = f"This request cannot be full-filled."
    raise Http404(message)
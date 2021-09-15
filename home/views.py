from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse, Http404
from project.models import Project, Issue, IssueAssignmentRequest, ActiveIssue, PullRequest
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from helper import complete_profile_required
from project.forms import PRSubmissionForm
from django.utils import timezone


# TODO:ISSUE: Replace each HttpResponse with a HTML page
# TODO:ISSUE: Create a URL to view each Issue on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each PR on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each Issue Assignment Request on a separate Page with all its information.
# TODO:ISSUE: Make a Custom Http404 Page


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

    if issue.is_assignable(requester=requester):
        IssueAssignmentRequest.objects.create(issue=issue, requester=requester)
        message = f"Assignment Request for Issue <a href={issue.html_url}>#{issue.number}</a> of " \
                  f"<a href={issue.project.html_url}>{issue.project.name}</a> submitted successfully. "
        return HttpResponse(message)

    message = f"Assignment Request for <a href={issue.html_url}>Issue #{issue.number}</a> of <a href={issue.project.html_url}>" \
              f"{issue.project.name}</a> cannot be made by you currently."
    return HttpResponse(message)


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
        message = f"This Issue Cannot be accepted by you! Probably it's already Accepted/Rejected."
        return HttpResponse(message)


def reject_issue_request():
    pass  # TODO: ISSUE: Implement Reject Issue Request


@login_required
@complete_profile_required
def submit_pr_request(request, active_issue_pk):
    if request.method == 'GET':
        contributor = request.user
        active_issue_qs = ActiveIssue.objects.filter(pk=active_issue_pk, contributor=contributor)
        if active_issue_qs:
            active_issue = active_issue_qs[0]
            issue = active_issue.issue
            pr_qs = PullRequest.objects.filter(issue_id=issue.pk, contributor=contributor)
            if pr_qs:
                # If resubmitting PR request for Active Issue
                form = PRSubmissionForm(request.GET, instance=pr_qs.first())
            else:
                form = PRSubmissionForm(request.GET)

            if active_issue.can_raise_pr(contributor=contributor) and form.is_valid():
                pr = form.save(commit=False)
                pr.issue = issue
                pr.contributor = request.user
                pr.state = PullRequest.PENDING_VERIFICATION
                pr.submitted_at = timezone.now()
                pr.save()
                # TODO:ISSUE Create Check on URL in backend so that it is a Valid Github PR URL.

                # TODO: Send Email to Mentor

                message = f"PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                return HttpResponse(message)
            else:
                message = f"This request cannot be full-filled. Probably you already submitted PR verification request " \
                          f"for <a href={issue.html_url}>Issue #{issue.number}</a> of Project <a href=" \
                          f"{issue.project.html_url}>{issue.project.name}</a>"
            return HttpResponse(message)

    message = "This request cannot be full-filled."
    return HttpResponse(message)


# TODO:ISSUE: Implement Functionality for mentor to assign bonus/peanlty points while accepting/rejecting the issue.A form will be needed.

# TODO:ISSUE: Send an Email to Contributor Notifying that their PR is accepted/rejected.

# TODO:ISSUE: Implement a feature such that mentor is able to leave remarks about PR before Accepting/Rejecting (Some fields in Model need to be added/updated).


@login_required
@complete_profile_required
def accept_pr(request, pk):
    mentor = request.user
    pr_qs = PullRequest.objects.filter(pk=pk)
    if pr_qs:
        pr = pr_qs.first()
        issue = pr.issue

        if mentor.username == issue.mentor.username:
            contributor = pr.contributor
            pr = PullRequest.objects.get(issue=issue, contributor=contributor)
            if pr.state == PullRequest.PENDING_VERIFICATION:
                pr.accept()
                message = f"Successfully accepted <a href={pr.html_url}>PR</a> of Issue <a href={issue.html_url}>" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
            else:
                message = f"This PR Verification Request is already Accepted/Rejected."
        else:
            message = f"You are not mentor of Issue <a href={issue.html_url}>{issue.number}</a> of Project <a href=" \
                      f"{issue.project.html_url}>{issue.project.name}</a>"
    else:
        message = f"This PR is probably already Accepted/Rejected."
    return HttpResponse(message)


@login_required
@complete_profile_required
def reject_pr(request, pk):
    mentor = request.user
    pr_qs = PullRequest.objects.filter(pk=pk)
    if pr_qs:
        pr = pr_qs.first()
        issue = pr.issue

        if mentor.username == issue.mentor.username:
            contributor = pr.contributor
            pr = PullRequest.objects.get(issue=issue, contributor=contributor)
            if pr.state == PullRequest.PENDING_VERIFICATION:
                pr.reject()
                message = f"Successfully rejected <a href={pr.html_url}>PR</a> of Issue <a href={issue.html_url}>" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
            else:
                message = f"This PR Verification Request is already Accepted/Rejected."
        else:
            message = f"You are not mentor of Issue <a href={issue.html_url}>{issue.number}</a> of Project <a href=" \
                      f"{issue.project.html_url}>{issue.project.name}</a>"
    else:
        message = f"This PR is probably already Accepted/Rejected."
    return HttpResponse(message)

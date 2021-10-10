from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse, redirect
from django.core.mail import EmailMessage
from home.helpers import send_email
from django.core import mail
from django.template.loader import render_to_string
from project.models import Project, Issue, IssueAssignmentRequest, ActiveIssue, PullRequest
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRSubmissionForm
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# TODO:ISSUE: Replace each HttpResponse with a HTML page
# TODO:ISSUE: Create a URL to view each Issue on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each PR on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each Issue Assignment Request on a separate Page with all its information.
# TODO:ISSUE: Make a Custom Http404 Page
# TODO:ISSUE: Up-vote Down-vote Issue Feature
from user_profile.models import UserProfile
from .forms import ContactForm
import smtplib

@complete_profile_required
def home(request):
    project_qs = Project.objects.all()
    issues_qs = Issue.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(issues_qs, 20)
    try:
        issue_p = paginator.page(page)
    except PageNotAnInteger:
        issue_p = paginator.page(1)
    except EmptyPage:
        issue_p = paginator.page(paginator.num_pages)
    context = {
        'projects': project_qs,
        'issues': issue_p
    }
    return render(request, 'home/index.html', context=context)


def authorize(request):
    """
    Used for rendering authorize.html which is responsible for both LogIn and SignUp
    :param request:
    :return:
    """
    return render(request, 'home/authorize.html', {})


@login_required
def logout_(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
@complete_profile_required
@check_issue_time_limit
def request_issue_assignment(request, issue_pk):
    issue = Issue.objects.get(pk=issue_pk)
    requester = request.user

    if issue.is_assignable(requester=requester):
        IssueAssignmentRequest.objects.create(issue=issue, requester=requester)
        message = f"Assignment Request for Issue <a href={issue.html_url}>#{issue.number}</a> of " \
                  f"<a href={issue.project.html_url}>{issue.project.name}</a> submitted successfully. "

        template_path = "home/mail_template_request_issue_assignment.html"
        email_context = {
            'mentor': issue.mentor,
            'user': requester,
            'url': issue.html_url,
            'protocol': request.get_raw_uri().split('://')[0],
            'host': request.get_host(),
            'subject': "Request for Issue Assignment under ContriHUB-21.",
        }
        try:
            send_email(template_path=template_path, email_context=email_context)
            # TODO:ISSUE: Create Html Template for HttpResponses in home/views.py
            return HttpResponse(
                f"Issue Requested Successfully. Email Request Sent to the Mentor({issue.mentor.username}). Keep your eye out on the your profile.")
        except mail.BadHeaderError:
            ms_teams_id = UserProfile.objects.get(user=issue.mentor).ms_teams_id
            return HttpResponse(
                f"Issue Requested Successfully, but there was some problem sending email to the mentor({issue.mentor.username}). For quick response from mentor try contacting him/her on MS-Teams({ms_teams_id})")
        except smtplib.SMTPSenderRefused:  # If valid EMAIL_HOST_USER and EMAIL_HOST_PASSWORD not set
            ms_teams_id = UserProfile.objects.get(user=issue.mentor).ms_teams_id
            return HttpResponse(
                f"Issue Requested Successfully, but there was some problem sending email to the mentor({issue.mentor.username}). For quick response from mentor try contacting him/her on MS-Teams({ms_teams_id})")
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


def reject_issue_request(request, issue_req_pk):
    # TODO: ISSUE: [Ask Mentor for Clarification]: Implement Reject Issue Request with proper error handling
    user = request.user
    issue_request = IssueAssignmentRequest.objects.get(pk=issue_req_pk)
    issue = issue_request.issue
    requester = issue_request.requester
    issue_request.state = IssueAssignmentRequest.REJECTED
    issue_request.save()
    message = f"Issue <a href={issue.html_url}>#{issue.number}</a> of Project <a href={issue.project.html_url}>" \
              f"{issue.project.name}</a> is rejected for {requester}"
    return HttpResponse(message)


@login_required
@complete_profile_required
@check_issue_time_limit
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

                template_path = "home/mail_template_submit_pr_request.html"
                email_context = {
                    'mentor': issue.mentor,
                    'user': contributor,
                    'url': pr.pr_link,
                    'protocol': request.get_raw_uri().split('://')[0],
                    'host': request.get_host(),
                    'subject': "Request for Approval of PR on an issue under ContriHUB-21.",
                }
                try:
                    send_email(template_path=template_path, email_context=email_context)
                    message = f"Email Request Sent to the Mentor({issue.mentor.username}). PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                              f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                except mail.BadHeaderError:
                    ms_teams_id = UserProfile.objects.get(user=issue.mentor).ms_teams_id
                    message = f"PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                              f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>. But there was some problem sending email to the mentor({issue.mentor.username}). For quick response from mentor try contacting him/her on MS-Teams({ms_teams_id})"
                except smtplib.SMTPSenderRefused:  # If valid EMAIL_HOST_USER and EMAIL_HOST_PASSWORD not set
                    ms_teams_id = UserProfile.objects.get(user=issue.mentor).ms_teams_id
                    message = f"PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                              f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>. But there was some problem sending email to the mentor({issue.mentor.username}). For quick response from mentor try contacting him/her on MS-Teams({ms_teams_id})"
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
                message = f"Successfully accepted <a href={pr.pr_link}>PR</a> of Issue <a href={issue.html_url}>" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
            else:
                message = f"This PR Verification Request is already Accepted/Rejected. Probably in the FrontEnd You still see the " \
                          f"Accept/Reject Button, because showing ACCEPTED/REJECTED status in frontend is an ISSUE."
        else:
            message = f"You are not mentor of Issue <a href={issue.html_url}>{issue.number}</a> of Project <a href=" \
                      f"{issue.project.html_url}>{issue.project.name}</a>"
    else:
        message = f"This PR is probably already Accepted. Probably in the FrontEnd You still see the " \
                  f"Accept/Reject Button, because showing ACCEPTED/REJECTED status in frontend is an ISSUE."
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
                message = f"Successfully rejected <a href={pr.pr_link}>PR</a> of Issue <a href={issue.html_url}>" \
                          f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
            else:
                message = f"This PR Verification Request is already Accepted/Rejected. Probably in the FrontEnd You still see the " \
                          f"Accept/Reject Button, because showing ACCEPTED/REJECTED status in frontend is an ISSUE."
        else:
            message = f"You are not mentor of Issue <a href={issue.html_url}>{issue.number}</a> of Project <a href=" \
                      f"{issue.project.html_url}>{issue.project.name}</a>"
    else:
        message = f"This PR Verification Request is already Accepted/Rejected. Probably in the FrontEnd You still see the " \
                  f"Accept/Reject Button, because showing ACCEPTED/REJECTED status in frontend is an ISSUE."
    return HttpResponse(message)


@login_required
def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        user = form['name'].value()
        email = form['email'].value()
        body = form['body'].value()
        subject = form['subject'].value()
        message = render_to_string('home/contact_body.html', {
            'user': user,
            'email': email,
            'body': body,
        })
        email = EmailMessage(
            subject, message, to=['contrihub.avishkar@gmail.com']
        )
        email.send()
        return redirect('home')
    elif request.method == 'GET':
        form = ContactForm()
        return render(request, 'home/contact_form.html', context={'form': form})

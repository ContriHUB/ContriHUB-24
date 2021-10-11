from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from project.models import Issue, PullRequest, IssueAssignmentRequest, ActiveIssue
from .forms import UserProfileForm,EditProfileForm
from .models import UserProfile
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRSubmissionForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from home.helpers import send_email
User = get_user_model()

# TODO:ISSUE: Implement feature where User can see how many Issues they have solved Level Wise


@complete_profile_required
@check_issue_time_limit
def profile(request, username):
    """
    View which returns User Profile based on username.
    :param request:
    :param username:
    :return:
    """
    user = request.user
    native_profile_qs = UserProfile.objects.filter(user__username=username)
    if native_profile_qs:  # Checking if profile exists

        native_profile = native_profile_qs.first()

        if username == user.username:
            # TODO: ISSUE Fetch User's Avatar's URL from Github API and display it in profile
            pr_requests_by_student = PullRequest.objects.filter(contributor=user)
            assignment_requests_by_student = IssueAssignmentRequest.objects.filter(requester=user)
            active_issues = ActiveIssue.objects.filter(contributor=user)

            mentored_issues = Issue.objects.filter(mentor=user)
            assignment_requests_for_mentor = IssueAssignmentRequest.objects.filter(issue__mentor=user)
            pr_requests_for_mentor = PullRequest.objects.filter(issue__mentor=user)

            pr_form = PRSubmissionForm()

            free_issues_solved = 0
            v_easy_issues_solved = 0
            easy_issues_solved = 0
            medium_issues_solved = 0
            hard_issues_solved = 0

            for pr in pr_requests_by_student:
                if pr.state == pr.ACCEPTED and pr.issue.level == 0:
                    free_issues_solved += 1
                if pr.state == pr.ACCEPTED and pr.issue.level == 4:
                    v_easy_issues_solved += 1
                if pr.state == pr.ACCEPTED and pr.issue.level == 1:
                    easy_issues_solved += 1
                if pr.state == pr.ACCEPTED and pr.issue.level == 2:
                    medium_issues_solved += 1
                if pr.state == pr.ACCEPTED and pr.issue.level == 3:
                    hard_issues_solved += 1

            pe_form = EditProfileForm(instance=request.user.userprofile)
            context = {
                "mentored_issues": mentored_issues,
                "pr_requests_by_student": pr_requests_by_student,
                "pr_requests_for_mentor": pr_requests_for_mentor,
                "active_issues": active_issues,
                "assignment_requests_by_student": assignment_requests_by_student,
                "assignment_requests_for_mentor": assignment_requests_for_mentor,
                'pr_form': pr_form,
                'pe_form':pe_form,
                "native_profile": native_profile,
                "free_issues_solved": free_issues_solved,
                "v_easy_issues_solved": v_easy_issues_solved,
                "easy_issues_solved": easy_issues_solved,
                "medium_issues_solved": medium_issues_solved,
                "hard_issues_solved": hard_issues_solved,
            }
            return render(request, 'user_profile/profile.html', context=context)
        else:
            context = {
                "native_profile": native_profile,
            }
            return render(request, 'user_profile/profile.html', context=context)
    return HttpResponse("Profile not found!")


@login_required
def complete(request):
    """
    For Completing User Profile after First Login.
    :param request:
    :return:
    """
    existing_profile = UserProfile.objects.get(user=request.user)
    if request.method == "GET":
        form = UserProfileForm(instance=existing_profile)
        context = {
            'form': form
        }
        return render(request, 'user_profile/complete_profile.html', context=context)

    form = UserProfileForm(request.POST, instance=existing_profile)
    if form.is_valid():
        # TODO:ISSUE Backend Check on Registration Number
        existing_profile = form.save(commit=False)
        existing_profile.is_complete = True
        existing_profile.save()
    return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))


    # TODO:ISSUE Edit Profile Functionality


@login_required
def rankings(request):
    contributors = UserProfile.objects.filter(role=UserProfile.STUDENT).order_by('-total_points')
    context = {
        'contributors': contributors,
    }
    # TODO:ISSUE: Display number of Issues solved as well in the Rankings
    return render(request, 'user_profile/rankings.html', context=context)

@login_required
def edit_profile(request):
    if request.method=="POST":
        form=EditProfileForm(request.POST)
        user = request.user
        reg_num = form['registration_no'].value()
        year = form['current_year'].value()
        course = form['course'].value()
        course=dict(form.fields['course'].choices)[int(course)]
        subject = "Change in Personal Information"
        message = render_to_string('user_profile/edit_email.html', {
            'user': user,
            'reg_num': reg_num,
            'year': year,
            'course': course,
        })

        email = EmailMessage(
            subject, message, to=['contrihub.avishkar@gmail.com']
        )
        email.content_subtype="html"
        email.send()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse("Something went wrong")

@login_required
def change_msid(request):
    if request.is_ajax():
        new_id=request.POST.get('ms_id')
        user_pro=UserProfile.objects.get(user=request.user)
        if user_pro.ms_teams_id != new_id:
         user_pro.ms_teams_id=new_id
         user_pro.save()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse("Something Went Wrong")
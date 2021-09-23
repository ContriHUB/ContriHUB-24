from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from project.models import Issue, PullRequest, IssueAssignmentRequest, ActiveIssue
from .forms import UserProfileForm
from .models import UserProfile
from helper import complete_profile_required
from project.forms import PRSubmissionForm

User = get_user_model()

# TODO:ISSUE: Implement feature where User can see how many Issues they have solved Level Wise


@complete_profile_required
def profile(request, username):
    """
    View which returns User Profile based on username.
    :param request:
    :param username:
    :return:
    """
    user = request.user
    if user.is_authenticated:
        native_profile = UserProfile.objects.get(user__username=username)
        if username == user.username:
            pr_requests_by_student = PullRequest.objects.filter(contributor=user)
            assignment_requests_by_student = IssueAssignmentRequest.objects.filter(requester=user)
            active_issues = ActiveIssue.objects.filter(contributor=user)

            mentored_issues = Issue.objects.filter(mentor=user)
            assignment_requests_for_mentor = IssueAssignmentRequest.objects.filter(issue__mentor=user)
            pr_requests_for_mentor = PullRequest.objects.filter(issue__mentor=user)

            pr_form = PRSubmissionForm()

            context = {
                "mentored_issues": mentored_issues,
                "pr_requests_by_student": pr_requests_by_student,
                "pr_requests_for_mentor": pr_requests_for_mentor,
                "active_issues": active_issues,
                "assignment_requests_by_student": assignment_requests_by_student,
                "assignment_requests_for_mentor": assignment_requests_for_mentor,
                'pr_form': pr_form,
                "native_profile": native_profile
            }
            return render(request, 'user_profile/profile.html', context=context)
        else:
            context = {
                "native_profile": native_profile
            }
            return render(request, 'user_profile/profile.html', context=context)
    else:
        response = "EMPTY ERROR"
    context = {
        "response": response
    }
    return render(request, 'user_profile/profile.html', context=context)


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

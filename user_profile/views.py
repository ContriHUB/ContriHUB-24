from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from project.models import Issue, PullRequest
from .forms import UserProfileForm
from .models import UserProfile
from helper import complete_profile_required

User = get_user_model()


@complete_profile_required
def profile(request, username):
    user = request.user
    if user.is_authenticated and username == user.username:
        mentored_issues = Issue.objects.filter(mentor=user)
        assigned_issues = Issue.objects.filter(assignee=user)
        submitted_prs = PullRequest.objects.filter(user=user)

        context = {
            "mentored_issues": mentored_issues,
            "assigned_issues": assigned_issues,
            "submitted_prs": submitted_prs
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
    existing_profile = UserProfile.objects.get(user=request.user)
    if request.method == "GET":
        form = UserProfileForm(instance=existing_profile)
        context = {
            'form': form
        }
        return render(request, 'user_profile/complete_profile.html', context=context)
    # else:
    form = UserProfileForm(request.POST, instance=existing_profile)
    if form.is_valid():
        # TODO: Backend Check on Registration Number ISSUE
        existing_profile = form.save(commit=False)
        existing_profile.is_complete = True
        existing_profile.save()
    return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))


    # TODO: Edit Profile Functionality ISSUE
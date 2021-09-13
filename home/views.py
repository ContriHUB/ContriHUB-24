from django.shortcuts import render, HttpResponseRedirect, reverse
from project.models import Project, Issue
from django.contrib.auth import logout
from helper import complete_profile_required
# Create your views here.


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


@complete_profile_required
def submit_pr_request(request):
    pass

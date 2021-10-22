from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

import user_profile.views
from project.models import Project, Issue, PullRequest, IssueAssignmentRequest, ActiveIssue
from .forms import UserProfileForm, EditProfileForm
from project.forms import CreateIssueForm
from .models import UserProfile
from project.views import parse_level
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRSubmissionForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
import re
import json
import requests

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
        n_user = UserProfile.objects.get(user=native_profile.user)
        prRequestByNativeProfile = PullRequest.objects.filter(contributor=n_user.user)
        free_issues_solved = 0
        v_easy_issues_solved = 0
        easy_issues_solved = 0
        medium_issues_solved = 0
        hard_issues_solved = 0

        for pr in prRequestByNativeProfile:
            if pr.state == pr.ACCEPTED and pr.issue.level == pr.issue.FREE:
                free_issues_solved += 1
            if pr.state == pr.ACCEPTED and pr.issue.level == pr.issue.VERY_EASY:
                v_easy_issues_solved += 1
            if pr.state == pr.ACCEPTED and pr.issue.level == pr.issue.EASY:
                easy_issues_solved += 1
            if pr.state == pr.ACCEPTED and pr.issue.level == pr.issue.MEDIUM:
                medium_issues_solved += 1
            if pr.state == pr.ACCEPTED and pr.issue.level == pr.issue.HARD:
                hard_issues_solved += 1

        if username == user.username:
            pr_requests_by_student = PullRequest.objects.filter(contributor=user)
            assignment_requests_by_student = IssueAssignmentRequest.objects.filter(requester=user)
            active_issues = ActiveIssue.objects.filter(contributor=user)

            mentored_issues = Issue.objects.filter(mentor=user)
            assignment_requests_for_mentor = IssueAssignmentRequest.objects.filter(issue__mentor=user)
            pr_requests_for_mentor = PullRequest.objects.filter(issue__mentor=user)

            pr_form = PRSubmissionForm()
            create_issue_form = CreateIssueForm()
            pe_form = EditProfileForm(instance=request.user.userprofile)
            context = {
                "mentored_issues": mentored_issues,
                "pr_requests_by_student": pr_requests_by_student,
                "pr_requests_for_mentor": pr_requests_for_mentor,
                "active_issues": active_issues,
                "assignment_requests_by_student": assignment_requests_by_student,
                "assignment_requests_for_mentor": assignment_requests_for_mentor,
                'pr_form': pr_form,
                'pe_form': pe_form,
                'create_issue_form': create_issue_form,
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
                "free_issues_solved": free_issues_solved,
                "v_easy_issues_solved": v_easy_issues_solved,
                "easy_issues_solved": easy_issues_solved,
                "medium_issues_solved": medium_issues_solved,
                "hard_issues_solved": hard_issues_solved,
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
        phd = r'\b(2)\d{3}(R|r)[a-zA-Z]{2}\d{2}\b'
        mtech = r'\b(2)\d{3}[a-zA-z]{2}\d{2}\b'
        msc = r'\b(2)\d{3}(MSC|msc)\d{2}\b'
        mca = r'\b(2)\d{3}(ca|CA)\d{3}\b'
        btech = r'\b(2)\d{7}\b'
        reg_ex = [btech, mca, mtech, msc, phd]
        reg_no = request.POST.get('registration_no')
        course = int(request.POST.get('course'))
        flag = False
        if (re.match(reg_ex[course - 1], reg_no)):
            flag = True
        if flag:
            existing_profile = form.save(commit=False)
            existing_profile.is_complete = True
            existing_profile.save()
            return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
        else:
            return HttpResponse('Something Went wrong.!!!')
        return HttpResponseRedirect(reverse('complete_profile'))

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
    if request.method == "POST":
        form = EditProfileForm(request.POST)
        user = request.user
        reg_num = form['registration_no'].value()
        year = form['current_year'].value()
        course = form['course'].value()
        course = dict(form.fields['course'].choices)[int(course)]
        subject = "Change in Personal Information"
        message = render_to_string('user_profile/edit_email.html', {
            'user': user,
            'reg_num': reg_num,
            'year': year,
            'course': course,
        })
        print({
            'user': user,
            'reg_num': reg_num,
            'year': year,
            'course': course,
        })
        email = EmailMessage(
            subject, message, to=['contrihub.avishkar@gmail.com']
        )
        email.content_subtype = "html"
        email.send()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse("Something went wrong")


@login_required
def change_contact_info(request):
    if request.is_ajax():
        new_id = request.POST.get('ms_id')
        new_whatsapp_no = request.POST.get('whatsapp_no')
        user_pro = UserProfile.objects.get(user=request.user)
        if user_pro.ms_teams_id != new_id:
            user_pro.ms_teams_id = new_id
            user_pro.save()
        if user_pro.whatsapp_no != new_whatsapp_no:
            user_pro.whatsapp_no = new_whatsapp_no
            user_pro.save()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse("Something Went Wrong")


@login_required
def create_issue(request):
    if request.user.userprofile.role == UserProfile.STUDENT :
        messages.error(request,"Students cannot create an issue")
        return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
    level = {
        '0': 'free',
        '1': 'easy',
        '2': 'medium',
        '3': 'hard',
        '4': 'very_easy'
    }
    if request.is_ajax():
        data = request.POST
        project_id = data.get('project')
        level_id = data.get('level')
        mentor_id = data.get('mentor')
        points = data.get('points')
        is_restricted_str = data.get('is_restricted')
        default_points = parse_level(level.get(level_id))
        title = data.get('title')
        description = data.get('desc')

        is_default_points_used = False
        if points == '0':
            is_default_points_used = True
            points = str(default_points[1])     # refer project.views and settings.py for parse_level and points

        is_restricted = False
        if is_restricted_str == '1':
            is_restricted = True

        project = Project.objects.get(id=project_id)
        level = level.get(level_id)
        mentor = User.objects.get(id=mentor_id).username
        url = project.api_url

        labels = [mentor, level]

        if not is_default_points_used:
            labels.append(points)

        if is_restricted:
            labels.append('restricted')

        url += '/issues'

        issue_detail = {
            'title': title,
            'body': description,
            'labels': labels
        }

        payload = json.dumps(issue_detail)
        social = request.user.social_auth.get(provider='github')
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
        }

        r = requests.post(url, data=payload, headers=headers)
        response_data = r.json()

        if r.status_code == 201:

            print('Successfully created Issue "%s"' % title)
            Issue.objects.create(
                title='' + response_data['title'],
                api_url='' + response_data['repository_url'],
                html_url='' + response_data['url'],
                project=project,
                mentor=User.objects.get(id=mentor_id),
                level=level_id,
                points=points,
                state=1,
                description=description,
                is_restricted=is_restricted
            )
            return JsonResponse({'status': 'success'})
        else:
            print('Could not create Issue "%s"' % title)
            print('Response:', r.content)
            return JsonResponse({'status': 'error'})
    else:
        return HttpResponseRedirect("Something Went Wrong")

import re
import json
import requests

from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from pprintpp import pprint

from helper import complete_profile_required, check_issue_time_limit
from .forms import UserProfileForm, EditProfileForm
from .models import UserProfile

from project.models import Project, Issue, PullRequest, IssueAssignmentRequest, ActiveIssue
from project.forms import CreateIssueForm, PRSubmissionForm
from project.views import parse_level

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
    messages.success(request,"Profile not found!",extra_tags='safe')
    return HttpResponseRedirect(reverse('home'))


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
        if re.match(reg_ex[course - 1], reg_no):
            flag = True
        if flag:
            existing_profile = form.save(commit=False)
            existing_profile.is_complete = True
            existing_profile.save()
            return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
        else:
            messages.success(request,'Something Went wrong.!!!',extra_tags='safe')
            return HttpResponseRedirect(reverse('complete_profile'))
    return HttpResponseRedirect(reverse('complete_profile'))


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

        email = EmailMessage(
            subject, message, to=['contrihub.avishkar@gmail.com']
        )
        email.content_subtype = "html"
        email.send()
        return JsonResponse({'status': 'success'})
    else:
        messages.success(request, 'Something Went wrong.!!!', extra_tags='safe')
        return redirect('user_profile',username=request.user)


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
        messages.success(request, 'Something Went wrong.!!!', extra_tags='safe')
        return redirect('user_profile', username=request.user)


@login_required
def create_issue(request):

    # If logged - in user is Student
    if request.user.userprofile.role == UserProfile.STUDENT:
        messages.error(request, "Students cannot create an issue")
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
            points = str(default_points[1])  # refer project.views and settings.py for parse_level and points

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
                number= response_data['number'],
                title='' + response_data['title'],
                api_url='' + response_data['repository_url'],
                html_url='' + response_data['html_url'],
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
        messages.success(request, 'Something Went wrong.!!!', extra_tags='safe')
        return redirect('user_profile', username=request.user)



def pr_details(request,pk):
    pr = PullRequest.objects.get(pk=pk)
    pr_url = pr.pr_link
    url = pr.issue.project.api_url
    index = pr_url.rfind('pull/')
    index+= 5
    pull_no=''
    for c in pr_url[index:len(pr_url)]:
        if c=='/'or c=='#':
            break
        pull_no+=c
    url+='/pulls/'+pull_no
    social = request.user.social_auth.get(provider='github')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
    }
    r = requests.get(url, headers=headers)
    response_data = r.json()
    if r.status_code == 200:
        user = response_data['user']
        user_avatar_url = user['avatar_url']
        user_name = user['login']
        head = response_data['head']
        head_label = head['label']
        pr_to_repo = head['repo']
        pr_to_repo_name = pr_to_repo['name']+':'+pr_to_repo['default_branch']
        body = response_data['body']
        files_changed=response_data['changed_files']
        no_of_commits = response_data['commits']
        created_at = response_data['created_at']
        created_dd = created_at[8:10]
        created_mm = created_at[5:7]
        created_yyyy = created_at[0:4]
        created_hh = created_at[11:13]
        created_min = created_at[14:16]
        created_date = created_dd + '-' + created_mm + '-' + created_yyyy
        created_time = created_hh + ':' + created_min
        created_dt = 'On '+created_date +' at '+created_time
        deletions = response_data['deletions']
        pr_from = response_data['head']
        html_url = response_data['html_url']
        l = response_data['labels']
        labels=[]
        no_of_labels = 0
        for lb in l:
            labels.append(lb['name'])
            no_of_labels+=1
        maintainer_can_modify = response_data['maintainer_can_modify']
        mergeable = response_data['mergeable']
        mergeable_state = response_data['mergeable_state']
        merged_at = response_data['merged_at']
        merge_status = True
        merged_dt=''
        if merged_at == '':
            merge_status = False
        if merged_at :
            merged_dd = merged_at[8:10]
            merged_mm = merged_at[5:7]
            merged_yyyy = merged_at[0:4]
            merged_hh = merged_at[11:13]
            merged_min = merged_at[14:16]
            merged_date = merged_dd + '-' + merged_mm + '-' + merged_yyyy
            merged_time = merged_hh + ':' + merged_min
            merged_dt = 'On '+merged_date +' at '+merged_time
        merged_by = response_data['merged_by']
        merged_by_user = ''
        if merged_by != None:
            merged_by_user=merged_by['login']
        else:
            merged_by_user='None'
        title = response_data['title']
        updated_at = response_data['updated_at']
        context = {
            'pr_no':pull_no,
            'pr':pr,
            'head_label' : head_label,
            'user' : user,
            'user_avatar_url' : user_avatar_url,
            'username':user_name,
            'body' : body,
            'files_changed' : files_changed,
            'no_of_commits' : no_of_commits,
            'created_at' : created_at,
            'deletions' : deletions,
            'pr_from' : pr_from,
            'html_url' : html_url,
            'labels' : labels,
            'no_of_labels':no_of_labels,
            'maintainer_can_modify' : maintainer_can_modify,
            'mergeable' : mergeable,
            'mergeable_state' : mergeable_state,
            'merge_status':merge_status,
            'merged_at' : merged_at,
            'merged_by_user' : merged_by_user,
            'title' : title,
            'updated_at' : updated_at,
            'issue' : pr.issue,
            'pr_to_repo_name':pr_to_repo_name,
            'merged_dt':merged_dt,
            'created_dt':created_dt,
        }
        return render(request, 'user_profile/pr_details_page.html', context=context)
    else:
        print('Could not fetch PR details')
        print('Response:', r.content)
        return HttpResponse("Something Went Wrong")
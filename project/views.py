from django.shortcuts import HttpResponseRedirect, reverse
from contrihub.settings import AVAILABLE_PROJECTS, LABEL_MENTOR, LABEL_LEVEL, LABEL_POINTS, DEPENDABOT_LOGIN, \
    LABEL_RESTRICTED, LABEL_BONUS, DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, DEFAULT_HARD_POINTS
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from .models import Project, Issue, PullRequest
from user_profile.models import UserProfile
from helper import complete_profile_required, fetch_all_issues
from config import APIS, URIS
from .serializers import ProjectSerializer, IssueSerializer, PullRequestSerializer
from user_profile.serializers import UserSerializer, UserProfileSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

User = get_user_model()


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_projects(request):
    """
    Used to Populate Projects in Local Database. Creates entries based on project names present in AVAILABLE_PROJECTS
    config variable in settings.py
    :param request:
    :return:
    """
    api_uri = APIS['api_contrihub']
    html_uri = URIS['uri_html']
    print(AVAILABLE_PROJECTS)
    for project_name in AVAILABLE_PROJECTS:
        project_qs = Project.objects.filter(name=project_name)
        if not project_qs:
            api_url = f"{api_uri}{project_name}"
            html_url = f"{html_uri}{project_name}"
            Project.objects.create(
                name=project_name,
                api_url=api_url,
                html_url=html_url
            )

    return HttpResponseRedirect(reverse('home'))


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_issues(request):
    """
    Used to Populate Issues in Local Database. It fetches Issues from Github using Github API.
    :param request:
    :return:
    """
    project_qs = Project.objects.all()

    social = request.user.social_auth.get(provider='github')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
    }
    uri = APIS['api_contrihub']

    for project in project_qs:
        print("PROJECT: ", project.name)
        issues_dict = fetch_all_issues(uri, project.name, headers)
        issues = issues_dict['data']
        print("COUNT: ", len(issues))
        for issue in issues:
            # TODO: Can be given as ISSUE
            if issue['user']['login'] == DEPENDABOT_LOGIN:  # Ignoring issues created by Dependabot
                continue
            if issue.get('pull_request') is not None:  # this issue is actually a PR.
                # Source: https://docs.github.com/en/rest/reference/issues#list-repository-issues
                print("This issue is a actually a PR")
                continue
            title, number = issue['title'], issue['number']
            mentor_name, level, points, is_restricted, bonus_value, bonus_description = parse_labels(labels=issue['labels'])

            if mentor_name and level:  # If mentor name and level labels are present in issue
                api_url, html_url = issue['url'], issue['html_url']
                issue_qs = Issue.objects.filter(number=number, project=project)
                # print("I: ", number, title, mentor_name, level)
                if issue_qs:  # Update if already present
                    db_issue = issue_qs.first()
                    db_issue.title = title
                    db_issue.level = level
                    db_issue.points = points
                    db_issue.is_restricted = is_restricted
                    db_issue.bonus_value = bonus_value
                    db_issue.bonus_description = bonus_description
                else:  # Else Create New
                    db_issue = Issue(
                        number=number,
                        title=title,
                        api_url=api_url,
                        html_url=html_url,
                        project=project,
                        level=level,
                        points=points,
                        is_restricted=is_restricted,
                        bonus_value=bonus_value,
                        bonus_description=bonus_description
                    )

                # print(db_issue)
                try:
                    mentor = User.objects.get(username=mentor_name)
                    db_issue.mentor = mentor
                except User.DoesNotExist:
                    pass

                db_issue.save()

    return HttpResponseRedirect(reverse('home'))

def parse_bonus(bonus):
    return bonus.strip(" ").split(" ")[0], bonus


def parse_labels(labels):
    mentor, level, points, is_restricted, bonus_value, bonus_description = None, None, 0, False, "0", " "
    for label in labels:

        if str(label["description"]).lower() == LABEL_MENTOR:  # Parsing Mentor
            mentor = parse_mentor(label["name"])

        if str(label["description"]).lower() == LABEL_LEVEL:  # Parsing Level
            level, points = parse_level(label["name"])  # Fetching Level and it's default point

        if str(label["description"]).lower() == LABEL_POINTS:  # Parsing Points
            points = parse_points(label["name"])  # Consider Custom points if provided

        if str(label["name"]).lower() == LABEL_RESTRICTED:  # Parsing Is Restricted
            is_restricted = True

        if str(label["description"]).lower() == LABEL_BONUS:  # Bonus Points
            bonus_value, bonus_description = parse_bonus(label["name"])

    return mentor, level, points, is_restricted, bonus_value, bonus_description


def parse_level(level):
    level = str(level).lower()
    levels_read = (Issue.FREE_READ, Issue.VERY_EASY_READ, Issue.EASY_READ, Issue.MEDIUM_READ, Issue.HARD_READ)
    levels = (Issue.FREE, Issue.VERY_EASY, Issue.EASY, Issue.MEDIUM, Issue.HARD)
    default_points = (
    DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, DEFAULT_HARD_POINTS)

    for lev, read, pts in zip(levels, levels_read, default_points):
        if level == str(read).lower():
            return lev, pts

    return Issue.EASY, DEFAULT_EASY_POINTS  # Default FallBack


def parse_mentor(mentor):
    return str(mentor).lower()


def parse_points(points):
    points = str(points)

    if points.isnumeric():
        return int(float(points))

    return 0  # Default FallBack


@api_view(['GET'])
def project_list_view(request, *args, **kwargs):
    qs = Project.objects.all()
    serializer = ProjectSerializer(qs, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def project_detail_view(request, project_id, *args, **kwargs):
    qs = Project.objects.filter(id=project_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = ProjectSerializer(obj)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def issue_list_view(request, project_id, *args, **kwargs):
    qs = Issue.objects.filter(project_id=project_id)
    serializer = IssueSerializer(qs, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def issue_detail_view(request, project_id, issue_id, *args, **kwargs):
    qs = Issue.objects.filter(project_id=project_id).filter(id=issue_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = IssueSerializer(obj)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def pullrequest_list_view(request, project_id, *args, **kwargs):
    qs = PullRequest.objects.filter(project_id=project_id)
    serializer = PullRequestSerializer(qs, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def pullrequest_detail_view(request, project_id, pull_id, *args, **kwargs):
    qs = PullRequest.objects.filter(project_id=project_id).filter(id=pull_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = PullRequestSerializer(obj)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def contributors_list_view(request, project_id, *args, **kwargs):
    project = Project.objects.filter(id=project_id)
    if not project.exists():
        return Response({}, status=404)
    project = project.first()
    issue = Issue.objects.filter(project=project)
    qs = PullRequest.objects.filter(issue__in=issue)
    us = User.objects.filter(contributor__in=qs)
    usp = UserProfile.objects.filter(user__in=us)
    serializer = UserProfileSerializer(usp, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def user_contrib_list_view(request, github_user_name, *args, **kwargs):
    user = User.objects.filter(username=github_user_name)
    if not user.exists():
        return Response({}, status=404)
    user = user.first()
    qs = PullRequest.objects.filter(contributor=user)
    serializer = PullRequestSerializer(qs, many=True)
    return Response(serializer.data, status=200)

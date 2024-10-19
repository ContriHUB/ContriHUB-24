from django.shortcuts import HttpResponseRedirect, reverse, render
from contrihub.settings import AVAILABLE_PROJECTS, LABEL_MENTOR, LABEL_LEVEL, LABEL_POINTS, DEPENDABOT_LOGIN, \
    LABEL_RESTRICTED, DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, \
    DEFAULT_HARD_POINTS
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from .models import Project, Issue
from helper import safe_hit_url, SUCCESS, complete_profile_required
from config import api_endpoint, html_endpoint
import requests

User = get_user_model()


def fetch_github_repositories():
    """
    Fetches public repositories from the GitHub organization 'ContriHUB' using the GitHub API.
    """
    github_api_url = "https://api.github.com/orgs/ContriHUB/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(github_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns the list of repositories
    else:
        return []


def filter_matching_projects(repositories, available_projects):
    """
    Filters GitHub repositories to match with the projects defined in AVAILABLE_PROJECTS.
    """
    matching_projects = []
    
    for repo in repositories:
        if repo['name'] in available_projects:
            project_data = {
                "name": repo["name"],
                "maintainer": repo["owner"]["login"],
                "about": repo["description"],
            }
            matching_projects.append(project_data)
    
    return matching_projects


def home(request):
    """
    Home view that fetches GitHub repositories and filters them to match the AVAILABLE_PROJECTS.
    The filtered data is then passed to the template.
    """
    repositories = fetch_github_repositories()  # Fetch all repos from GitHub
    matching_projects = filter_matching_projects(repositories, AVAILABLE_PROJECTS)  # Filter projects
    
    context = {
        "projects": matching_projects
    }
    
    return render(request, 'index.html', context)


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_projects(request):
    """
    Used to Populate Projects in Local Database. Creates entries based on project names present in AVAILABLE_PROJECTS
    config variable in settings.py
    """
    api_uri = api_endpoint['contrihub_api_1']
    html_uri = html_endpoint['contrihub_html']

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
    """
    project_qs = Project.objects.all()

    social = request.user.social_auth.get(provider='github')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
    }

    uri = api_endpoint['contrihub_api_2']

    for project in project_qs:
        url = f"{uri}{project.name}/issues"
        response = safe_hit_url(url=url, headers=headers)
        if response['status'] == SUCCESS:
            issues = response['data']
            for issue in issues:
                try:
                    if issue['user']['login'] == DEPENDABOT_LOGIN:  # Ignoring issues created by Dependabot
                        continue
                except:
                    continue
                finally:
                    print('error')
                if issue.get('pull_request') is not None:  # this issue is actually a PR.
                    print("This issue is actually a PR")
                    continue
                title, number, state = issue['title'], issue['number'], issue['state']
                mentor_name, level, points, is_restricted = parse_labels(labels=issue['labels'])

                api_url, html_url = issue['url'], issue['html_url']
                issue_qs = Issue.objects.filter(number=number, project=project)

                if issue_qs:  # Update if already present
                    db_issue = issue_qs.first()
                    db_issue.title = title
                    db_issue.level = level
                    db_issue.levelcolor = level
                    db_issue.points = points
                    db_issue.is_restricted = is_restricted
                    db_issue.bonus_pt = 0
                    if state == "closed":
                        db_issue.state = db_issue.CLOSED
                    else:
                        db_issue.state = db_issue.OPEN

                else:  # Else Create New
                    db_issue = Issue(
                        number=number,
                        title=title,
                        api_url=api_url,
                        html_url=html_url,
                        project=project,
                        level=level,
                        levelcolor=level,
                        points=points,
                        is_restricted=is_restricted,
                        bonus_pt=0
                    )

                try:
                    mentor = User.objects.get(username=mentor_name)
                    db_issue.mentor = mentor
                except User.DoesNotExist:
                    pass

                db_issue.save()

    return HttpResponseRedirect(reverse('home'))


def parse_labels(labels):
    mentor, level, points, is_restricted = None, Issue.EASY, 0, False
    for label in labels:

        if str(label["description"]).lower() == LABEL_MENTOR:  # Parsing Mentor
            mentor = parse_mentor(label["name"])

        if str(label["description"]).lower() == LABEL_LEVEL:  # Parsing Level
            level, points = parse_level(label["name"])  # Fetching Level and its default point

        if str(label["description"]).lower() == LABEL_POINTS:  # Parsing Points
            points = parse_points(label["name"])  # Consider Custom points if provided

        if str(label["name"]).lower() == LABEL_RESTRICTED:  # Parsing Is Restricted
            is_restricted = True

    return mentor, level, points, is_restricted


def parse_level(level):
    level = str(level).lower()
    levels_read = (Issue.FREE_READ, Issue.VERY_EASY_READ, Issue.EASY_READ, Issue.MEDIUM_READ, Issue.HARD_READ)
    levels = (Issue.FREE, Issue.VERY_EASY, Issue.EASY, Issue.MEDIUM, Issue.HARD)
    default_points = (
        DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, DEFAULT_HARD_POINTS
    )

    for lev, read, pts in zip(levels, levels_read, default_points):
        if level == str(read).lower():
            return lev, pts

    return Issue.EASY, DEFAULT_EASY_POINTS  # Default FallBack


def parse_mentor(mentor):
    return str(mentor)


def parse_points(points):
    points = str(points)

    if points.isnumeric():
        return int(float(points))

    return 0  # Default FallBack

from django.shortcuts import HttpResponseRedirect, reverse
from contrihub.settings import AVAILABLE_PROJECTS, LABEL_MENTOR, LABEL_LEVEL, LABEL_POINTS, DEPENDABOT_LOGIN
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from .models import Project, Issue
from helper import safe_hit_url, SUCCESS, complete_profile_required

User = get_user_model()


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_projects(request):
    available_projects = str(AVAILABLE_PROJECTS).split(";")

    api_uri = "https://api.github.com/repos/ContriHUB/"
    html_uri = "https://github.com/ContriHUB/"

    for project_name in available_projects:
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
    project_qs = Project.objects.all()

    social = request.user.social_auth.get(provider='github')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
    }

    uri = "https://api.github.com/repos/contrihub/"

    for project in project_qs:
        url = f"{uri}{project.name}/issues"
        response = safe_hit_url(url=url, headers=headers)
        if response['status'] == SUCCESS:
            issues = response['data']
            for issue in issues:

                if issue['user']['login'] == DEPENDABOT_LOGIN:  # Ignoring issues created by Dependabot
                    continue

                title, number = issue['title'], issue['number']
                mentor_name, level, points = parse_labels(labels=issue['labels'])
                api_url, html_url = issue['url'], issue['html_url']
                issue_qs = Issue.objects.filter(number=number)

                if issue_qs:  # Update if already present
                    db_issue = issue_qs.first()
                    db_issue.title = title
                    db_issue.level = level
                    db_issue.points = points
                else:  # Else Create New
                    db_issue = Issue(
                        number=number,
                        title=title,
                        api_url=api_url,
                        html_url=html_url,
                        project=project,
                        level=level,
                        points=points,
                    )

                print(db_issue)
                try:
                    mentor = User.objects.get(username=mentor_name)
                    db_issue.mentor = mentor
                except User.DoesNotExist:
                    pass

                db_issue.save()

    return HttpResponseRedirect(reverse('home'))


def parse_labels(labels):
    mentor, level, points = None, Issue.EASY, 0
    for label in labels:

        if str(label["description"]).lower() == LABEL_MENTOR:  # Parsing Mentor
            mentor = parse_mentor(label["name"])

        if str(label["description"]).lower() == LABEL_LEVEL:  # Parsing Level
            level = parse_level(label["name"])

        if str(label["description"]).lower() == LABEL_POINTS:  # Parsing Points
            points = parse_points(label["name"])

    return mentor, level, points


def parse_level(level):
    level = str(level).lower()
    levels_read = (Issue.FREE_READ, Issue.EASY_READ, Issue.MEDIUM_READ, Issue.DIFFICULT_READ)
    levels = (Issue.FREE, Issue.EASY, Issue.MEDIUM, Issue.DIFFICULT)

    for lev, read in zip(levels, levels_read):
        if level == str(read).lower():
            return lev

    return Issue.EASY  # Default FallBack


def parse_mentor(mentor):
    return str(mentor).lower()


def parse_points(points):
    points = str(points)

    if points.isnumeric():
        return int(float(points))

    return 0  # Default FallBack

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Project(models.Model):

    name = models.CharField(verbose_name="Name", max_length=200)

    api_url = models.URLField(verbose_name="API URL")

    html_url = models.URLField(verbose_name="HTML URL")

    def __str__(self):
        return self.name


class Issue(models.Model):

    FREE, EASY, MEDIUM, DIFFICULT = 0, 1, 2, 3
    FREE_READ, EASY_READ, MEDIUM_READ, DIFFICULT_READ = "Free", "Easy", "Medium", "Difficult"  # Human Readable Names
    LEVELS = (
        (FREE, FREE_READ),  # (Value, Human Readable Name)
        (EASY, EASY_READ),
        (MEDIUM, MEDIUM_READ),
        (DIFFICULT, DIFFICULT_READ),
    )

    OPEN, ASSIGNED, CLOSED = 1, 2, 3
    STATES = (
        (OPEN, "Open"),
        (ASSIGNED, "Assigned"),
        (CLOSED, "Closed"),
    )

    number = models.IntegerField(verbose_name="Number", default=0)

    title = models.CharField(verbose_name="Title", max_length=200)

    api_url = models.URLField(verbose_name="API URL")

    html_url = models.URLField(verbose_name="HTML URL")

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    mentor = models.ForeignKey(User, related_name="mentor", on_delete=models.DO_NOTHING, null=True)

    # 1-Easy, 2-Medium, 3-Difficult
    level = models.PositiveSmallIntegerField(verbose_name='Level', choices=LEVELS, default=1)

    points = models.IntegerField(verbose_name="Points", default=0)

    # 1 - Open, 2 - Assigned, 0 - Closed
    state = models.PositiveSmallIntegerField('State', choices=STATES, default=1)

    assignee = models.ForeignKey(User, related_name="assignee", on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.title


class PullRequest(models.Model):
    ACCEPTED, REJECTED, PENDING_VERIFICATION = 1, 2, 3
    STATES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (PENDING_VERIFICATION, "Pending Verification"),
    )

    api_url = models.URLField(verbose_name="API URL")

    html_url = models.URLField(verbose_name="HTML URL")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    state = models.PositiveSmallIntegerField(verbose_name="State", choices=STATES, default=PENDING_VERIFICATION)

    def __str__(self):
        return f"{self.user}_{self.issue}"

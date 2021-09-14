from django.db import models
from django.contrib.auth import get_user_model
from contrihub.settings import MAX_SIMULTANEOUS_ISSUE
from django.utils import timezone

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

    OPEN, CLOSED = 1, 3
    STATES = (
        (OPEN, "Open"),
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

    # 1 - Open, 0 - Closed
    state = models.PositiveSmallIntegerField('State', choices=STATES, default=1)

    # Restricted only for BTech 2nd yr and MCA 1st yr.
    is_restricted = models.BooleanField(verbose_name='Is Restricted', default=False)

    def __str__(self):
        return self.title

    def is_assignable(self, requester):

        if self.state == self.CLOSED:
            return False

        is_active = ActiveIssue.objects.filter(issue=self)

        if is_active:  # If this issue is already assigned to someone currently
            return False

        profile = requester.userprofile

        if profile.role != profile.STUDENT:
            return False

        if profile.current_year == profile.FINAL:  # Final Year Students not allowed
            return False

        if self.is_restricted:
            if profile.course in (profile.M_TECH, profile.M_SC, profile.PHD):
                return False

            if profile.course == profile.B_TECH:
                if profile.current_year in (profile.THIRD, profile.FINAL):
                    return False

            # if requester.course == requester.MCA:  # TODO: Check what to allow
            #     if requester.current_year in (requester.)

        requester_active_issue_count = ActiveIssue.objects.filter(contributor=requester).count()

        if requester_active_issue_count > MAX_SIMULTANEOUS_ISSUE:
            return False

        return True


class PullRequest(models.Model):

    ACCEPTED, REJECTED, PENDING_VERIFICATION = 1, 2, 3
    STATES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (PENDING_VERIFICATION, "Pending Verification"),
    )

    html_url = models.URLField(verbose_name="HTML URL")

    contributor = models.ForeignKey(User, on_delete=models.CASCADE)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    state = models.PositiveSmallIntegerField(verbose_name="State", choices=STATES, default=PENDING_VERIFICATION)

    bonus = models.IntegerField(verbose_name="Bonus", default=0)

    penalty = models.IntegerField(verbose_name="Penalty", default=0)

    def __str__(self):
        return f"{self.contributor}_{self.issue}"


class IssueAssignmentRequest(models.Model):

    ACCEPTED, REJECTED, PENDING_VERIFICATION = 1, 2, 3
    STATES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (PENDING_VERIFICATION, "Pending Verification"),
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    requester = models.ForeignKey(User, on_delete=models.CASCADE)

    state = models.PositiveSmallIntegerField(verbose_name="State", choices=STATES, default=PENDING_VERIFICATION)

    def __str__(self):
        return f"{self.requester}_{self.issue}"

    def is_acceptable(self, mentor):

        requester = self.requester
        issue = self.issue
        actual_mentor = issue.mentor

        if mentor.username != actual_mentor.username:
            return False

        if self.state != self.PENDING_VERIFICATION:  # If this Issue Request was already Accepted/Rejected
            return False

        active_count = ActiveIssue.objects.filter(contributor=requester, issue=issue).count()

        if active_count >= MAX_SIMULTANEOUS_ISSUE:
            return False

        return True


class ActiveIssue(models.Model):

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    contributor = models.ForeignKey(User, on_delete=models.CASCADE)

    assigned_at = models.DateTimeField(verbose_name="Decided At", default=timezone.now)

    def __str__(self):
        return f"{self.contributor}_{self.issue}"

    def can_raise_pr(self, contributor):

        if contributor != self.contributor:
            return False

        if self.issue.state == self.issue.CLOSED:  # If this Issue has been closed
            return False

        all_prs = PullRequest.objects.filter(contributor=contributor, issue=self.issue,
                                             state=PullRequest.PENDING_VERIFICATION)

        if all_prs:  # If there is already a pending PR for this user and issue
            return False

        return True

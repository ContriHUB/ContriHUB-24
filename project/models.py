from django.db import models
from django.contrib.auth import get_user_model
from contrihub.settings import MAX_SIMULTANEOUS_ISSUE, DAYS_PER_ISSUE_FREE, DAYS_PER_ISSUE_EASY, DAYS_PER_ISSUE_MEDIUM, \
    DAYS_PER_ISSUE_HARD, DAYS_PER_ISSUE_VERY_EASY
from django.utils import timezone
from datetime import timedelta, datetime

User = get_user_model()


class Domain(models.Model):

    name = models.CharField(max_length=56, null=True)

    def __str__(self):
        return self.name


class SubDomain(models.Model):

    name = models.CharField(max_length=56, null=True)

    def __str__(self):
        return self.name


class Project(models.Model):

    name = models.CharField(verbose_name="Name", max_length=200)

    api_url = models.URLField(verbose_name="API URL")

    html_url = models.URLField(verbose_name="HTML URL")

    domain = models.ForeignKey(Domain, on_delete=models.DO_NOTHING, null=True, default=None)

    def __str__(self):
        return self.name


class SubDomainProject(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    sub_domain = models.ForeignKey(SubDomain, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.project.name + ' -> ' + self.sub_domain.name


class Issue(models.Model):
    FREE, EASY, MEDIUM, HARD, VERY_EASY = 0, 1, 2, 3, 4
    FREE_READ, VERY_EASY_READ, EASY_READ, MEDIUM_READ, HARD_READ = "Free", "Very-Easy", "Easy", "Medium", "Hard"  # Human Readable Names
    LEVELS = (
        (FREE, FREE_READ),  # (Value, Human Readable Name)
        (VERY_EASY, VERY_EASY_READ),
        (EASY, EASY_READ),
        (MEDIUM, MEDIUM_READ),
        (HARD, HARD_READ),
    )

    OPEN, CLOSED = 1, 3
    STATES = (
        (OPEN, "Open"),
        (CLOSED, "Closed"),
    )

    number = models.IntegerField(verbose_name="Number", default=0)

    title = models.CharField(verbose_name="Title", max_length=200)

    # Issue description
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    api_url = models.URLField(verbose_name="API URL")  # CAUTION: May contain inconsistent values, do not use this

    html_url = models.URLField(verbose_name="HTML URL")

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    mentor = models.ForeignKey(User, related_name="mentor", on_delete=models.DO_NOTHING, null=True)

    # 1-Easy, 2-Medium, 3-Hard, 4-Very-Easy
    level = models.PositiveSmallIntegerField(verbose_name='Level', choices=LEVELS, default=1)

    points = models.IntegerField(verbose_name="Points", default=0)

    # 1 - Open, 0 - Closed
    state = models.PositiveSmallIntegerField('State', choices=STATES, default=1)

    # Restricted only for BTech 2nd yr and MCA 2nd yr.
    is_restricted = models.BooleanField(verbose_name='Is Restricted', default=False)

    bonus_value = models.CharField(verbose_name="Bonus Value", max_length=200, default="0")

    bonus_description = models.CharField(verbose_name="Bonus Description", max_length=200, default="")

    upvotes = models.ManyToManyField(User, related_name="upvotes", blank=True)

    downvotes = models.ManyToManyField(User, related_name="downvotes", blank=True)

    def __str__(self):
        return self.title

    def is_assignable(self, requester):

        if self.state == self.CLOSED:
            return False, "The Issue is Closed Already."

        is_active = ActiveIssue.objects.filter(issue=self)

        if is_active:  # If this issue is already assigned to someone currently
            return False, "This issue is already assigned to someone else currently"

        is_already_requested = IssueAssignmentRequest.objects.filter(issue=self,
                                                                     state=IssueAssignmentRequest.PENDING_VERIFICATION)

        if is_already_requested:  # Current requester has already requested it and is pending.
            return False, f"This issue has been already requested by @{is_already_requested.first().requester}"

        # TEST: Start
        requester_requests_count = IssueAssignmentRequest.objects.filter(requester=requester,
                                                                         state=IssueAssignmentRequest.PENDING_VERIFICATION).count()
        requester_active_issue_count = ActiveIssue.objects.filter(contributor=requester).count()
        if requester_requests_count + requester_active_issue_count >= MAX_SIMULTANEOUS_ISSUE:
            return False, f"Your Max-Simultaneous-Issue-Engagement-Count(2) Reached. Total Pending Requests:- {requester_active_issue_count}, Total Active Issues Count:- {requester_active_issue_count}"
        # TEST: End

        profile = requester.userprofile

        if profile.role != profile.STUDENT:  # Issues can be assigned to Student Role only
            return False, f"Whoa! You are not a Student."

        if profile.current_year == profile.FINAL:  # Final Year Students not allowed
            return False, f"Hehe! Have a chill pill, vro. It's Final year"

        if self.is_restricted or self.level == self.VERY_EASY:
            if profile.course in (profile.M_TECH, profile.M_SC, profile.PHD):
                return False, f"Sorry! M.Tech, M.Sc and Phd Student not allowed."

            if profile.course == profile.B_TECH:
                if profile.current_year in (profile.THIRD, profile.FINAL):
                    return False, f"Sorry! B.Tech Third Year Student cannot take this issue."

            if profile.course == profile.MCA:
                if profile.current_year in (profile.THIRD, profile.FINAL):
                    return False, f"Sorry! MCA Final Year Student cannot take this issue."

        return True, f"Success."

    def get_issue_days_limit(self):
        if self.level == self.FREE:
            return DAYS_PER_ISSUE_FREE
        elif self.level == self.VERY_EASY:
            return DAYS_PER_ISSUE_VERY_EASY
        elif self.level == self.EASY:
            return DAYS_PER_ISSUE_EASY
        elif self.level == self.MEDIUM:
            return DAYS_PER_ISSUE_MEDIUM
        elif self.level == self.HARD:
            return DAYS_PER_ISSUE_HARD


class PullRequest(models.Model):
    ACCEPTED, REJECTED, PENDING_VERIFICATION = 1, 2, 3
    BONUS, PENALTY = "bonus", "penalty"
    STATES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (PENDING_VERIFICATION, "Pending Verification"),
    )

    pr_link = models.URLField(verbose_name="PR Link")

    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_query_name='contributor')

    remark = models.CharField(max_length=50, blank=True)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    state = models.PositiveSmallIntegerField(verbose_name="State", choices=STATES, default=PENDING_VERIFICATION)

    bonus = models.IntegerField(verbose_name="Bonus", default=0)

    penalty = models.IntegerField(verbose_name="Penalty", default=0)

    submitted_at = models.DateTimeField(verbose_name="Submitted At", default=timezone.now)

    def __str__(self):
        return f"{self.contributor}_{self.issue}"

    class Meta:
        ordering = ['-state', 'submitted_at']

    def accept(self, bonus, penalty, remark):
        """
        Method to accept (verify) PR.
        :param bonus:
        :param penalty:
        :return:
        """

        # Updating this PR
        self.state = self.ACCEPTED
        self.bonus = int(bonus)
        self.penalty = int(penalty)
        self.remark = remark
        self.save()

        # Updating related Issue
        self.issue.state = self.issue.CLOSED
        self.issue.save()

        # Updated accepted pr req. of current user
        accepted_pr_count = PullRequest.objects.filter(contributor=self.contributor, state=self.ACCEPTED).count()

        # Updating Contributor's Profile
        contributor_profile = self.contributor.userprofile
        contributor_profile.total_points += (int(self.issue.points) + int(bonus) - int(penalty))
        contributor_profile.bonus_points += int(bonus)
        contributor_profile.deducted_points += int(penalty)
        contributor_profile.issues_solved = accepted_pr_count
        contributor_profile.save()

        # Deleting Active Issue related to this PR
        active_issue = ActiveIssue.objects.filter(issue=self.issue, contributor=self.contributor)
        if active_issue:
            active_issue[0].delete()
        # try:
        #     self.issue.activeissue_set.first().delete()
        # except AttributeError:
        #     pass

    def reject(self, bonus, penalty, remark):
        """
        Method to reject (verify) PR.
        :param bonus:
        :param penalty:
        :return:
        """

        # Updating this PR
        self.state = self.REJECTED
        self.bonus = int(bonus)
        self.penalty = int(penalty)
        self.remark = remark
        self.save()

        # Updating Contributor's Profile
        contributor_profile = self.contributor.userprofile
        contributor_profile.total_points += (int(bonus) - int(penalty))
        contributor_profile.bonus_points += int(bonus)
        contributor_profile.deducted_points += int(penalty)
        contributor_profile.save()

        # Deleting Active Issue related to this PR
        active_issue = ActiveIssue.objects.filter(issue=self.issue, contributor=self.contributor)
        if active_issue:
            active_issue[0].delete()

        # try:
        #     self.issue.activeissue_set.first().delete()
        # except AttributeError:
        #     pass


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

    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.requester}_{self.issue}"

    class Meta:
        ordering = ['-state', 'created_on']

    def is_acceptable(self, mentor):

        requester = self.requester
        issue = self.issue
        actual_mentor = issue.mentor

        if mentor.username != actual_mentor.username:
            return False

        if self.state != self.PENDING_VERIFICATION:  # If this Issue Request was already Accepted/Rejected
            return False

        is_active = ActiveIssue.objects.filter(issue=self.issue)

        if is_active:  # If this issue is already assigned to someone currently
            return False

        active_count = ActiveIssue.objects.filter(contributor=requester).count()

        if active_count >= MAX_SIMULTANEOUS_ISSUE:  # If this requester is already working on MAX_SIMULTANEOUS_ISSUE
            # issues
            return False

        return True


class ActiveIssue(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    contributor = models.ForeignKey(User, on_delete=models.CASCADE)

    assigned_at = models.DateTimeField(verbose_name="Assigned At", default=timezone.now)

    def __str__(self):
        return f"{self.contributor}_{self.issue}"

    def can_raise_pr(self, contributor):

        if contributor != self.contributor:
            return False

        if self.issue.state == self.issue.CLOSED:  # If this Issue has been closed
            return False

        is_pending = PullRequest.objects.filter(contributor=contributor, issue=self.issue,
                                                state=PullRequest.PENDING_VERIFICATION)
        is_accepted = PullRequest.objects.filter(contributor=contributor, issue=self.issue,
                                                 state=PullRequest.ACCEPTED)

        if is_pending or is_accepted:  # If there is already a pending PR for this user and issue
            return False

        return True

    # TODO: ISSUE: Rename this function to 'get_deadline' as it is more suitable. Don't Forget to update name at all
    #  places.
    def get_remaining_time(self):
        return self.assigned_at + timezone.timedelta(days=self.issue.get_issue_days_limit())
    def check_last_hour(self):
        current_time = timezone.now()
        deadline = self.assigned_at + timedelta(days=self.issue.get_issue_days_limit())
        last_hour = deadline - timedelta(hours = 1)
        if(last_hour<current_time<deadline):
            return True
        return False
    

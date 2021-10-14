from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

User = get_user_model()


class UserProfile(models.Model):

    STUDENT, MENTOR, ADMIN = 1, 2, 3
    ROLES = (
        (STUDENT, 'Student'),
        (MENTOR, 'Mentor'),
        (ADMIN, 'Admin'),
    )

    B_TECH, MCA, M_TECH, M_SC, PHD = 1, 2, 3, 4, 5
    B_TECH_READ, MCA_READ, M_TECH_READ, M_SC_READ, PHD_READ = 'B.Tech', 'M.C.A', 'M.Tech', 'M.Sc', 'P.H.D'
    COURSES = (
        (B_TECH, B_TECH_READ),
        (MCA, MCA_READ),
        (M_TECH, M_TECH_READ),
        (M_SC, M_SC_READ),
        (PHD, PHD_READ),
    )

    FIRST, SECOND, THIRD, FINAL = 1, 2, 3, 4
    FIRST_READ, SECOND_READ, THIRD_READ, FINAL_READ = 'First', 'Second', 'Third', 'Final'
    YEARS = (
        (FIRST, FIRST_READ),
        (SECOND, SECOND_READ),
        (THIRD, THIRD_READ),
        (FINAL, FINAL_READ),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    registration_no = models.CharField(verbose_name='Registration Number', max_length=10, default='')

    ms_teams_id = models.EmailField(verbose_name="MS Teams ID", default='')

    # TODO:ISSUE Add a field to take What'sapp Number with all checks (External App can be used)
    whatsapp_no = PhoneNumberField(verbose_name='Whatsapp Number', default='', blank=False, null=False)

    course = models.PositiveSmallIntegerField(verbose_name='Course', choices=COURSES, default=B_TECH)

    current_year = models.PositiveSmallIntegerField(verbose_name='Current Year', choices=YEARS, default=FIRST)

    role = models.IntegerField(verbose_name='Role', choices=ROLES, default=STUDENT)

    issues_solved = models.IntegerField(verbose_name='Issues Solved', default=0)

    total_points = models.IntegerField(verbose_name='Points', default=0)

    bonus_points = models.IntegerField(verbose_name='Bonus Points', default=0)

    deducted_points = models.IntegerField(verbose_name='Deducted Points', default=0)

    is_complete = models.BooleanField(verbose_name="Is Complete", default=False)

    def __str__(self):
        return self.user.username

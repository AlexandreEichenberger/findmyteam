from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# create custom validation

def validate_first_program(value):
    if value == Team.UNSPECIFIED:
        raise ValidationError("failed to define a first program")
    
# Create your models here.

class Team(models.Model):
    UNSPECIFIED = '-'
    JFLL = 'J'
    FLL = 'L'
    FTC = 'T'
    FRC = 'R'
    FIRST_PROGRAM = (
        (UNSPECIFIED, '-'),
        (JFLL, 'jFLL'),
        (FLL, 'FLL'),
        (FTC, 'FTC'),
        (FRC, 'FRC'),
    )
    # info about team
    first_program = models.CharField(
        max_length=1,
        choices=FIRST_PROGRAM,
        default=UNSPECIFIED,
        validators=[validate_first_program]
    )
    username = models.CharField(max_length=200)
    team_name = models.CharField(max_length=200, help_text="Enter the name of your team.")
    team_number = models.IntegerField(blank=True, null=True, help_text="Enter the team of your team. Prospective teams, established jFLL, or established FLL teams can leave the field blank.")
    school_district_name = models.CharField(max_length=200, blank=True, null=True, help_text="Enter the name of your school district if your team is restricted to members living in the district. Otherwise, leave the field blank.")
    town_name = models.CharField(max_length=200, editable=False)
    zip_code = models.PositiveSmallIntegerField(help_text="5 digit ZIP code of where you meet.")
    year_founded = models.PositiveSmallIntegerField(blank=True, null=True, help_text="Enter the year that your team was founded. Leave field blank for prospective teams.")
    description = models.TextField(max_length=2000, help_text="Enter a brief team's description and include your team's objectives.")
    achievement = models.TextField(max_length=1000, help_text="Describe your recent achievements.")
    web_site = models.URLField(max_length=200, blank=True, null=True, help_text="Enter the URL of your team online presence.")
    # what is the team looking for
    looking_for_teammate = models.BooleanField(default=True, help_text="Select if you are actively looking for new teammates. Only then will you receive messages from prospective team members.")
    prospective_teammate_profile = models.CharField(max_length=200, blank=True, null=True, help_text="Optional description of the profile of prospective teammates.")
    looking_to_mentor_another_team = models.BooleanField(default=False, help_text="Select if you are interested in mentoring another team. Only then will you receive messages from prospective teams.")
    prospective_team_profile = models.CharField(max_length=200, blank=True, null=True, help_text="Optional description of the profile of prospective teams that you are interested in mentoring.")
    looking_for_mentorship = models.BooleanField(default=False, help_text="Select if you are interested being mentored by another team. Only then will you receive message from prospective expert teams.")
    help_request = models.CharField(max_length=200, blank=True, null=True, help_text="Optional description of the expertise you would like to get help with.")
    # stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField(default=0, editable=False)
    looking_request_count = models.PositiveIntegerField(default=0, editable=False)
    requested_count = models.PositiveIntegerField(default=0, editable=False)
    #methods
    def __str__(self):
        if self.team_number:
            return "%s-%d %s" %(self.first_program, self.team_number, self.team_name)
        else:
            return "%s %s" %(self.first_program, self.team_name)

class Person(models.Model):
    # info about person
    username = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=200, help_text="Enter the name of the child's guardian.")
    child_name = models.CharField(max_length=200, help_text="Enter the name of the child that you are looking for a team.")
    child_interest = models.TextField(max_length=1000, help_text="Enter your child's interest and relevant experience.")
    school_district_name = models.CharField(max_length=200, help_text="Enter the name of your child's school district. Some school-based teams are restricted to children in the district.")
    town_name = models.CharField(max_length=200, editable=False)
    zip_code = models.PositiveSmallIntegerField(help_text="5 digit ZIP code of where you live.")
    years_of_FIRST_experience = models.PositiveSmallIntegerField(default=0, help_text="Enter the number of seasons that your child has participated in FIRST programs.")
    # what is child looking for
    interested_in_jFLL = models.BooleanField(default=False, help_text="Select if your child is interested in joining a Junior FIRST Lego League (jFLL) team.")
    interested_in_FLL  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Lego League (FLL) team.")    
    interested_in_FTC  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Tech Challenge (FTC) team.")    
    interested_in_FRC  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Robotics Competition (FRC) team.")    
    # stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField(editable=False)
    looking_request_count = models.PositiveIntegerField(editable=False)
    requested_count = models.PositiveIntegerField(editable=False)
    def __str__(self):
        return self.child_name

from django.db import models

# Create your models here.
from django.db import models

class Team(models.Model):
    FLL = 'L'
    FTC = 'T'
    FRC = 'R'
    FIRST_PROGRAM = (
        (FLL, 'FLL'),
        (FTC, 'FTC'),
        (FRC, 'FRC'),
    )
    # info about team
    first_program = models.CharField(
        max_length=1,
        choices=FIRST_PROGRAM,
        default=FLL,
    )
    username = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    number = models.IntegerField(default=0)
    school_base_team = models.BooleanField()
    school_district_or_town_name = models.CharField(max_length=200)
    zip_code = models.PositiveSmallIntegerField(default=0)
    year_founded = models.PositiveSmallIntegerField(default=2017)
    description = models.TextField(max_length=1000)
    achievement = models.TextField(max_length=1000)
    web_site = models.URLField(max_length=200)
    # what is the team looking for
    looking_for_teammate = models.BooleanField()
    looking_for_teammate_stem_project = models.BooleanField()
    looking_for_teammate_build = models.BooleanField()
    looking_for_teammate_prog = models.BooleanField()
    looking_for_teammate_outreach = models.BooleanField()
    looking_for_mentoring_opportunities = models.BooleanField()
    looking_for_outreach_opportunities = models.BooleanField()
    # stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField()
    looking_request_count = models.PositiveIntegerField()
    requested_count = models.PositiveIntegerField()

class Person(models.Model):
    # info about person
    username = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=200)
    child_name = models.CharField(max_length=200)
    child_interest = models.TextField(max_length=1000)
    school_district_or_town_name = models.CharField(max_length=200)
    zip_code = models.PositiveSmallIntegerField(default=0)
    years_of_FIRST_experience = models.PositiveSmallIntegerField(default=0)
    # what is child looking for
    interested_in_stem_project = models.BooleanField()
    interested_in_building = models.BooleanField()
    interested_in_programming = models.BooleanField()
    interested_in_outreach = models.BooleanField()
    # stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField()
    looking_request_count = models.PositiveIntegerField()
    requested_count  = models.PositiveIntegerField()

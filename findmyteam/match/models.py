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
    first_program = models.CharField(
        max_length12,
        choices=FIRST_PROGRAM,
        default=FLL,
    )
    name = models.CharField(max_length=200)
    number = models.IntegerField(default=0)
    school_base = models.BooleanField()
    district_town_name = models.CharField(max_length=200)
    zip_code = models.PositiveSmallIntegerField(default=0)
    year_founded = models.PositiveSmallIntegerField(default=2017)
    mission = models.TextField(max_length=1000)
    achievement = models.TextField(max_length=1000)
    web_site = model.URLField(max_length=200)
    looking_teammate_new = models.BooleanField()
    looking_teammate_stem = models.BooleanField()
    looking_teammate_build = models.BooleanField()
    looking_teammate_prog = models.BooleanField()
    looking_teammate_outreach = models.BooleanField()
    looking_mentoring = models.BooleanField()
    looking_outreach = models.BooleanField()

    

from django import forms
from django.db import models
from django.db.models import DEFERRED
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import get_object_or_404


from uszipcode import ZipcodeSearchEngine
from dateutil.relativedelta import relativedelta
import datetime
from math import radians, cos, sin, asin, sqrt

# globals
invite_expiration_in_days = 7
max_initiated_invite = 20

# print help

def display_conjunction_list(conjunction, list): # list = [[pred, name], ...]
  n = 0
  i = 0
  str = ""
  for logic, name in list:
    if logic:
      n+=1
  for logic, name in list:
    if logic:
      if i == 0:
        str = name
      elif i < n-1:
        str += ", " + name
      elif n == 2:
        str += " %s %s" % (conjunction, name)
      else:
        str += ", and " + name
      i += 1
  return str

def display_and_list(list):
    return display_conjunction_list("and", list)

def display_or_list(list):
    return display_conjunction_list("or", list)

def display_singular_plural(count, singular_world, plural_word):
    if count > 1:
        return plural_word
    else:
        return singluar_word

def display_pluralized(count, singular_word):
    return display_singular_plural(count, singular_word, singular_word + "s")

# distance

AVG_EARTH_RADIUS = 6371  # in km

def great_circle(point1, point2, miles=True):
    """ Calculate the great-circle distance bewteen two points on the Earth surface.
    :input: two 2-tuples, containing the latitude and longitude of each point
    in decimal degrees.
    Example: haversine((45.7597, 4.8422), (48.8567, 2.3508))
    :output: Returns the distance bewteen the two points.
    The default unit is kilometers. Miles can be returned
    if the ``miles`` parameter is set to True.
    """
    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = list(map(radians, [lat1, lng1, lat2, lng2]))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lng / 2) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * 0.621371  # in miles
    else:
        return h  # in kilometers

# create custom validation

def validate_user_type(value):
    if value == User.UNSPECIFIED:
        raise ValidationError("Please select a valid type of account.")

def validate_first_program(value):
    if value == Team.UNSPECIFIED:
        raise ValidationError("Please select a valid First program.")

def validate_team_type(value):
    if value == Team.UNSPECIFIED:
        raise ValidationError("Please select a valid team type.")

def validate_zip_code(value):
    zipcode_search_engine = ZipcodeSearchEngine()
    info = zipcode_search_engine.by_zipcode(value)
    if info.City == None:
        raise ValidationError("This zipcode is not a valid US zip code.")


################################################################################
# extension to user model

class Profile(models.Model):
    # extend user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    UNSPECIFIED = '-'
    PERSON = 'P'
    TEAM   = 'T'
    ORG    = 'O'
    # type
    TYPE= (
        (UNSPECIFIED, '-'),
        (PERSON, 'Account for a person'),
        (TEAM, 'Account for a team'),
        (ORG, 'Account for a charitable organization'),
        )
    type = models.CharField(
        max_length=1,
        choices=TYPE,
        default=UNSPECIFIED
        )
    # reference
    UNDEFINED_ID = -1
    specific_profile_id = models.IntegerField(default=UNDEFINED_ID)
    # computed stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField(default=0)
    looking_request_count = models.PositiveIntegerField(default=0)
    requested_count = models.PositiveIntegerField(default=0)
    accepted_count = models.PositiveIntegerField(default=0)

    # methods
    def __str__(self):
        return self.user.username

    def update_info(self):
        print("update profile info for %s" % self.user.username)
        self.last_update = datetime.datetime.now()
        self.update_count += 1

    def init_info(self, type, id):
        print("init profile info for %s with type %s and id %s" % (self.user.username, type, id))
        self.type = type
        self.specific_profile_id = id
        self.first_update = datetime.datetime.now()
        self.update_count = 0
        self.looking_request_count = 0
        self.requested_count = 0
        self.accepted_count = 0
        self.update_info()
        
    def is_person(self):
        return self.type == self.PERSON

    def is_team(self):
        return self.type == self.TEAM

    def is_unspecified(self):
        return self.type == self.UNSPECIFIED

    def get_person(self):
        if self.is_person():
            return get_object_or_404(Person, id=self.specific_profile_id)
        raise Http404("Get for person for a non-person.")
        
    def get_team(self):
        if self.is_team():
            return get_object_or_404(Team, id=self.specific_profile_id)
        raise Http404("Get team details for a non-team.")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

################################################################################
# Person

class Person(models.Model):
    # info about person
    username = models.CharField(max_length=200, default="")
    guardian_name = models.CharField(max_length=200,
        help_text="Enter the name of the child's guardian.")
    child_name = models.CharField(max_length=200,
        help_text="Enter the name of the child that you are looking a team for.")
    child_interest = models.TextField(max_length=1000,
        help_text="Enter your child's interest and relevant experience. Text should read as a paragraph.")
    school_district_name = models.CharField(max_length=200,
        help_text="Enter the name of your child's school district. Some school-based teams restricts membership to children in the district.")
    years_of_FIRST_experience = models.PositiveSmallIntegerField(default=0,
        help_text="Enter the number of seasons that your child has participated in FIRST programs.")
    zip_code = models.PositiveSmallIntegerField(validators=[validate_zip_code],
        help_text="5 digit ZIP code of where you live.")
    # computed location data
    town_name = models.CharField(max_length=50, blank=True, default="")
    state_name = models.CharField(max_length=2, blank=True, default="")
    latitude = models.FloatField(default=0.0, blank=True)
    longitude = models.FloatField(default=0.0, blank=True)    
    # what is child looking for
    interested_in_jFLL = models.BooleanField(default=False,
        help_text="Select if your child is interested in joining a Junior FIRST Lego League (jFLL) team.")
    interested_in_FLL  = models.BooleanField(default=False,
        help_text="Select if your child is interested in joining an FIRST Lego League (FLL) team.")    
    interested_in_FTC  = models.BooleanField(default=False,
        help_text="Select if your child is interested in joining an FIRST Tech Challenge (FTC) team.")    
    interested_in_FRC  = models.BooleanField(default=False,
        help_text="Select if your child is interested in joining an FIRST Robotics Competition (FRC) team.") 
    
    # methods
    def __str__(self):
        return "%s-%s" % (self.username, self.child_name)

    def child_team_interest_description(self, positive_pre_sentence, negative_pre_sentence):
        if self.interested_in_jFLL or self.interested_in_FLL or self.interested_in_FTC or self.interested_in_FRC:
            str = positive_pre_sentence + " "
            str += display_or_list([[self.interested_in_jFLL, "junior FLL"],
                    [self.interested_in_FLL, "FLL"], [self.interested_in_FTC, "FTC"],
                    [self.interested_in_FRC, "FRC"]])
            return str + " team"
        else:
            return negative_pre_sentence

    def child_team_interest(self):
        return "Child is %s. " % self.child_team_interest_description("interested in",
            "not currently interested in joining a new team.  ")
    
    def child_description(self):
        str = "A child from %s, %s, is %s.  " % (self.town_name, self.state_name,
            self.child_team_interest_description("looking for a", "not currently looking for a"))
        str += "The child lives in the %s school district" % self.school_district_name
        if self.years_of_FIRST_experience > 0:
            str += " and has %d %s of FIRST experience. " % (self.years_of_FIRST_experience,
                display_pluralized(self.years_of_FIRST_experience, "year"))
        else:
            str += ".  "
        return str

    def update_info(self, username):
        print("update person info for %s" % username)
        self.username = username
        info = ZipcodeSearchEngine().by_zipcode(self.zip_code)
        self.town_name = info.City
        self.state_name = info.State
        self.latitude = info.Latitude
        self.longitude = info.Longitude

    def distance_from(self, other_latitude, other_longitude):
        return great_circle([self.latitude, self.longitude], [other_latitude, other_longitude])        

class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['guardian_name', 'child_name','child_interest','school_district_name','zip_code','years_of_FIRST_experience','interested_in_jFLL','interested_in_FLL','interested_in_FTC','interested_in_FRC'] 



################################################################################
# Team

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
        validators=[validate_first_program],
        help_text="Enter the FIRST program of your team."
    )
    username = models.CharField(max_length=200, default="")
    team_name = models.CharField(max_length=200, help_text="Enter the name of your team.")
    team_number = models.IntegerField(blank=True, null=True,
        help_text="Enter the team number of your team. Prospective teams, established jFLL, or established FLL teams may leave the field blank.")
    SCHOOL = 'S'
    CLUB_4H = 'H'
    BOY_SCOUT = 'B'
    GIRL_SCOUT = 'G'
    OTHER = 'O'
    TEAM_TYPE = (
        (UNSPECIFIED, '-'),
        (SCHOOL, 'school based'),
        (CLUB_4H, '4H club'),
        (BOY_SCOUT, 'boy scout'),
        (GIRL_SCOUT, 'girl scout'),
        (OTHER, 'other')
    )
    team_type = models.CharField(
        max_length=1,
        choices=TEAM_TYPE,
        default=UNSPECIFIED,
        validators=[validate_team_type],
        help_text="Enter the type of association that your team is part of.  School-based teams typically restrict membership to children living in the school district."
    )
    school_district_name = models.CharField(max_length=200, blank=True, null=True,
        help_text="Enter the name of your school district if your team is a school-based team. Otherwise, leave the field blank.")
    year_founded = models.PositiveSmallIntegerField(blank=True, null=True,
        help_text="Enter the year that your team was founded. Leave field blank for prospective teams.")
    description = models.TextField(max_length=2000,
        help_text="Enter a brief team's description and include your team's objectives. Text shoud read as a paragraph.")
    achievement = models.TextField(max_length=1000,
        help_text="Describe your recent achievements. Text should read as a paragraph.")
    web_site = models.URLField(max_length=200, blank=True, null=True,
        help_text="Enter the URL of your team online presence.")
    zip_code = models.PositiveSmallIntegerField(validators=[validate_zip_code],
        help_text="5 digit ZIP code of where you meet.")
    # computed location info
    town_name = models.CharField(max_length=50, blank=True, default="")
    state_name = models.CharField(max_length=2, blank=True, default="")
    latitude = models.FloatField(default=0.0, blank=True)
    longitude = models.FloatField(default=0.0, blank=True)    
    # what is the team looking for
    looking_for_teammate = models.BooleanField(default=True,
        help_text="Select if you are actively looking for new teammates. Only then will you receive messages from prospective team members.")
    prospective_teammate_profile = models.CharField(max_length=200, blank=True, null=True,
        help_text="Optional description of the profile of prospective teammates.")
    looking_to_mentor_another_team = models.BooleanField(default=False,
        help_text="Select if you are offering to mentor another team. Only then will you receive messages from prospective teams.")
    prospective_team_profile = models.CharField(max_length=200, blank=True, null=True,
        help_text="Optional description of the profile of prospective teams that you are interested in mentoring.")
    looking_for_mentorship = models.BooleanField(default=False,
        help_text="Select if you are seeking mentorship by another team. Only then will you receive message from prospective expert teams.")
    help_request = models.CharField(max_length=200, blank=True, null=True,
        help_text="Optional description of the expertise you would like to get help with.")
    
    #methods
    def __str__(self):
        return "%s-%s-%s" %(self.username, self.team_number_description(), self.team_name)

    def team_number_description(self):
        if self.team_number:
            return "%s%d" %(self.get_first_program_display(), self.team_number)
        else:
            return "%s" %(self.get_first_program_display())
                     
    def team_age_description(self):
        current = datetime.datetime.now().year
        if self.year_founded == None:
            return "prospective "
        elif self.year_founded == current:
            return "rookie "
        else:
            return "%d-year-old " % (current - self.year_founded)
    
    def team_description(self):
        str = "Team %s is a %s %s team based in %s, %s, " % (self.team_name, self.team_age_description(), self.get_first_program_display(), self.town_name, self.state_name)
        if self.team_type == self.SCHOOL and self.school_district_name != None:
            str += "and affiliated with the %s school district. " % self.school_district_name
        else:
            str += "and is run as a club-team.  "
        return str
    
    def team_needs(self):
        str = "The team is "
        if self.looking_for_teammate or self.looking_to_mentor_another_team or self.looking_for_mentorship:
            str += "currently looking for "
            str += display_and_list([[self.looking_for_teammate, "new teammates"],
                              [self.looking_to_mentor_another_team, "mentoring opportunities"],
                              [self.looking_for_mentorship, "other team to provide mentorship"]])
            str += ".  "
        else:
            str += "not currently looking for new teammates or mentoring opportunities.  "
        return str

    def update_info(self, username):
        print("update team info for %s" % username)
        self.username = username
        info = ZipcodeSearchEngine().by_zipcode(self.zip_code)
        self.town_name = info.City
        self.state_name = info.State
        self.latitude = info.Latitude
        self.longitude = info.Longitude

    def distance_from(self, other_latitude, other_longitude):
        return great_circle([self.latitude, self.longitude], [other_latitude, other_longitude])        
        
class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['first_program', 'team_name', 'team_number', 'team_type', 'school_district_name', 'zip_code', 'year_founded', 'description', 'achievement', 'web_site', 'looking_for_teammate', 'prospective_teammate_profile', 'looking_to_mentor_another_team', 'prospective_team_profile', 'looking_for_mentorship', 'help_request'] 
 

################################################################################

class Invite(models.Model):
    # info about person
    invitor_username = models.CharField(max_length=200)
    prospective_username = models.CharField(max_length=200)
    date_invited = models.DateField(auto_now_add=True)
    date_response = models.DateField(blank=True, null=True)
    P2T = 'P'
    T2P = 'T'
    T2M = 'H'
    M2T = 'M'
    INVITE_TYPE = (
        (P2T, 'person to team'),
        (T2P, 'team to person'),
        (T2M, 'team seeking mentorship'),
        (M2T, 'team offering to mentor a team'),
    )
    # invite type
    type = models.CharField(max_length=1, choices=INVITE_TYPE, default=P2T)
    INITIATED = 'I'
    ACCEPTED = 'A'
    DECLINED = 'D'
    OLD_DECLINED = 'O'
    EXPIRED = 'E'
    STATUS = (
        (INITIATED, 'initiated'),
        (ACCEPTED, 'accepted'),
        (DECLINED, 'declined'),
        (OLD_DECLINED, 'declined that has now expired'),
        (EXPIRED, 'expired'),
    )
    # invite status
    status = models.CharField(max_length=1, choices=STATUS, default=INITIATED)
    # methods

    def __str__(self):
        return "%s-%s-%s" % (self.invitor_username, self.prospective_username,
                             self.get_type_display())
    
    @classmethod
    def create(cls, invitor_username, prospective_username, type):
        invite = cls(invitor_username=invitor_username,
            prospective_username=prospective_username, type=type)
        return invite

    @classmethod
    def find_identical_pending_invite(cls, invitor_username, prospective_username, type):
        # does same invite already exists?
        qs = cls.objects.filter(invitor_username=invitor_username,
            prospective_username=prospective_username, type=type)
        for i in qs:
            # ignore completed requests
            if not i.completed():
                print("find request that was not completed %s %s" % (invitor_username,
                    prospective_username))
                return i
        return None

    @classmethod
    def pending_invite_num(cls, invitor_username):
        # does same invite already exists?
        qs = cls.objects.filter(invitor_username=invitor_username)
        num = 0
        for i in qs:
            # ignore completed requests
            if not i.completed():
                num += 1
        return num

    # invite offers exired after a number of days
    def expired(self, factor):
        today = datetime.date.today()
        today_num = today.year * 365 + today.month * 31 + today.day
        old_num = self.date_invited.year * 365 + self.date_invited.month * 31 + self.date_invited.day
        delta = today_num - old_num
        if delta > factor * invite_expiration_in_days:
            return True
        return False
    
    # completed if accepted / declined / expired. Check conditions for expired
    def completed(self):
        # check new expired
        if self.status == self.INITIATED and self.expired(1):
            self.status = self.EXPIRED
            self.save()
        if self.status == self.DECLINED and self.expired(2):
            self.status = self.OLD_DECLINED
            self.save()
        if self.status == self.ACCEPTED or self.status == self.OLD_DECLINED or self.status == self.EXPIRED:
            return True
        return False

    def team_email_and_name(self, tusername):
        try:
            team = Team.objects.get(username=tusername)
            user = User.objects.get(username=tusername)
            print("got team %s %s" % (user.email, team.team_name))
            return (user.email, team.team_name)
        except:
            return None

    def person_email_and_name(self, pusername):
        try:
            person = Person.objects.get(username=pusername)
            user = User.objects.get(username=pusername)
            print("got user %s %s" % (user.email, person.guardian_name))
            return (user.email, person.guardian_name)
        except:
            return None
            
    def email_and_name_pairs(self):
        if self.type == self.P2T:
            p = self.person_email_and_name(self.invitor_username)
            t = self.team_email_and_name(self.prospective_username)
            if p and t:
                return p + t
        elif self.type == self.T2P:
            t = self.team_email_and_name(self.invitor_username)
            p = self.person_email_and_name(self.prospective_username)
            if p and t:
                return p + t
        else:
            t1 = self.team_email_and_name(self.invitor_username)
            t2 = self.team_email_and_name(self.prospective_username)
            if t1 and t2:
                return t1 + t2
        return None

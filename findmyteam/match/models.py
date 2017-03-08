from django.db import models
from django.db.models import DEFERRED
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from uszipcode import ZipcodeSearchEngine
from dateutil.relativedelta import relativedelta
import datetime
from math import radians, cos, sin, asin, sqrt

# print help

# [[pred, name], ...]
def display_conjunction_list(conjunction, list):
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

def validate_first_program(value):
    if value == Team.UNSPECIFIED:
        raise ValidationError("Please select a valid First program.")

def validate_zip_code(value):
    zipcode_search_engine = ZipcodeSearchEngine()
    info = zipcode_search_engine.by_zipcode(value)
    if info.City == None:
        raise ValidationError("This zipcode is not a valid US zip code.")

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
    school_based_team = models.BooleanField(default=False, help_text="Select if your team is restricted to members living in the school district.")
    school_district_name = models.CharField(max_length=200, blank=True, null=True, help_text="Enter the name of your school district if your team is a school-based team. Otherwise, leave the field blank.")
    zip_code = models.PositiveSmallIntegerField(validators=[validate_zip_code], help_text="5 digit ZIP code of where you meet.")
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
    #local data
    zip_code_cached = 0
    town_name = ""
    state_name = ""
    latitude = 0.0
    longitude = 0.0
    #methods
    def __str__(self):
        return "%s %s" %(self.team_number_description(), self.team_name)

    def team_number_description(self):
        if self.team_number:
            return "%s-%d" %(self.get_first_program_display(), self.team_number)
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
        self.update_zip_info()        
        str = "Team %s is a %s %s team based in %s, %s, " % (self.team_name, self.team_age_description(), self.get_first_program_display(), self.town_name, self.state_name)
        if self.school_based_team == True and self.school_district_name != None:
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
        str += "Distance from Chappaqua is %d.  " % self.distance_from(41.1693588, -73.78308609999998)
        return str
    
    def update_zip_info(self):
        zipcode_search_engine = ZipcodeSearchEngine()
        if self.zip_code_cached != self.zip_code:
            self.zip_code_cached = self.zip_code
            info = zipcode_search_engine.by_zipcode(self.zip_code)
            self.town_name = info.City
            self.state_name = info.State
            self.latitude = info.Latitude
            self.longitude = info.Longitude

    def distance_from(self, other_latitude, other_longitude):
        self.update_zip_info()
        return great_circle([self.latitude, self.longitude], [other_latitude, other_longitude])
        

class Person(models.Model):
    # info about person
    username = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=200, help_text="Enter the name of the child's guardian.")
    child_name = models.CharField(max_length=200, help_text="Enter the name of the child that you are looking a team for.")
    child_interest = models.TextField(max_length=1000, help_text="Enter your child's interest and relevant experience.")
    school_district_name = models.CharField(max_length=200, help_text="Enter the name of your child's school district. Some school-based teams are restricted to children in the district.")
    zip_code = models.PositiveSmallIntegerField(validators=[validate_zip_code], help_text="5 digit ZIP code of where you live.")
    years_of_FIRST_experience = models.PositiveSmallIntegerField(default=0, help_text="Enter the number of seasons that your child has participated in FIRST programs.")
    # what is child looking for
    interested_in_jFLL = models.BooleanField(default=False, help_text="Select if your child is interested in joining a Junior FIRST Lego League (jFLL) team.")
    interested_in_FLL  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Lego League (FLL) team.")    
    interested_in_FTC  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Tech Challenge (FTC) team.")    
    interested_in_FRC  = models.BooleanField(default=False, help_text="Select if your child is interested in joining an FIRST Robotics Competition (FRC) team.")    
    # stats
    first_update = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    update_count = models.PositiveIntegerField(default=0, editable=False)
    looking_request_count = models.PositiveIntegerField(default=0, editable=False)
    requested_count = models.PositiveIntegerField(default=0, editable=False)
    #local data
    zip_code_cached = 0
    town_name = ""
    state_name = ""
    latitude = 0.0
    longitude = 0.0
    
    # methods
    def __str__(self):
        return self.child_name

    def child_description(self):
        self.update_zip_info()        
        str = "A child from %s, %s, is " % (self.town_name, self.state_name)
        if self.interested_in_jFLL or self.interested_in_FLL or self.interested_in_FTC or self.interested_in_FRC:
            str += "looking for a "
            str += display_or_list([[self.interested_in_jFLL, "junior FLL"], [self.interested_in_FLL, "FLL"], [self.interested_in_FTC, "FTC"], [self.interested_in_FRC, "FRC"]])
            str += " team. "
        else:
            str += "not currently looking for a team.  "
        str += "The child lives in the %s school district and has %d %s of FIRST experience. " % (self.school_district_name, self.years_of_FIRST_experience, display_pluralized(self.years_of_FIRST_experience, "year"))
        return str
    
    def update_zip_info(self):
        zipcode_search_engine = ZipcodeSearchEngine()
        if self.zip_code_cached != self.zip_code:
            self.zip_code_cached = self.zip_code
            info = zipcode_search_engine.by_zipcode(self.zip_code)
            self.town_name = info.City
            self.state_name = info.State
            self.latitude = info.Latitude
            self.longitude = info.Longitude

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from uszipcode import ZipcodeSearchEngine
from uszipcode import ZipcodeSearchEngine
import datetime


# Create your views here.
from .models import Team, TeamForm, Person, PersonForm, Invite
from .models import has_team, has_person, invite_expiration_in_days, max_initiated_invite

################################################################################
# general
# dummy response return HttpResponse("Hello.")

IS_ANONYMOUS = 0
IS_PERSON = 1
IS_TEAM = 2
IS_UNINIT_ENTITY = 3

def classify(request):
    if not request.user.is_authenticated:
        return IS_ANONYMOUS
    # registered
    username = request.user.username
    if has_person(username):
        return IS_PERSON
    if has_team(username):
        return IS_TEAM
    # registered, but neiter... should set now
    return IS_UNINIT_ENTITY

def index(request):
    type = classify(request)
    if type == IS_UNINIT_ENTITY:
        return render(request, 'match/settings.html', {'is_uninit' : True})
    return render(request, 'match/index.html', {})

@login_required
def settings(request):
    type = classify(request)
    context = {}
    if type == IS_PERSON:
        context['is_person'] = True
    elif type == IS_TEAM:
        context['is_team'] = True
    else:
        context['is_uninit'] = True
    return render(request, 'match/settings.html', context)

max_travel_distance = 200

################################################################################
# person

@login_required
def person_profile(request):
    username = request.user.username
    # person cannot also have a team profile
    if has_team(username):
        return team_profile(request)
    # try to get person profile from database
    try:
        #has a person
        person = Person.objects.get(username=username)
        if request.method == "POST":
            # posted a new form, inspect
            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                person = form.save(commit=False)
                person.info_cleanup(username, False)
                person.save()
                return settings(request)
        else:
            # comming here before recieving a post
            form = PersonForm(instance=person)
        return render(request, 'match/person_profile.html', {'form': form})
        
    except:
        # does not have a person
        if request.method == "POST":
            # posted a new form, inspect
            form = PersonForm(request.POST)
            if form.is_valid():
                person = form.save(commit=False)
                person.info_cleanup(username, True)
                person.save()
                return settings(request)
        else:
            # comming here first, get the post
            form = PersonForm()
        return render(request, 'match/person_profile.html', {'form': form})

def person_viewing_team(request, tusername):
    pusername = request.user.username
    person = get_object_or_404(Person, username=pusername)
    prospective_team = get_object_or_404(Team, username=tusername)
    can_invite = True
    if Invite.find_identical_pending_invite(pusername, tusername, Invite.P2T):
        can_invite = False
    too_many_invite = ""
    if Invite.pending_invite_num(pusername) > max_initiated_invite:
        too_many_invite = "Person cannot invite prospective teams at this time as you have exceeeded the maximum of %d pending invites; invites expire within %d days" % (max_initiated_invite, invite_expiration_in_days)
    return render(request, 'match/person_viewing_team.html', {
        'prospective_team' : prospective_team, 'can_invite' : can_invite,
        'too_many_invite' : too_many_invite })

@login_required
def person_inviting_team(request, tusername):
    pusername = request.user.username
    person = get_object_or_404(Person, username=pusername)
    prospective_team = get_object_or_404(Team, username=tusername)
    greeting = "Hi Team %s," % prospective_team.team_name
    par1 = "%s" % person.child_description()
    par2 = "The child's interests are as follows. %s" % person.child_interest
    par3 = ""
    return render(request, 'match/show_invite.html', {'invitor' : pusername,
        'invitee' : tusername, 'type' : Invite.P2T, 'greeting' : greeting,
        'par1' : par1, 'par2' : par2, 'par3' : par3})


def render_person_searching_teams(request, zipcode, dist, latitude, longitude,
                                  new_members, jfll, fll, ftc, frc, error_message):
    team_list_by_dist = []
    list_results = False
    if not error_message and (jfll or fll or ftc or frc):
        list_results = True
        # has data, filter by kind
        qs = []
        if new_members:
            qs = Team.objects.filter(looking_for_teammate="True")
        else:
            qs = Team.objects
        if not jfll:
            qs = qs.exclude(first_program=Team.JFLL)
        if not fll:
            qs = qs.exclude(first_program=Team.FLL)
        if not ftc:
            qs = qs.exclude(first_program=Team.FTC)
        if not frc:
            qs = qs.exclude(first_program=Team.FRC)
        # filter by distance
        team_list = []
        dist_list = []
        for t in qs:
            d = t.distance_from(latitude, longitude)
            if d <= dist:
                team_list.append(t)
                dist_list.append(d)
        # sort list by distance
        team_list_by_dist = [x for (y,x) in sorted(zip(dist_list, team_list), key=lambda pair: pair[0])]
    # has team list / or empty
    return render(request, 'match/person_searching_teams_result.html', {
        'zipcode' : zipcode, 'dist' : dist,
        'new_members' : new_members,
        'jfll' : jfll, 'fll' : fll, 'ftc' : ftc, 'frc' : frc,
        'list_results' : list_results,
        'team_list_size' : len(team_list_by_dist),
        'team_list': team_list_by_dist,
        'error_message' : error_message})

def person_searching_teams(request):
    if request.user.is_authenticated:
        person = has_person(request.user.username)
        if person != None:
            return render_person_searching_teams(request, person.zip_code, 15,
                person.latitude, person.longitude, True,
                person.interested_in_jFLL, person.interested_in_FLL, person.interested_in_FTC,
                person.interested_in_FRC, None)
    return render_person_searching_teams(request, 10000, 15, 0.0, 0.0,
        True, False, False, False, False, "")    

def person_searching_teams_result(request):
    person = None
    error_message = ""
    # get and normalize dist
    dist = int(request.POST['distance'])
    if dist == None or dist < 1 or dist > max_travel_distance:
        error_message += "Must specify a distance between 1 and %s miles.  " % max_travel_distance
        dist = 15
    zipcode = request.POST['zipcode']
    zipcode_search_engine = ZipcodeSearchEngine()
    info = zipcode_search_engine.by_zipcode(zipcode)
    latitude = info.Latitude
    longitude = info.Longitude
    if latitude == None or longitude == None:
        error_message += "Must specify a valid US zipcode.  "
    jfll = False
    if "jfll" in request.POST:
        jfll = True
    fll = False
    if "fll" in request.POST:
        fll = True
    ftc = False
    if "ftc" in request.POST:
        ftc = True
    frc = False
    if "frc" in request.POST:
        frc = True
    if not (jfll or fll or ftc or frc):
        error_message += "Must select at least one of jFLL, FLL, FTC, or FRC type of teams.  "
    new_members = False
    if "new_members" in request.POST:
       new_members  = True
    return render_person_searching_teams(request, zipcode, dist, latitude, longitude, new_members,
                                       jfll, fll, ftc, frc, error_message)    





################################################################################
# teams

@login_required
def team_profile(request):
    username = request.user.username
    if has_person(username):
        return person_profile(request)
    # try to get team profile from database
    try:
        #has a team
        team = Team.objects.get(username=username)
        if request.method == "POST":
            # posted a new form, inspect
            form = TeamForm(request.POST, instance=team)
            if form.is_valid():
                team = form.save(commit=False)
                team.info_cleanup(username, False)
                team.save()
                return settings(request)
        else:
            # comming here before recieving a post
            form = TeamForm(instance=team)
        return render(request, 'match/team_profile.html', {'form': form})
        
    except:
        # does not have a team
        if request.method == "POST":
            # posted a new form, inspect
            form = TeamForm(request.POST)
            if form.is_valid():
                team = form.save(commit=False)
                team.info_cleanup(username, True)
                team.save()
                return settings(request)
        else:
            # comming here first, get the post
            form = TeamForm()
        return render(request, 'match/team_profile.html', {'form': form})
    

@login_required
def team_viewing_person(request, pusername):
    tusername = request.user.username
    team = get_object_or_404(Team, username=tusername)
    prospective_person = get_object_or_404(Person, username=pusername)
    can_invite = True
    if Invite.find_identical_pending_invite(tusername, pusername, Invite.T2P):
        can_invite = False
    too_many_invite = ""
    if Invite.pending_invite_num(tusername) > max_initiated_invite:
        too_many_invite = "Team cannot invite prospective teammates at this time as you have exceeeded the maximum of %d pending invites; invites expire within %d days." % (max_initiated_invite, invite_expiration_in_days)
    return render(request, 'match/team_viewing_person.html', {
        'prospective_person' : prospective_person, 'can_invite' : can_invite,
        'too_many_invite' : too_many_invite})

@login_required
def team_inviting_person(request, pusername):
    tusername = request.user.username
    team = get_object_or_404(Team, username=tusername)
    prospective_person = get_object_or_404(Person, username=pusername)

    greeting = "Dear prospective teammate's gurdian,"
    par1  = "%s" % team.team_description()
    par1 += "Our team is looking for teammates and we are hoping that your child will consider us."
    par2  = "We have described our team as follow.  %s.  " % team.description
    if team.achievement:
        par2 += "And here are our recent achievements.  %s." % team.achievement
    par3  = ""
    if team.web_site:
        par3 = "You will find further information on our web site: %s" % team.web_site
    return render(request, 'match/show_invite.html', {'invitor' : tusername,
        'invitee' : pusername, 'type' : Invite.T2P, 'greeting' : greeting,
        'par1' : par1, 'par2' : par2, 'par3' : par3})


def render_team_searching_persons(request, team, dist, error_message):
    # refine to relevant team
    qs = []
    if team.first_program == team.JFLL:
        qs = Person.objects.filter(interested_in_jFLL = True)
    elif team.first_program == team.FLL:
        qs = Person.objects.filter(interested_in_FLL = True)
    elif team.first_program == team.FTC:
        qs = Person.objects.filter(interested_in_FTC = True)
    elif team.first_program == team.FRC:
        qs = Person.objects.filter(interested_in_FRC = True)
    person_list = []
    dist_list = []
    for p in qs:
        d = p.distance_from(team.latitude, team.longitude)
        if d <= dist:
            person_list.append(p)
            dist_list.append(d)
    # sort list by distance
    person_list_by_dist = [x for (y,x) in sorted(zip(dist_list, person_list), key=lambda pair: pair[0])]
    list_results = True
    if error_message:
        list_results = False
    return render(request, 'match/team_searching_persons_result.html', {
        'dist' : dist,
        'person_list_size' : len(person_list_by_dist),
        'person_list': person_list_by_dist,
        'list_results' : list_results,
        'error_message' : error_message})

@login_required
def team_searching_persons(request):
    tusername = request.user.username
    team = get_object_or_404(Team, username=tusername)
    dist = 15
    return render_team_searching_persons(request, team, dist, "")    

@login_required
def team_searching_persons_result(request):
    tusername = request.user.username
    team = get_object_or_404(Team, username=tusername)
    # get and normalize dist
    error_message = ""
    dist = int(request.POST['distance'])
    if dist == None or dist < 1 or dist > max_travel_distance:
        error_message += "Must specify a distance between 1 and %s miles.  " % max_travel_distance
        dist = 15
    return render_team_searching_persons(request, team, dist, error_message)    



################################################################################
# invite

@login_required
def send_invite(request, invitor, invitee, type):
    site = "http://127.0.0.1:8000/match"
    # get message
    greeting = request.POST['greeting']
    par1 = request.POST['par1']
    par2 = request.POST['par2']
    par3 = request.POST['par3']
    message = request.POST['message']
    text = "\n\nBegin of message from findmyteam.org user\n\n"
    text = "%s\n\n%s\n\n%s\n\n" % (greeting, par1, par2)
    if par3:
        text += "%s\n\n" % par3
    if message:
        text += "%s\n\n" % message
    text += "Looking forward to hearing from you.\n"
    # create record
    invite = Invite.create(invitor, invitee, type)
    invite.save()
    id = invite.id
    text += "\n\nEnd of message from findmyteam.org user"
    text += "You are requested to take one of the following two actions.\n\n"
    text += "  1) If you are interested to learn more and communicate, accept the invite.\n"
    text += "  2) If you are not interested, decline the invite.\n"
    text += "You will learn of each other's email address only if you accept the request.  "
    text += "You have %d days to respond.\n\n" % invite_expiration_in_days
    text += "Accept: visit %s/%d/accept_invite\n" % (site, id)
    text += "Decline: visit %s/%d/decline_invite\n\n" % (site, id)
    text += "Thanks for using findmyteam.org!\nfindmyteam.org powered by Team Robocracy\n"
    print(text)
    email = EmailMessage(subject='Contact request from findmyteam.org',
                         body=text, to=[request.user.email])
    email.send()
    return render(request, 'match/index.html', {'header' : 'Congratulations!',
        'message' : 'Invite sent'}) 


@login_required
def accept_invite(request, invite_id):
    # locate invite
    invite = get_object_or_404(Invite, id=invite_id)
    # make sure the invite was addressed to us, and is still current
    if invite.prospective_username != request.user.username:
        return render(request, 'match/index.html', { 'header' : 'Error!', 
            'message' : 'Responding to someone else\'s invite; ignore.'})
    if invite.completed():
        return render(request, 'match/index.html', { 'header' : 'Error!',
            'message' : 'Responding to an expired invite; ignore.'})
    # find involved
    tupple = invite.email_and_name_pairs()
    if not tupple:
        return render(request, 'match/index.html', {'header' : 'Error!', 
            'message' : 'Failed to load info; failure.'})
    [email1, name1, email2, name2] = tupple
    # send email to both
    text =  "\n\nDear %s and %s,\n\n" % (name1, name2)
    text += "Congratulation, both of you have expressed interest in getting in touch with each other.  On behalf of findmyteam.org, we whish you luck in your future endavor. \n\n"
    text += "When you have a chance, please spread the word about http://findmyteam.org so that others might benefits from finding teams and teammates. And remember, be safe out-there and use common sense when interacting with new acquaintances. \n\n"
    text += "Thanks for using findmyteam.org!\nfindmyteam.org powered by Team Robocracy\n\n"
    email = EmailMessage(subject="Shared Contact from findmyteam.org", body=text, to=[email1, email2])
    email.send()
    # mark as accepted
    invite.status = invite.ACCEPTED
    invite.save()
    return render(request, 'match/index.html', {'header' : 'Congratulations!',
        'message' : 'Congratulation, an email was send to both parties.'})
    

@login_required
def decline_invite(request, invite_id):
    return render(request, 'match/index.html',
                      {'message' : 'Your invitation has been recoreded as declined.'})


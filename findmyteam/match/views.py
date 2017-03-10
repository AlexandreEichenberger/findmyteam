from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# Create your views here.
from .models import Team, Person, Invite

################################################################################
# general

def index(request):
    return render(request, 'match/index.html', {})

def settings(request):
    return render(request, 'match/settings.html', {})

max_travel_distance = 200

################################################################################
# person

def person_viewing_team(request, pusername, tusername):
    person = get_object_or_404(Person, username=pusername)
    prospective_team = get_object_or_404(Team, username=tusername)
    return render(request, 'match/person_viewing_team.html', {'person' : person, 'prospective_team' : prospective_team})

def person_inviting_team(request, pusername, tusername):
    person = get_object_or_404(Person, username=pusername)
    prospective_team = get_object_or_404(Team, username=tusername)

    greeting = "Hi Team %s," % prospective_team.team_name
    par1 = "%s" % person.child_description()
    par2 = "The child's interests are as follows. %s" % person.child_interest
    par3 = ""
    return render(request, 'match/show_invite.html', {'invitor' : pusername,
        'invitee' : tusername, 'type' : Invite.P2T, 'greeting' : greeting,
        'par1' : par1, 'par2' : par2, 'par3' : par3})

def render_team_list_for_person(request, person, dist):
    # refine to relevant team
    qs = Team.objects.filter(looking_for_teammate="True")
    if person.interested_in_jFLL == False:
        qs = qs.exclude(first_program=Team.JFLL)
    if person.interested_in_FLL == False:
        qs = qs.exclude(first_program=Team.FLL)
    if person.interested_in_FTC == False:
        qs = qs.exclude(first_program=Team.FTC)
    if person.interested_in_FRC == False:
        qs = qs.exclude(first_program=Team.FRC)
    person.update_zip_info()
    team_list = []
    dist_list = []
    for t in qs:
        d = t.distance_from(person.latitude, person.longitude)
        if d <= dist:
            team_list.append(t)
            dist_list.append(d)
    # sort list by distance
    team_list_by_dist = [x for (y,x) in sorted(zip(dist_list, team_list))]
    return render(request, 'match/person_searching_team_result.html', {'person' : person,
        'team_interest' : person.child_team_interest_description("interested in a", "not currently interested in a"),
        'dist' : dist,
        'team_list_size' : len(team_list_by_dist),
        'team_list': team_list_by_dist})


def person_searching(request, pusername):
    person = get_object_or_404(Person, username=pusername)
    dist = 15
    return render_team_list_for_person(request, person, dist)    

def person_searching_result(request, pusername):
    person = get_object_or_404(Person, username=pusername)
    # get and normalize dist
    dist = int(request.POST['distance'])
    if dist == None:
        dist = 15
    elif dist < 1:
        dist = 1
    elif dist > max_travel_distance:
        dist = max_travel_distance
    return render_team_list_for_person(request, person, dist)    



################################################################################
# teams

def team_viewing_person(request, tusername, pusername):
    team = get_object_or_404(Team, username=tusername)
    prospective_person = get_object_or_404(Person, username=pusername)
    can_invite = True
    if Invite.find_pending_invite(tusername, pusername, Invite.T2P):
        print("found an invite already")
        can_invite = False
    return render(request, 'match/team_viewing_person.html', {'team' : team,
        'prospective_person' : prospective_person, 'can_invite' : can_invite})

def team_inviting_person(request, tusername, pusername):
    team = get_object_or_404(Team, username=tusername)
    prospective_person = get_object_or_404(Person, username=pusername)

    greeting = "Dear prospective teammate's gurdian,"
    par1  = "%s" % team.team_description()
    par1 += "Our team is looking for teammates and we are hoping that you will consider us."
    par2  = "We have described our team as follow.  %s.  " % team.description
    if team.achievement:
        par2 += "And here are our recent achievements.  %s." % team.achievement
    par3  = ""
    if team.web_site:
        par3 = "You will find further information on our web site: %s" % team.web_site
    return render(request, 'match/show_invite.html', {'invitor' : tusername,
        'invitee' : pusername, 'type' : Invite.T2P, 'greeting' : greeting,
        'par1' : par1, 'par2' : par2, 'par3' : par3})


def render_person_list_for_team(request, team, dist):
    # refine to relevant team
    qs = []
    if team.first_program == team.JFLL:
        qs = Person.objects.filter(interested_in_jFLL = True)
    elif team.first_program == team.FLL:
        qs = Person.objects.filter(interested_in_FLL = True)
    elif team.first_program == team.FTC:
        qs = Person.objects.filter(interested_in_FTC = True)
    elif team.first_program == team.FLL:
        qs = Person.objects.filter(interested_in_FRC = True)
    team.update_zip_info()
    person_list = []
    dist_list = []
    for p in qs:
        d = p.distance_from(team.latitude, team.longitude)
        if d <= dist:
            person_list.append(p)
            dist_list.append(d)
    # sort list by distance
    person_list_by_dist = [x for (y,x) in sorted(zip(dist_list, person_list))]
    return render(request, 'match/team_searching_person_result.html', {'team' : team,
        'dist' : dist,
        'person_list_size' : len(person_list_by_dist),
        'person_list': person_list_by_dist})


def team_searching_person(request, tusername):
    team = get_object_or_404(Team, username=tusername)
    dist = 15
    return render_person_list_for_team(request, team, dist)    

def team_searching_person_result(request, tusername):
    team = get_object_or_404(Team, username=tusername)
    # get and normalize dist
    dist = int(request.POST['distance'])
    if dist == None:
        dist = 15
    elif dist < 1:
        dist = 1
    elif dist > max_travel_distance:
        dist = max_travel_distance
    return render_person_list_for_team(request, team, dist)    


################################################################################
# invite

def send_invite(request, invitor, invitee, type):
    greeting = request.POST['greeting']
    par1 = request.POST['par1']
    par2 = request.POST['par2']
    par3 = request.POST['par3']
    message = request.POST['message']
    text = "%s\n\n%s\n\n%s\n\n" % (greeting, par1, par2)
    if par3:
        text += "%s\n\n" % par3
    if message:
        text += "%s\n\n" % message
    text += "Looking forward to hearing from you.\n"

    invite = Invite.create(invitor, invitee, type)
    invite.save()
    invite_txt = "Invite: from %s, to %s, type %s, status %s" % (invite.invitor_username,
        invite.prospective_username, invite.get_type_display(), invite.get_status_display())
    print(invite_txt)
    print(text)
    return HttpResponse("Hello, send invite.")


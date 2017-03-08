from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# Create your views here.
from .models import Team, Person

def index(request):
    return HttpResponse("Hello, world. You're at find my team page.")

max_travel_distance = 200

################################################################################
# person

def person_detail(request, username):
    person = get_object_or_404(Person, username=username)
    return render(request, 'match/person_detail.html', {'person' : person})

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
    return render(request, 'match/person_searching_result.html', {'person' : person,
        'team_interest' : person.child_team_interest_description("interested in a", "not currently interested in a"),
        'dist' : dist,
        'team_list_size' : len(team_list_by_dist),
        'team_list': team_list_by_dist})


def person_searching(request, username):
    person = get_object_or_404(Person, username=username)
    dist = 15
    return render_team_list_for_person(request, person, dist)    

def person_searching_result(request, username):
    person = get_object_or_404(Person, username=username)
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

def team_detail(request, username):
    team = get_object_or_404(Team, username=username)
    return render(request, 'match/team_detail.html', {'team' : team})

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


def team_searching_person(request, username):
    team = get_object_or_404(Team, username=username)
    dist = 15
    return render_person_list_for_team(request, team, dist)    

def team_searching_person_result(request, username):
    team = get_object_or_404(Team, username=username)
    # get and normalize dist
    dist = int(request.POST['distance'])
    if dist == None:
        dist = 15
    elif dist < 1:
        dist = 1
    elif dist > max_travel_distance:
        dist = max_travel_distance
    return render_person_list_for_team(request, team, dist)    



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# Create your views here.
from .models import Team, Person

def index(request):
    return HttpResponse("Hello, world. You're at find my team page.")

def person_detail(request, username):
    person = get_object_or_404(Person, username=username)
    return render(request, 'match/person_detail.html', {'description' : person.child_description()})

# person

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
        'team_interest' : person.child_team_interest("interested in a", "not currently interested in a"),
        'dist' : dist,
        'team_size' : len(team_list_by_dist),
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
    elif dist > 1000:
        dist = 1000
    return render_team_list_for_person(request, person, dist)    

# teams

def team_detail(request, username):
    team = get_object_or_404(Team, username=username)
    return render(request, 'match/team_detail.html', {'team' : team})


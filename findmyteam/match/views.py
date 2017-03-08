from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# Create your views here.
from .models import Team, Person

def index(request):
    return HttpResponse("Hello, world. You're at find my team page.")

def team_detail(request, username):
    #return HttpResponse("You are looking at team %s. " % username)
    team = get_object_or_404(Team, username=username)
    return render(request, 'match/team_detail.html', {'description' : team.team_description() + team.team_needs()})

def person_detail(request, username):
    #return HttpResponse("You are looking at team %s. " % username)
    person = get_object_or_404(Person, username=username)
    return render(request, 'match/person_detail.html', {'description' : person.child_description()})



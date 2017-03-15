from django.conf.urls import url

from . import views

app_name = "match"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^programs/$', views.programs, name='programs'),
    url(r'^about/$', views.about, name='about'),

    # person
    url(r'^person_actions/$', views.person_actions, name='person_actions'),
    url(r'^person_profile/$', views.person_profile, name='person_profile'),
    
    url(r'^person_viewing_team/(?P<tusername>[a-zA-Z_]+)/$', views.person_viewing_team, name='person_viewing_team'),
    url(r'^person_inviting_team/(?P<tusername>[a-zA-Z_]+)/$', views.person_inviting_team, name='person_inviting_team'),
    url(r'^person_searching_teams/$', views.person_searching_teams, name='person_searching_teams'),
    url(r'^person_searching_teams_result/$', views.person_searching_teams_result, name='person_searching_teams_result'),
    
    # team
    url(r'^team_actions/$', views.team_actions, name='team_actions'),
    url(r'^team_profile/$', views.team_profile, name='team_profile'),
    url(r'^team_viewing_person/(?P<pusername>[a-zA-Z_]+)/$', views.team_viewing_person, name='team_viewing_person'),
    url(r'^team_inviting_person/(?P<pusername>[a-zA-Z_]+)/$', views.team_inviting_person, name='team_inviting_person'),
    url(r'^team_searching_persons/$', views.team_searching_persons, name='team_searching_persons'),
    url(r'^team_searching_persons_result/$', views.team_searching_persons_result, name='team_searching_persons_result'),

    # organization
    url(r'^org_actions/$', views.org_actions, name='org_actions'),
    
    # invite
    url(r'^(?P<invitor>[a-zA-Z_]+)/(?P<invitee>[a-zA-Z_]+)/(?P<type>[a-zA-Z_]+)/send_invite/$', views.send_invite, name='send_invite'),
    url(r'^(?P<invite_id>[0-9]+)/accept_invite/$', views.accept_invite, name='accept_invite'),
    url(r'^(?P<invite_id>[0-9]+)/decline_invite/$', views.accept_invite, name='accept_invite'),

]

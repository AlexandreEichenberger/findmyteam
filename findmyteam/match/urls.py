from django.conf.urls import url

from . import views

app_name = "match"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^settings$', views.settings, name='settings'),
    # person
    url(r'^(?P<pusername>[a-zA-Z_]+)/person_viewing_team/(?P<tusername>[a-zA-Z_]+)/$', views.person_viewing_team, name='person_viewing_team'),
    url(r'^(?P<pusername>[a-zA-Z_]+)/person_inviting_team/(?P<tusername>[a-zA-Z_]+)/$', views.person_inviting_team, name='person_inviting_team'),
    url(r'^(?P<pusername>[a-zA-Z_]+)/person_searching_team/$', views.person_searching, name='person_searching_team'),
    url(r'^(?P<pusername>[a-zA-Z_]+)/person_searching_team_result/$', views.person_searching_result, name='person_searching_team_result'),

    # team
    url(r'^(?P<tusername>[a-zA-Z_]+)/team_viewing_person/(?P<pusername>[a-zA-Z_]+)/$', views.team_viewing_person, name='team_viewing_person'),
    url(r'^(?P<tusername>[a-zA-Z_]+)/team_inviting_person/(?P<pusername>[a-zA-Z_]+)/$', views.team_inviting_person, name='team_inviting_person'),
        url(r'^(?P<tusername>[a-zA-Z_]+)/team_searching_person/$', views.team_searching_person, name='team_searching_person'),
    url(r'^(?P<tusername>[a-zA-Z_]+)/team_searching_person_result/$', views.team_searching_person_result, name='team_searching_person_result'),

    # invite
    url(r'^(?P<invitor>[a-zA-Z_]+)/(?P<invitee>[a-zA-Z_]+)/(?P<type>[a-zA-Z_]+)/send_invite/$', views.send_invite, name='send_invite'),

]

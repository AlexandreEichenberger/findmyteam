from django.conf.urls import url

from . import views

app_name = "match"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /match/team/name/
    url(r'^team_detail/(?P<username>[a-zA-Z_]+)/$', views.team_detail, name='team_detail'),
    url(r'^person_detail/(?P<username>[a-zA-Z_]+)/$', views.person_detail, name='person_detail'),
    url(r'^person_searching/(?P<username>[a-zA-Z_]+)/$', views.person_searching, name='person_searching'),
    url(r'^person_searching_result/(?P<username>[a-zA-Z_]+)/$', views.person_searching_result, name='person_searching_result'),

]

from django.conf.urls import url

from . import views

app_name = "match"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /match/team/name/
    url(r'^(?P<username>[a-zA-Z_]+)/team_detail/$', views.team_detail, name='team_detail'),
    url(r'^(?P<username>[a-zA-Z_]+)/person_detail/$', views.person_detail, name='person_detail'),
    url(r'^(?P<username>[a-zA-Z_]+)/person_searching/$', views.person_searching, name='person_searching'),
    url(r'^(?P<username>[a-zA-Z_]+)/person_searching_result/$', views.person_searching_result, name='person_searching_result'),

]

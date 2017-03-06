from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /match/team/name/
    url(r'^team_detail/(?P<username>[a-zA-Z_]+)/$', views.team_detail, name='team_detail'),

]

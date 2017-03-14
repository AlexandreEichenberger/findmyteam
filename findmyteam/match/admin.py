from django.contrib import admin
from .models import Profile, Person, Team, Invite

# Register your models here. 
admin.site.register(Profile)
admin.site.register(Person)
admin.site.register(Team)
admin.site.register(Invite)


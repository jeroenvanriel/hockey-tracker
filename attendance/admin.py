from django.contrib import admin

from .models import Player, Event, Attendance, Fine

admin.site.register(Player)
admin.site.register(Event)
admin.site.register(Attendance)
admin.site.register(Fine)

from django.contrib import admin

from .models import Player, Training, Attendance, Fine

admin.site.register(Player)
admin.site.register(Training)
admin.site.register(Attendance)
admin.site.register(Fine)

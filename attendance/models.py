from django.db import models
from django.conf import settings

class Training(models.Model):
    date = models.DateTimeField('date')

class Player(models.Model):
    name = models.CharField(max_length=50)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    presence = models.BooleanField(default=False)

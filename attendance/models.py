from django.db import models
from django.conf import settings

class Training(models.Model):
    date = models.DateTimeField('date')
    canceled = models.BooleanField(default=False)
    deadline = models.DateTimeField('deadline', default=None, null=True, blank=True)

    def __str__(self):
        return str(self.date.date()) + (" (canceled)" if self.canceled else "")

class Player(models.Model):
    """This decoupling from the user (authentication) enables us to start using the app before
    users login and do certain things themselves."""
    name = models.CharField(max_length=50)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    presence = models.BooleanField(default=True)
    actual_presence = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.training.date.date()} - {self.player}, {self.presence}, {self.actual_presence}"

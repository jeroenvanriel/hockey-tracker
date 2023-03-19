from django.db import models
from django.conf import settings
import datetime
from .apps import DEADLINE_DELTA, DEADLINE_TIME

class Event(models.Model):
    class Meta:
        permissions = [
            ('verify_event', 'Verify attendance of players that said they would come.')
        ]

    date = models.DateTimeField('date')
    canceled = models.BooleanField(default=False)
    deadline = models.DateTimeField('deadline', default=None, null=True, blank=True)
    verified = models.BooleanField(default=False)

    type = models.TextField(default='training')

    def __str__(self):
        return str(self.date.date()) + (" (canceled)" if self.canceled else "")

    def save(self, *args, **kwargs):
        if not self.deadline:
            # move the deadline the specified number of days backward
            # and set the default deadline time (e.g. 23:59)
            self.deadline = (self.date - datetime.timedelta(days=DEADLINE_DELTA)).replace(
                hour=DEADLINE_TIME.hour, minute=DEADLINE_TIME.minute, second=DEADLINE_TIME.second)
        super().save(*args, **kwargs)

class Player(models.Model):
    """This decoupling from the user (authentication) enables us to start using the app before
    users login and do certain things themselves."""
    name = models.CharField(max_length=50)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    player = models.ForeignKey(Player, related_name='attendances', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    presence = models.BooleanField(default=True)
    actual_presence = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.event.date.date()} - {self.player}, {self.presence}, {self.actual_presence}"

class Fine(models.Model):
    attendance = models.OneToOneField(Attendance, null=True, on_delete=models.SET_NULL)
    amount = models.FloatField()
    paid = models.BooleanField(default=False)

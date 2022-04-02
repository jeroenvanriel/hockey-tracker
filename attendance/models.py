from django.db import models

class Training(models.Model):
    date = models.DateTimeField('date')

class Player(models.Model):
    name = models.CharField(max_length=50)

class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)


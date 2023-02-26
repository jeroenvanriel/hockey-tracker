from django.apps import AppConfig
import datetime


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'


DEADLINE_DELTA = 2
DEADLINE_TIME = datetime.time(23, 59, 59)

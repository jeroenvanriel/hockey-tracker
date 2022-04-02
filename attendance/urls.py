from django.urls import path

from . import views

urlpatterns = [
    path('players/', views.players, name='players'),
    path('players/<int:player_id>/', views.player, name='player'),
    path('trainings/', views.trainings, name='trainings'),
    path('training/<int:training_id>/', views.training, name='training'),
    path('training/<int:training_id>/submit/', views.submit, name='submit'),
]


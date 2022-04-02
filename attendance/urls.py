from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('players/', views.PlayerView.as_view(), name='players'),
    path('players/<int:player_id>/', views.player, name='player'),
    path('trainings/', views.TrainingView.as_view(), name='trainings'),
    path('training/<int:training_id>/', views.training, name='training'),
    path('training/<int:training_id>/submit/', views.submit, name='submit'),
]


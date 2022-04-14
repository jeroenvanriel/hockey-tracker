from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('player', views.PlayerListView.as_view(), name='players'),
    path('player/<int:pk>/', views.PlayerDetailView.as_view(), name='player'),

    path('training/', views.TrainingListView.as_view(), name='trainings'),
    path('training/<int:pk>/', views.TrainingDetailView.as_view(), name='training'),

    path('training/<int:training_id>/submit/', views.submit, name='submit'),
]


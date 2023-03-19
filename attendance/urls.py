from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('player', views.PlayerListView.as_view(), name='players'),
    path('player/<int:pk>/', views.PlayerDetailView.as_view(), name='player'),
    path('player/<int:pk>/paid', views.fine_paid, name='fine_paid'),

    path('event/', views.event_overview, name='events'),
    path('event/<int:pk>/', views.update_presence, name='event'),
    path('event/<int:pk>/verify/', views.verify, name='verify'),
]

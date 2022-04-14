from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Player, Training

def index(request):
    return render(request, 'index.html')

class PlayerListView(generic.ListView):
    model = Player
class PlayerDetailView(generic.DetailView):
    model = Player

class TrainingListView(generic.ListView):
    model = Training
class TrainingDetailView(generic.DetailView):
    model = Training

def submit(request, training_id):
    training = get_object_or_404(Training, pk=training_id)

    choice = request.POST['choice']
    return HttpResponse(f"submitted choice: {choice}")


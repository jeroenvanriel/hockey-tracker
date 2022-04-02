from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

from django.views import generic

from .models import Player, Training

def index(request):
    return render(request, 'index.html')

class PlayerView(generic.ListView):
    model = Player

def player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    return render(request, 'player.html', {'player': player})

class TrainingView(generic.ListView):
    model = Training

def training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    return render(request, 'training.html', {'training': training})

def submit(request, training_id):
    training = get_object_or_404(Training, pk=training_id)

    choice = request.POST['choice']
    return HttpResponse(f"submitted choice: {choice}")

    #return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


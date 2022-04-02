from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

from .models import Player, Training

def players(request):
    players = Player.objects.all()
    return render(request, 'players.html', {'players': players})

def player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    return render(request, 'player.html', {'player': player})

def trainings(request):
    trainings = Training.objects.all()
    return render(request, 'trainings.html', {'trainings': trainings})

def training(request, training_id):
    training = get_object_or_404(Training, pk=training_id)
    return render(request, 'training.html', {'training': training})

def submit(request, training_id):
    training = get_object_or_404(Training, pk=training_id)

    choice = request.POST['choice']
    return HttpResponse(f"submitted choice: {choice}")

    #return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


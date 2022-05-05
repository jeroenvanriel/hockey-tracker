from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery, Exists


from .models import Player, Training, Attendance

def index(request):
    return render(request, 'index.html')

class PlayerListView(LoginRequiredMixin, generic.ListView):
    model = Player

class PlayerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Player

class TrainingListView(LoginRequiredMixin, generic.ListView):
    model = Training

@login_required
def update_presence(request, pk):
    training = get_object_or_404(Training, pk=pk)
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        messages.error(request, "Your account is not linked to a registered player.")
        return HttpResponseRedirect(reverse('trainings'))

    if request.method == 'POST':
        choice = 'yes' in request.POST

        attendance, created = Attendance.objects.update_or_create(
            player=player,
            training=training,
            defaults={'presence': choice}
        )

        return HttpResponseRedirect(reverse('training', args=(training.id,)))

    else:
        cancellations = Attendance.objects.filter(training=training, player=OuterRef('pk'), presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations))

        return render(request, 'attendance/training_detail.html', {
            'training': training,
            'players': players,
        })

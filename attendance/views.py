from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Exists
from django.utils import timezone

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
    deadline_passed = timezone.now() > training.deadline if training.deadline else False
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        messages.error(request, "Your account is not linked to a registered player.")
        return HttpResponseRedirect(reverse('trainings'))

    if request.method == 'POST':
        choice = 'yes' in request.POST

        if deadline_passed:
            messages.error(request, "The deadline to update presence has passed.")
            return HttpResponseRedirect(reverse('trainings'))

        attendance, created = Attendance.objects.update_or_create(
            player=player,
            training=training,
            defaults={'presence': choice}
        )

        return HttpResponseRedirect(reverse('training', args=(training.id,)))

    else:
        cancellations = Attendance.objects.filter(training=training, player=OuterRef('pk'), presence=False)
        actual = Attendance.objects.filter(training=training, player=OuterRef('pk'), actual_presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations), actual_presence=~Exists(actual))

        return render(request, 'attendance/training_detail.html', {
            'training': training,
            'players': players,
            'deadline_passed': deadline_passed,
        })

@permission_required('attendance.change_attendance')
def verify(request, pk):
    training = get_object_or_404(Training, pk=pk)

    if request.method == 'POST':
        print(request.POST)
        for player in Player.objects.all():
            Attendance.objects.update_or_create(player=player, training=training, defaults={
                'actual_presence': str(player.pk) in request.POST.keys()
            })

        return HttpResponseRedirect(reverse('training', args=(training.id,)))

    else:
        cancellations = Attendance.objects.filter(training=training, player=OuterRef('pk'), presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations))

        return render(request, 'attendance/training_verify.html', {
            'training': training,
            'players': players,
        })

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Exists, Sum
from django.utils import timezone

from .models import Player, Training, Attendance, Fine

def index(request):
    return render(request, 'index.html')

class PlayerListView(LoginRequiredMixin, generic.ListView):
    model = Player

class PlayerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Player

    def get_queryset(self):
        # calculate remaining unpaid total fine
        subquery = Fine.objects.filter(
            paid=False,
            attendance__player__pk=OuterRef('pk')
        ).values('attendance__player__pk')
        
        total_fine = subquery.annotate(total_fine=Sum('amount')).values('total_fine')
        return Player.objects.annotate(total_fine=total_fine, any_fines=Exists(subquery))

class TrainingListView(LoginRequiredMixin, generic.ListView):
    model = Training
    queryset = Training.objects.filter(verified=False, date__gte = timezone.now()).order_by('date')

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
        players_present = players.filter(presence=True).count()

        return render(request, 'attendance/training_detail.html', {
            'training': training,
            'players': players,
            'deadline_passed': deadline_passed,
            'players_present': players_present,
        })

@permission_required('attendance.change_attendance')
def verify(request, pk):
    training = get_object_or_404(Training, pk=pk)

    if request.method == 'POST':
        print(request.POST)
        for player in Player.objects.all():
            try:
                said_presence = Attendance.objects.get(player=player, training=training).presence
            except Attendance.DoesNotExist:
                said_presence = True # assume presence by default

            # record the actual presence
            actual_presence = str(player.pk) in request.POST.keys()
            attendance, _ = Attendance.objects.update_or_create(player=player, training=training, defaults={
                'actual_presence': actual_presence
            })

            if said_presence and not actual_presence:
                # TODO: determine fine amount based on training or game, or maybe
                # even on the amount of minutes late. The latter could even be
                # implemented automatically, but then we need a route for partial
                # "he was late" requests.
                Fine.objects.update_or_create(attendance=attendance, amount=5)
        
        training.verified = True
        training.save()

        return HttpResponseRedirect(reverse('training', args=(training.id,)))

    elif not training.verified:
        cancellations = Attendance.objects.filter(training=training, player=OuterRef('pk'), presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations))

        return render(request, 'attendance/training_verify.html', {
            'training': training,
            'players': players,
        })

    else:
        # TODO: In case we want to support (partial) updates, make sure to return the actual
        # presence to show on the update page 
        messages.error(request, "This training has already been verified.")
        return HttpResponseRedirect(reverse('training', args=(training.id)))

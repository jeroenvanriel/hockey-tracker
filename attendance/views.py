from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Exists, Sum, Count
from django.utils import timezone

from .models import Player, Training, Attendance, Fine

def index(request):
    return render(request, 'index.html', {
        'total_unpaid_fines': Fine.objects.filter(paid=False).aggregate(Sum('amount'))['amount__sum'],
        'upcoming_training': Training.objects.filter(verified=False, date__gte=timezone.now()).order_by('date').first(),
        # TODO: player with highest fine
        # TODO: player with highest unpaid fine
        # TODO: player with highest attendance
        # TODO: player with lowest attendance
        # TODO: make the above per season (so we first need to introduce this concept of season)
    })

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

def training_overview(request):
    trainings = Training.objects.filter(verified=False, date__gte = timezone.now()).order_by('date')

    # this way, because I don't know how to do this with an annotation
    for training in trainings:
        cancellations = Attendance.objects.filter(training=training, player=OuterRef('pk'), presence=False)
        actual = Attendance.objects.filter(training=training, player=OuterRef('pk'), actual_presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations), actual_presence=~Exists(actual))
        training.nr_players_present = players.filter(presence=True).count()

    return render(request, 'attendance/training_list.html', { 'training_list': trainings })

@login_required
def update_presence(request, pk):
    training = get_object_or_404(Training, pk=pk)
    deadline_passed = timezone.now() > training.deadline if training.deadline else False
    player = Player.objects.filter(user=request.user).first()

    if request.method == 'POST':
        if not player:
            messages.error(request, "Your account is not linked to a registered player.")
            return HttpResponseRedirect(reverse('training', args=(training.id,)))

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
        nr_players_present = players.filter(presence=True).count()

        return render(request, 'attendance/training_detail.html', {
            'training': training,
            'players': players,
            'deadline_passed': deadline_passed,
            'nr_players_present': nr_players_present,
            'user_can_verify': request.user.has_perm('attendance.training_verify'),
        })

@permission_required('attendance.training_verify')
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
        players_present = players.filter(presence=True)
        nr_players_present = players.filter(presence=True).count()

        return render(request, 'attendance/training_verify.html', {
            'training': training,
            'players_present': players_present,
            'nr_players_present': nr_players_present,
        })

    else:
        # TODO: In case we want to support (partial) updates, make sure to return the actual
        # presence to show on the update page 
        messages.error(request, "This training has already been verified.")
        return HttpResponseRedirect(reverse('training', args=(training.id,)))

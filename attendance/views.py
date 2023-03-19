from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Exists, Sum
from django.db.models.functions import Coalesce
from django.db import models
from django.utils import timezone

from .models import Player, Event, Attendance, Fine

def index(request):
    return render(request, 'index.html', {
        'total_unpaid_fines': Fine.objects.filter(paid=False).aggregate(Sum('amount'))['amount__sum'],
        'upcoming_event': Event.objects.filter(verified=False, date__gte=timezone.now()).order_by('date').first(),
        # TODO: personal total fine
        # TODO: player with highest fine
        # TODO: player with highest unpaid fine
        # TODO: player with highest attendance
        # TODO: player with lowest attendance
        # TODO: make the above per season (so we first need to introduce this concept of season)
    })

class PlayerListView(LoginRequiredMixin, generic.ListView):
    model = Player

    def get_queryset(self):
        # calculate remaining unpaid total fine
        subquery = Fine.objects.filter(
            paid=False,
            attendance__player__pk=OuterRef('pk')
        ).values('attendance__player__pk')
        
        total_fine = subquery.annotate(total_fine=Sum('amount')).values('total_fine')
        return Player.objects.annotate(total_fine=Coalesce(total_fine, 0, output_field=models.FloatField()), any_fines=Exists(subquery)).order_by('-total_fine')

class PlayerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Player

    def get_queryset(self):
        # calculate remaining unpaid total fine
        subquery = Fine.objects.filter(
            paid=False,
            attendance__player__pk=OuterRef('pk')
        ).values('attendance__player__pk')
        
        total_fine = subquery.annotate(total_fine=Sum('amount')).values('total_fine')
        return Player.objects.annotate(total_fine=Coalesce(total_fine, 0, output_field=models.FloatField()), any_fines=Exists(subquery))

@permission_required('attendance.fine_paid')
def fine_paid(request, pk):
    """Register a fine as paid."""

    player = get_object_or_404(Player, pk=pk)

    if request.method != 'POST':
        return HttpResponse(status_code=405) # method not allowed
    
    if 'paid' in request.POST:
        fine = get_object_or_404(Fine, pk=request.POST['paid'])
        fine.paid = True
        fine.save()
    if 'reset' in request.POST:
        fine = get_object_or_404(Fine, pk=request.POST['reset'])
        fine.paid = False
        fine.save()

    return HttpResponseRedirect(reverse('player', args=(player.id,)))


def event_overview(request):
    events = Event.objects.filter(verified=False, date__gte = timezone.now()).order_by('date')

    # this way, because I don't know how to do this with an annotation
    for event in events:
        cancellations = Attendance.objects.filter(event=event, player=OuterRef('pk'), presence=False)
        actual = Attendance.objects.filter(event=event, player=OuterRef('pk'), actual_presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations), actual_presence=~Exists(actual))
        event.nr_players_present = players.filter(presence=True).count()
        event.type_name = {'training': 'Training', 'game': 'Wedstrijd'}[event.type]

    return render(request, 'attendance/event_list.html', { 'event_list': events })

@login_required
def update_presence(request, pk):
    event = get_object_or_404(Event, pk=pk)
    deadline_passed = timezone.now() > event.deadline if event.deadline else False
    player = Player.objects.filter(user=request.user).first()

    if request.method == 'POST':
        if not player:
            messages.error(request, "Your account is not linked to a registered player.")
            return HttpResponseRedirect(reverse('event', args=(event.id,)))

        choice = 'yes' in request.POST

        if deadline_passed:
            messages.error(request, "The deadline to update presence has passed.")
            return HttpResponseRedirect(reverse('events'))

        attendance, created = Attendance.objects.update_or_create(
            player=player,
            tsraining=event,
            defaults={'presence': choice}
        )

        return HttpResponseRedirect(reverse('tsraining', args=(event.id,)))

    else:
        cancellations = Attendance.objects.filter(event=event, player=OuterRef('pk'), presence=False)
        actual = Attendance.objects.filter(event=event, player=OuterRef('pk'), actual_presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations), actual_presence=~Exists(actual))
        nr_players_present = players.filter(presence=True).count()

        return render(request, 'attendance/event_detail.html', {
            'event': event,
            'players': players,
            'deadline_passed': deadline_passed,
            'nr_players_present': nr_players_present,
            'user_can_verify': request.user.has_perm('attendance.event_verify'),
        })

@permission_required('attendance.event_verify')
def verify(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        print(request.POST)
        for player in Player.objects.all():
            try:
                said_presence = Attendance.objects.get(player=player, event=event).presence
            except Attendance.DoesNotExist:
                said_presence = True # assume presence by default

            # record the actual presence
            actual_presence = str(player.pk) in request.POST.keys()
            attendance, _ = Attendance.objects.update_or_create(player=player, event=event, defaults={
                'actual_presence': actual_presence
            })

            if said_presence and not actual_presence:
                # TODO: determine fine amount based on training or game, or maybe
                # even on the amount of minutes late. The latter could even be
                # implemented automatically, but then we need a route for partial
                # "he was late" requests.
                Fine.objects.update_or_create(attendance=attendance, amount=10)
        
        event.verified = True
        event.save()

        return HttpResponseRedirect(reverse('event', args=(event.id,)))

    elif not event.verified:
        cancellations = Attendance.objects.filter(event=event, player=OuterRef('pk'), presence=False)
        players = Player.objects.annotate(presence=~Exists(cancellations))
        players_present = players.filter(presence=True)
        nr_players_present = players.filter(presence=True).count()

        return render(request, 'attendance/event_verify.html', {
            'event': event,
            'players_present': players_present,
            'nr_players_present': nr_players_present,
        })

    else:
        # TODO: In case we want to support (partial) updates, make sure to return the actual
        # presence to show on the update page 
        messages.error(request, "This event has already been verified.")
        return HttpResponseRedirect(reverse('event', args=(event.id,)))

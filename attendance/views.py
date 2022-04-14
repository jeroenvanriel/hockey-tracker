from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Player, Training, Attendance

def index(request):
    return render(request, 'index.html')

class PlayerListView(generic.ListView):
    model = Player
class PlayerDetailView(generic.DetailView):
    model = Player

class TrainingListView(generic.ListView):
    model = Training
class TrainingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Training

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presence'] = True

        try:
            player = Player.objects.get(user=self.request.user)
            attendance = Attendance.objects.get(training=self.object, player=player)
            context['presence'] = attendance.presence
        except (Player.DoesNotExist, Attendance.DoesNotExist):
            pass

        return context

@login_required
def submit(request, training_id):
    training = get_object_or_404(Training, pk=training_id)

    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return render(request, 'attendance/training_detail.html', {
            'training': training,
            'error_message': "No player attached to this account."
        })

    choice = request.POST['choice'] == 'yes'

    attendance, created = Attendance.objects.update_or_create(
        player=player,
        training=training,
        defaults={'presence': choice}
    )

    return HttpResponseRedirect(reverse('training', args=(training.id,)))

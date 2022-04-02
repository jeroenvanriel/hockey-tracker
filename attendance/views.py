from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def player(request, player_name):
    return HttpResponse(f"You're looking at player {player_name}.")


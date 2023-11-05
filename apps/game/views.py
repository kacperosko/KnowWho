from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import JoinUser, JoinRoom, CreateRoom
from .models import Room


def createRoom(request):
    context = {}
    if request.method == "POST":
        if 'create_room_form' in request.POST:
            form = CreateRoom(request.POST)
            if form.is_valid():
                room = Room(name=form['room_name'])
                room.save()

                request.session['room_id'] = room.room_code
                request.session['nickname'] = form.cleaned_data['nickname']

                return redirect(f"/game/{room.room_code}")
            else:
                context['message'] = form.errors
    return render(request, "game/game-create-room.html", context)


def joinRoom(request, room_id):
    context = {}
    if request.session.get('room_id') == room_id and 'nickname' in request.session:
        return render(request, "game/game-lobby.html", context)
    print("dupa")
    return redirect("/")


class gameHomePage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        if request.method == 'POST':
            if 'join_form' in request.POST:
                form = JoinRoom(request.POST)
                if form.is_valid():
                    Room.objects.filter(room_code=form.cleaned_data['room_id']).exists()
                    request.session['room_id'] = form.cleaned_data['room_id']
                    context['room_id'] = form.cleaned_data['room_id']
                    return render(request, "game/game-user-form.html", context)
                else:
                    context['message'] = "Provided Room code does not exist"

            if 'user_form' in request.POST:
                form = JoinUser(request.POST)
                if form.is_valid():
                    request.session['nickname'] = form.cleaned_data['nickname']
                else:
                    context['message'] = form.errors

                return render(request, "game/game-lobby.html", context)

        return render(request, "game/game-home.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        return render(request, "game/game-home.html", context)

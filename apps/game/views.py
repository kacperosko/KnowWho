from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import JoinUser, JoinRoom, CreateRoom, AnswerQuestion, AnswerAssignForm
from .models import Room, Player, Question, Answer, AnswerAssign
from django.http.response import JsonResponse
from django.db.models import Q
import random
import secrets


def createRoom(request):
    context = {}
    if request.method == "POST":
        if 'create_room_form' in request.POST:
            form = CreateRoom(request.POST)
            if form.is_valid():
                room = Room()
                room.save()

                for key in list(request.session.keys()):
                    if not key.startswith("_"):  # skip keys set by the django system
                        del request.session[key]

                request.session['room_id'] = room.room_code
                request.session['nickname'] = form.cleaned_data['nickname']
                request.session['isHost'] = True

                return redirect(f"/game/lobby?room_code={room.room_code}")
            else:
                context['message'] = form.errors
    return render(request, "game/game-create-room.html", context)


def joinRoom(request):
    context = {}
    room_id = request.GET.get('room_code')
    if request.session.get('room_id') == room_id and 'nickname' in request.session:
        session_player_code = request.session.get('player_code')
        if session_player_code != '' and session_player_code is not None and session_player_code != 'null':
            if session_player_code[-11:] != request.session.get('room_id'):
                if 'player_code' in request.session:
                    del request.session['player_code']
                if 'player_id' in request.session:
                    del request.session['player_id']
        return render(request, "game/game-lobby.html", context)
    return redirect("/")


def wait_room(request):
    context = {}
    room_id = request.GET.get('room_code')
    status = request.GET.get('status')
    if status == "before":
        if request.session.get('room_id') == room_id and 'nickname' in request.session:
            players = Player.objects.filter(
                Q(room__room_code=request.session.get('room_id')) & ~Q(player_code=request.session.get('player_code')))
            # players = Player.objects.filter(room__room_code=request.session.get('room_id'), player_code=)
            for p in players:
                p.answered = Answer.objects.filter(related_player=p,
                                                   related_question_id=request.session.get('current_question_id')).exists()

            context['players'] = players
            # session_player_code = request.session.get('player_code')
            # if session_player_code != '' and session_player_code is not None and session_player_code != 'null':
            #     if session_player_code[-11:] != request.session.get('room_id'):
            #         request.session['player_code'] = ''
            return render(request, "game/game-waitroom.html", context)
    elif status == "after":
        if request.session['room_id'] == room_id:
            room = Room.objects.get(room_code=request.session['room_id'])
            answers = AnswerAssign.objects.filter(Q(related_player__room=room) & Q(related_answer__round=room.current_round) & ~Q(related_player__player_code=request.session['player_code']))
            print(answers)
            context['answers'] = answers
            return render(request, "game/game-waitroom.html", context)
    return redirect("/")


class QuestionService(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        print('QuestionService POST')
        if request.method == 'POST':
            print("QuestionService FORM POST")
            # if 'answer_question_form' in request.POST:
            print("answer_question_form")
            form = AnswerQuestion(request.POST)
            if form.is_valid():
                player_answer = form.cleaned_data['answer']
                player_room = Room.objects.get(room_code=request.session.get('room_id'))
                print('player_answer -> ', player_answer)
                print('player_room current_round -> ', player_room.current_round)
                print('player_code -> ', request.session['player_code'])
                print('current_question_id -> ', request.session.get('current_question_id'))
                player_answer = Answer(content=player_answer,
                                       related_player=Player.objects.get(player_code=request.session['player_code']),
                                       related_question_id=request.session['current_question_id'],
                                       round=player_room.current_round)
                # print('answer', answer)
                player_answer.save()
                print(f'LOG$$$ answer {player_answer.id} saved for player {player_answer.related_player.nickname}')
                # return redirect(f"/game/waitroom?room_code={player_room.room_code}")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        try:
            player_answer = Answer.objects.filter(related_player__player_code=request.session['player_code'],
                                                  related_question_id=request.session['current_question_id'])
            if player_answer.exists():
                return redirect(f"/game/waitroom?room_code={request.session['room_id']}&status=before")
        except Exception as e:
            print('error', e)

        context['question'] = request.session.get('current_question')
        return render(request, "game/game-question.html", context)


class KnowWho(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        print('KnowWho POST')
        if request.method == 'POST':
            print("KnowWho FORM POST")
            # if 'answer_question_form' in request.POST:
            print("answer_assign_form")
            form = AnswerAssignForm(request.POST)
            if form.is_valid():
                player_choice_player_code = form.cleaned_data['choice']
                room_code = request.session['room_id']
                room = Room.objects.get(room_code=room_code)
                answers = AnswerAssign.objects.filter(related_answer__round=room.current_round,
                                                      related_player__player_code=request.session[
                                                          'player_code']).first()
                print('player_choice_player_code -> ', player_choice_player_code)
                isGoodChoice = False

                if answers.related_answer.related_player.player_code == player_choice_player_code:
                    isGoodChoice = True
                print('isGoodChoice', isGoodChoice)
                answers.player_choice = Player.objects.get(player_code=player_choice_player_code)
                answers.isPoint = isGoodChoice
                answers.save()
                print("$$$ LOG answer saved succesfully")

                return JsonResponse({'success': True})
                # return JsonResponse({'success': True})
            else:
                print("invalid")
                return JsonResponse({'success': False, 'errors': form.errors})
                # return render(request, "game/game-knowho-single.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        try:
            room_code = request.GET.get('room_code')
            room = Room.objects.get(room_code=room_code)
            answers = AnswerAssign.objects.filter(related_answer__round=room.current_round, related_player__room=room)
            player_answers = answers.filter(related_player__player_code=request.session['player_code'])
            # player_answers = AnswerAssign.objects.filter(related_player__player_code=request.session['player_code'], related_answer__round=room.current_round)
            players_to_choose = []
            for anaswer_player in answers.exclude(related_player__player_code=request.session['player_code']):
                players_to_choose.append(anaswer_player.related_player)
            # list(
            #     player_answers.exclude(related_player__player_code=player_to_exclude_code).values_list('related_player',
            #                                                                                            flat=True))

            context['players'] = players_to_choose
            print('player_answers', player_answers)
            print('players_to_choose', players_to_choose)
            if player_answers.exists():
                player_answers = list(player_answers)
                if len(player_answers):
                    context['answers'] = player_answers[0]
                else:
                    context['answers'] = player_answers
        except Exception as e:
            print('error', e)

        return render(request, "game/game-knowho-single.html", context)


def update_session_variable(request):
    success = False
    try:
        session_name = request.GET.get("session_name", "")
        session_value = request.GET.get("session_value", "")
        print(f"Upadting variable '{session_name}' with value '{session_value}'")
        request.session[session_name] = str(session_value)
        success = True
        if 'player_code' in request.session:
            print('test session player_code -> ', request.session['player_code'])
        if 'player_id' in request.session:
            print('test session player_id -> ', request.session['player_id'])
    except Exception as e:
        print('update_session_variable error:', e)
    return JsonResponse({'success': success})


def clear_player_session(request):
    print("clearing player session")
    del request.session


def get_question(request):
    print("get question")
    success = False
    context = {}
    try:

        room = Room.objects.get(room_code=request.GET.get('room_code'))
        if request.GET.get('action') == 'start_game':
            room.isStarted = True
        room.current_round += 1
        room.save()

        question = Question.objects.order_by('?').first()
        context['question'] = question.content
        context['question_id'] = question.id
        print(question.content)
        success = True
    except Exception as e:
        print('get_question error:', e)
    context['success'] = success
    print('get_question status:', success)

    return JsonResponse(context)


class gameHomePage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        if request.method == 'POST':
            print("gameHomePage FORM POST")
            if 'join_form' in request.POST:
                print("join_form")
                form = JoinRoom(request.POST)
                if form.is_valid():
                    room = Room.objects.filter(room_code=form.cleaned_data['room_id'])
                    if not room:
                        context['message'] = "Provided Room code does not exist"
                        return render(request, "game/game-home.html", context)
                    if room.first().isStarted:
                        context['message'] = "Game in provided room has already started :("
                        return render(request, "game/game-home.html", context)
                    print('room.isStarted', room.first().isStarted)
                    request.session['room_id'] = form.cleaned_data['room_id']
                    context['room_id'] = form.cleaned_data['room_id']
                    return render(request, "game/game-user-form.html", context)

            if 'user_form' in request.POST:
                print("user form")
                form = JoinUser(request.POST)
                if form.is_valid():
                    request.session['nickname'] = form.cleaned_data['nickname']
                    context['room_id'] = request.session['room_id']
                else:
                    print("user_form error", form.errors)
                    context['message'] = form.errors

                return redirect(f"/game/lobby?room_code={request.session['room_id']}")
                # return render(request, "game/game-lobby.html", context)

        return render(request, "game/game-home.html", context)

    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        return render(request, "game/game-home.html", context)


def shuffle_players(request):
    room_code = request.GET.get('room_code')
    room = Room.objects.get(room_code=room_code)
    players_answer = Answer.objects.filter(related_player__room__room_code=room_code, round=room.current_round)
    players_to_choose = list(players_answer.values_list('related_player', flat=True))
    print('players_to_choose', players_to_choose)
    random.shuffle(players_to_choose)
    secure_random = secrets.SystemRandom()
    num_to_select = 1

    selection = []

    for p_answer in players_answer:
        finished = False
        while not finished:
            list_of_random_players = secure_random.sample(players_to_choose, num_to_select)
            random_player = list_of_random_players[0]
            if random_player != p_answer.related_player.id:
                selection.append(AnswerAssign(related_player=p_answer.related_player,
                                              related_answer=players_answer.get(related_player=random_player)))
                players_to_choose.remove(random_player)
                finished = True

    AnswerAssign.objects.bulk_create(selection)
    return JsonResponse({'message': 'Players shuffled successfully', 'success': True}, status=200)

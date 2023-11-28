from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import JoinUser, JoinRoom, CreateRoom, AnswerQuestion, AnswerAssignForm
from .models import Room, Player, Question, Answer, AnswerAssign, RoomRound
from django.http.response import JsonResponse
from django.db.models import Q, Sum
import random
import secrets
import json


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

                generate_question_rounds(room)

                request.session['room_id'] = room.room_code
                request.session['nickname'] = form.cleaned_data['nickname']
                request.session['isHost'] = True

                return redirect(f"/game/lobby?room_code={room.room_code}")
            else:
                context['message'] = form.errors
    return render(request, "game/game-create-room.html", context)


def generate_question_rounds(room):
    reached_max_round = False
    isMixed = False
    mode = 'single'
    current_room_round = RoomRound.objects.filter(room=room)
    if current_room_round.exists():
        iterate_round = current_room_round.latest('round').round + 1
    else:
        iterate_round = 1

    questions = Question.objects.values_list('id', flat=True).all()
    round_rooms_to_create = []
    used_questions = []
    if questions.count() < room.max_rounds:
        room.max_rounds = questions.count()
        room.save()

    if room.game_mode == 'mixed':
        isMixed = True
    if room.game_mode == 'multiple':
        mode = 'multiple'
    while not reached_max_round:
        reached_max_round = iterate_round == room.max_rounds

        question_id = questions.exclude(id__in=used_questions).order_by('?').first()
        room_round_question = RoomRound.objects.filter(room=room, question_id=question_id)
        if not room_round_question.exists():
            if isMixed:
                mode = 'single' if iterate_round%2==0 else 'multiple'
            round_rooms_to_create.append(RoomRound(question_id=question_id, room=room, round=iterate_round, mode=mode))
            used_questions.append(question_id)
            iterate_round += 1

    RoomRound.objects.bulk_create(round_rooms_to_create)


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
                                                   related_question_id=request.session.get(
                                                       'current_question_id')).exists()

            context['players'] = players
            return render(request, "game/game-waitroom.html", context)
    elif status == "after":
        if request.session['room_id'] == room_id:
            room = Room.objects.get(room_code=request.session['room_id'])
            answers_to_display = []
            players_to_display = []
            answers = AnswerAssign.objects.filter(
                Q(related_player__room=room) & Q(related_answer__round=room.current_round) & ~Q(
                    related_player__player_code=request.session['player_code']))

            for a in answers:
                if a.related_player.id not in players_to_display:
                    answers_to_display.append(a)
                    players_to_display.append(a.related_player.id)

            print(answers_to_display)
            context['answers'] = answers_to_display
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


def get_results(request):
    room_id = request.GET.get('room_code')
    context = {}
    print('show results')
    if request.session['room_id'] == room_id:
        room = Room.objects.get(room_code=request.session['room_id'])
        answers = Answer.objects.filter(related_player__room=room, round=room.current_round).order_by('related_player__nickname')
        players = []
        answers_assign = AnswerAssign.objects.filter(related_player__room=room,
                                                     related_answer__round=room.current_round).order_by('related_player__nickname')
        for a in answers:
            a.related_player.current_round_score = answers_assign.filter(related_player=a.related_player, isPoint=True).count()
            players.append(a.related_player)

        for a in answers:
            temp_assign = []
            # a.answer_assign = list(answers_assign.filter(related_answer_id=a.id).order_by('related_player__nickname'))
            for p in players:
                player_choice = answers_assign.filter(related_player=p, related_answer=a)
                if player_choice.exists():
                    temp_player = player_choice.first()
                    # temp_player.related_player.current_round_score = answers_assign.filter(related_player=temp_player.related_player, isPoint=True).count()
                    # print('score -> ', temp_player.related_player.current_round_score)

                    temp_assign.append(player_choice.first())
                else:
                    temp_assign.append(None)
            a.answer_assign = temp_assign
        context['question'] = request.session['current_question']
        context['answers'] = answers
        context['players'] = list(players)
        return render(request, "game/game-results.html", context)


def get_finish(request):
    context = {}
    players = Player.objects.filter(room__room_code=request.session['room_id'])
    answer_assign = AnswerAssign.objects.filter(related_player__in=players)

    for p in players:
        if p.player_code == request.session['player_code']:
            p.nickname += ' (You)'
        temp_assign = answer_assign.filter(related_player_id=p.id)
        for a in temp_assign:
            if a.isPoint:
                p.score += 1

    players = list(players)
    players.sort(key=lambda x: x.score, reverse=True)
    print(players)

    context['players'] = players
    return render(request, "game/game-finish.html", context)


class KnowWho(View):
    @staticmethod
    def post(request, *args, **kwargs):
        context = {}
        print('KnowWho POST')
        if request.method == 'POST':
            print("KnowWho FORM POST")
            room_code = request.session['room_id']
            room = Room.objects.get(room_code=room_code)

            if request.POST.get("mode", "") == "multiple":
                answers = request.POST.get("answers", "")
                print('answers')
                print(answers)
                if answers == "":
                    return JsonResponse({'success': False, 'errors': "empty answers"})
                answers = json.loads(answers)
                answer_assign_to_create = []
                players_answers = Answer.objects.filter(related_player__room=room, round=room.current_round)
                players = Player.objects.filter(room=room)
                answer_assignee = AnswerAssign.objects.filter(related_player__player_code=request.session['player_code'])

                for a in answers:
                    temp_aa = answer_assignee.get(
                        related_answer=players_answers.get(answer_code=a['answer_code']))
                    temp_aa.player_choice = players.get(player_code=a['player_code'])
                    if temp_aa.player_choice.player_code == temp_aa.related_answer.related_player.player_code:
                        temp_aa.isPoint = True
                    answer_assign_to_create.append(temp_aa)

                AnswerAssign.objects.bulk_update(answer_assign_to_create, ['isPoint', 'player_choice'])
                return JsonResponse({'success': True})

            form = AnswerAssignForm(request.POST)
            print("answer_assign_form")
            if form.is_valid():
                player_choice_player_code = form.cleaned_data['choice']

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
            room_round = RoomRound.objects.get(room=room, round=room.current_round)
            question_round = RoomRound.objects.get(round=room.current_round, room=room)
            answers = AnswerAssign.objects.filter(related_answer__round=room.current_round, related_player__room=room)
            player_answers = answers.filter(related_player__player_code=request.session['player_code'])
            # player_answers = AnswerAssign.objects.filter(related_player__player_code=request.session['player_code'], related_answer__round=room.current_round)
            players_to_choose = []
            for anaswer_player in answers.exclude(related_player__player_code=request.session['player_code']):
                if anaswer_player.related_player not in players_to_choose:
                    players_to_choose.append(anaswer_player.related_player)

            context['players'] = players_to_choose
            print('player_answers', player_answers)
            print('players_to_choose', players_to_choose)
            if player_answers.exists():
                player_answers = list(player_answers)
                if question_round.mode == 'single':
                    context['answers'] = player_answers[0]
                else:
                    context['answers'] = list(player_answers)
                    print(context['answers'])
        except Exception as e:
            print('error', e)

        if room_round.mode == 'multiple':
            return render(request, "game/game-knowho-multiple.html", context)

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

        if room.current_round > room.max_rounds:
            context['status'] = 'finish'
            return JsonResponse(context)

        room.save()
        question = RoomRound.objects.get(room=room, round=room.current_round).question
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
    room_round = RoomRound.objects.get(room=room, round=room.current_round)
    players_answer = Answer.objects.filter(related_player__room__room_code=room_code, round=room.current_round)
    players_to_choose = list(players_answer.values_list('related_player', flat=True))
    print('players_to_choose', players_to_choose)
    random.shuffle(players_to_choose)
    selection = []

    if room_round.mode == 'multiple':
        for p_answer in players_answer:
            for player in players_to_choose:
                if player != p_answer.related_player.id:
                    print(f"assigne {player} with {p_answer.related_player.id}")
                    selection.append(AnswerAssign(related_player=p_answer.related_player,
                                                  related_answer=players_answer.get(related_player=player)))
    else:
        secure_random = secrets.SystemRandom()
        num_to_select = 1
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

from django.db import models
import uuid

GAME_MODES_CHOICES = (
    ('mixed', 'MIXED'),
    ('single', 'SINGLE'),
    ('multiple', 'MULTIPLE'),
)


class Room(models.Model):
    room_code = models.CharField(max_length=11)
    isStarted = models.BooleanField(default=False)
    current_round = models.IntegerField(default=0)
    max_rounds = models.IntegerField(default=4)
    game_mode = models.CharField(max_length=10, choices=GAME_MODES_CHOICES, default='mixed')

    def generate_unique_room_code(self):
        while True:
            room_code = f'{uuid.uuid4().hex[:5]}-{uuid.uuid4().hex[:5]}'
            if not Room.objects.filter(room_code=room_code).exists():
                return room_code

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = self.generate_unique_room_code()
        super().save(*args, **kwargs)


QUESTION_MODES_CHOICES = (
    ('text', 'TEXT'),
    ('draw', 'DRAW'),
    ('player', 'PLAYER'),
)


class Question(models.Model):
    content = models.CharField(max_length=255, blank=False, null=True)
    question_mode = models.CharField(max_length=16, choices=QUESTION_MODES_CHOICES, default='text')


MODES_CHOICES = (
    ('single', 'SINGLE'),
    ('multiple', 'MULTIPLE'),
    ('draw', 'DRAW'),
)


class RoomRound(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=False, null=False, related_name='RoomRound_room')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='RoomRound_question')
    mode = models.CharField(max_length=10, choices=MODES_CHOICES, default='multiple')
    round = models.IntegerField(blank=False, default=0)


class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=False, null=False, related_name='player_room')
    nickname = models.CharField(max_length=255, blank=False, null=False)
    player_code = models.CharField(max_length=270, blank=False, null=True, unique=True)

    score = 0
    answered = False
    current_round_score = 0

    def generate_unique_player_code(self):
        return self.nickname.upper().replace(' ', '_') + "_" + self.room.room_code

    def save(self, *args, **kwargs):
        self.player_code = self.generate_unique_player_code()
        super().save(*args, **kwargs)


class Answer(models.Model):
    answer_code = models.CharField(max_length=11)
    related_question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True,
                                         related_name='answer_question_relationship')
    related_player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='answer_player_relationship')
    content = models.CharField(max_length=255, blank=True, null=True)
    round = models.IntegerField(blank=False, default=0)

    answer_assign = []

    def generate_unique_answer_code(self):
        while True:
            answer_code = f'{uuid.uuid4().hex[:5]}-{uuid.uuid4().hex[:5]}'
            if not Answer.objects.filter(answer_code=answer_code).exists():
                return answer_code

    def save(self, *args, **kwargs):
        if not self.answer_code:
            self.answer_code = self.generate_unique_answer_code()
        super().save(*args, **kwargs)


class AnswerAssign(models.Model):
    related_player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='answer_assign_player_relationship')
    related_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='answer_assign_answer_relationship')
    player_choice = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='answer_assign_player_choice_relationship')
    isPoint = models.BooleanField(default=False)

from django.contrib import admin
from .models import Room, Player, Question, Answer, AnswerAssign, RoomRound


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'isStarted', 'current_round')
    search_fields = ('room_code',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'nickname', 'player_code', 'answered')
    search_fields = ('nickname', 'player_code')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'question_mode')
    search_fields = ('content',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'related_question', 'related_player', 'content', 'round')
    search_fields = ('content',)
    list_filter = ('round', 'related_question', 'related_player')


@admin.register(RoomRound)
class RoomRound(admin.ModelAdmin):
    list_display = ('room', 'round', 'get_question', 'mode')

    @admin.display(description="Question")
    def get_question(self, obj):
        return (obj.question.content)


@admin.register(AnswerAssign)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('related_player', 'get_related_player', 'related_answer', 'get_related_answer_player', 'isPoint')

    @admin.display(description="Related Player")
    def get_related_player(self, obj):
        return (obj.related_player.nickname)

    @admin.display(description="Related Answer Player")
    def get_related_answer_player(self, obj):
        return obj.related_answer.related_player.nickname

from django.contrib import admin, messages
from .models import Room, Player, Question, Answer, AnswerAssign, RoomRound
from .data_handler import export_to_JSON, load_from_JSON
from django.urls import path
from django.http import HttpResponseRedirect


class RoomRound_ItemInline(admin.TabularInline):
    model = RoomRound
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ['round', ]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'isStarted', 'current_round')
    search_fields = ('room_code',)

    inlines = [
        RoomRound_ItemInline,
    ]


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_room_code', 'nickname', 'player_code')
    search_fields = ('nickname', 'player_code')

    @admin.display(description="Room Code")
    def get_room_code(self, obj):
        return obj.room.room_code


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    change_list_template = "entities/question_tools.html"
    list_display = ('content', 'question_mode', 'global_key')
    search_fields = ('content',)
    readonly_fields = ('global_key',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_questions/', self.export_questions),
            path('load_questions/', self.load_questions),
            path('generate_global_keys/', self.generate_global_keys),
        ]
        return my_urls + urls

    def export_questions(self, request):
        export_to_JSON(self.model.objects.all())
        self.message_user(request, "All questions exported")
        return HttpResponseRedirect("../")

    def generate_global_keys(self, request):
        try:
            questions = self.model.objects.all()
            for q in questions:
                q.generate_unique_global_key()
            self.model.objects.bulk_update(questions, fields=["global_key"])
            self.message_user(request, "Globals keys are generated")
        except Exception as e:
            self.message_user(request, e, level=messages.ERROR)
        return HttpResponseRedirect("../")

    def load_questions(self, request):
        result = load_from_JSON(self.model)
        if result.is_success():
            self.message_user(request, result.get_message(), level=messages.SUCCESS)
        else:
            self.message_user(request, result.get_message(), level=messages.ERROR)
        return HttpResponseRedirect("../")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'related_question', 'related_player', 'content', 'round')
    search_fields = ('content',)
    list_filter = ('round', 'related_question', 'related_player')


@admin.register(RoomRound)
class RoomRound(admin.ModelAdmin):
    list_display = ('get_room_code', 'round', 'get_question', 'mode')
    search_fields = ('get_room_code',)

    @admin.display(description="Question")
    def get_question(self, obj):
        return obj.question.content

    @admin.display(description="Room Code")
    def get_room_code(self, obj):
        return obj.room.room_code


@admin.register(AnswerAssign)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('related_player', 'get_related_player', 'related_answer', 'get_related_answer_player', 'isPoint')

    @admin.display(description="Related Player")
    def get_related_player(self, obj):
        return obj.related_player.nickname

    @admin.display(description="Related Answer Player")
    def get_related_answer_player(self, obj):
        return obj.related_answer.related_player.nickname

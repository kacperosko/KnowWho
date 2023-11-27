from django.urls import path, include
from apps.game import views as game_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", game_views.gameHomePage.as_view(), name="game-home"),
    path("create-room", game_views.createRoom, name="game-home"),

    path("game/lobby", game_views.joinRoom, name="game-home"),
    path("game/question", game_views.QuestionService.as_view(), name="game-home"),
    path("game/waitroom", game_views.wait_room, name="game-wait_room"),
    path("game/know_who", game_views.KnowWho.as_view(), name="game-know_who"),
    path("game/results", game_views.get_results, name="game-get_results"),
    path("game/finish", game_views.get_finish, name="game-get_finish"),

    path("update_session_variable", game_views.update_session_variable, name="game-update_session_variable"),
    path("clear_player_session", game_views.clear_player_session, name="game-clear_player_session"),
    path("shuffle_players", game_views.shuffle_players, name="game-shuffle_players"),
    path("get_question", game_views.get_question, name="game-QuestionService"),
]

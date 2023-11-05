from django.urls import path, include
from apps.game import views as game_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", game_views.gameHomePage.as_view(), name="game-home"),
    path("create-room", game_views.createRoom, name="game-home"),
    path("game/<room_id>", game_views.joinRoom, name="game-home"),

    # # login-section
    # path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
    # path("auth/logout/", LogoutView.as_view(), name="logout-user"),
]

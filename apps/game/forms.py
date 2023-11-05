from django import forms


class JoinRoom(forms.Form):
    room_id = forms.CharField(max_length=12)


class JoinUser(forms.Form):
    nickname = forms.CharField(max_length=100)


class CreateRoom(forms.Form):
    room_name = forms.CharField(max_length=32)
    nickname = forms.CharField(max_length=100)

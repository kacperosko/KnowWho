from django import forms


class JoinRoom(forms.Form):
    room_id = forms.CharField(max_length=12)


class JoinUser(forms.Form):
    nickname = forms.CharField(max_length=100)


class CreateRoom(forms.Form):
    nickname = forms.CharField(max_length=100)


class AnswerQuestion(forms.Form):
    answer = forms.CharField(max_length=255, required=True)


class AnswerAssignForm(forms.Form):
    choice = forms.CharField(max_length=255, required=True)

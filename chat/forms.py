from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    """
    Форма для создания и обновления экземпляров «Сообщений».
    """

    class Meta:
        model = Message
        fields = ["content"]

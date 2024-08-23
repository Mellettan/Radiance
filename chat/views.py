from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View

from accounts.models import CustomUser

from .models import Message


def get_chat_users(user: CustomUser) -> QuerySet:
    """
    Получает отдельный список пользователей, с которыми данный пользователь обменивался сообщениями.

    Сюда входят:
    - пользователи, которые отправили сообщения данному пользователю,
    - пользователи, которые получали сообщения от данного пользователя,
    - сам пользователь.

    Args:
        user (CustomUser): Пользователь, для которого нужно получить участников чата.

    Returns:
        QuerySet: Отдельный список экземпляров `CustomUser`, упорядоченный по имени пользователя.
    """
    sent_users = CustomUser.objects.filter(sent_messages__recipient=user).distinct()
    received_users = CustomUser.objects.filter(received_messages__sender=user).distinct()
    current_user = CustomUser.objects.filter(pk=user.pk).distinct()
    chat_users = sent_users | received_users | current_user

    return chat_users.distinct().order_by('username')


class ChatView(LoginRequiredMixin, View):
    """
    Представление для отображения интерфейса чата между вошедшим в систему пользователем и другим пользователем.

    Это представление извлекает и отображает сообщения чата, которыми обмениваются текущий пользователь
    и еще один пользователь, идентифицированный `user_id`. Он также предоставляет чаты текущего пользователя.
    """

    def get(self, request: HttpRequest, user_id: int) -> HttpRequest:
        """
        Обрабатывает запросы GET для отображения интерфейса чата с указанным пользователем.

        Args:
            request (HttpRequest): Объект запроса, используемый для генерации этого ответа.
            user_id (int): Идентификатор другого пользователя, участвующего в чате.

        Returns:
            HttpResponse: Ответ, содержащий отображаемый интерфейс чата.
        """
        other_user = CustomUser.objects.get(id=user_id)

        message_list = Message.objects.filter(
            Q(sender=other_user, recipient=request.user) | Q(sender=request.user, recipient=other_user)
        ).select_related('sender', 'recipient').order_by('timestamp')  # Отсортированный список сообщений данной пары пользователей по времени

        context = {
            'other_user': other_user,
            'user_id': user_id,
            'message_list': message_list,
            'chat_users': get_chat_users(request.user)
        }
        return render(request, 'chat/chat.html', context)


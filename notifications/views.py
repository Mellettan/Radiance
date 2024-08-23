from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from notifications.models import Notification


class NotificationView(LoginRequiredMixin, View):
    """
    Представление для отображения уведомлений пользователя.

    Это представление отображает список уведомлений, относящихся к текущему авторизованному пользователю.
    Оно наследует LoginRequiredMixin, что требует авторизации пользователя для доступа к этой странице.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Обрабатывает GET-запрос для отображения уведомлений.

        Этот метод фильтрует уведомления для текущего пользователя, сортирует их по дате создания
        (от самых новых к самым старым), отмечает все уведомления как прочитанные и передает их в контекст
        для рендеринга HTML-шаблона.

        Args:
            request (HttpRequest): Объект запроса, содержащий данные о текущем запросе.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ с отрендеренной страницей уведомлений.
        """
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        context = {
            'notifications': notifications
        }
        notifications.update(is_read=True)
        return render(request, 'notifications/notifications.html', context)

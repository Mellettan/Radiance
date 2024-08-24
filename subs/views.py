from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from accounts.models import CustomUser, Subscription


class SubsView(View):
    """
    Представление для отображения списка пользователей и подписок.

    Это представление обрабатывает запросы GET для отображения списка подписок
    пользователя и поиска пользователей. Оно также поддерживает пагинацию
    для списка пользователей.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Обрабатывает GET-запрос для отображения списка подписок и поиска пользователей.

        Проверяет, авторизован ли пользователь. Если да, то извлекает и отображает его
        подписки. Выполняет поиск пользователей по запросу, если таковой имеется.
        Реализует пагинацию для списка пользователей.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            HttpResponse: Ответ с отрендеренным шаблоном и контекстом.
        """
        if request.user.is_authenticated:
            subscriptions = Subscription.objects.filter(follower=request.user)
        else:
            subscriptions = Subscription.objects.none()

        query = request.GET.get("q", "")
        page_number = request.GET.get("page", 1)

        if query:
            user_list = CustomUser.objects.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            ).order_by("username")
        else:
            user_list = CustomUser.objects.none()
        paginator = Paginator(user_list, 5)
        page_obj = paginator.get_page(page_number)

        context = {
            "subscriptions": subscriptions,
            "page_obj": page_obj,
        }

        return render(request, "subs/subs.html", context)

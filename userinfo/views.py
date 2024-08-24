from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class UserInfoView(View):
    """
    Представление для отображения и обновления информации о пользователе.

    Этот класс обрабатывает запросы на получение и обновление информации о пользователе.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает GET-запрос для отображения страницы информации о пользователе.

        Этот метод рендерит шаблон `userinfo/userinfo.html`, который отображает текущую информацию
        о пользователе.

        Args:
            request (HttpRequest): Объект запроса от клиента.

        Returns:
            HttpResponse: Ответ с отрендеренной страницей информации о пользователе.
        """
        return render(request, "userinfo/userinfo.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает POST-запрос для обновления аватара пользователя.

        Этот метод проверяет, был ли загружен файл с аватаром, и если да, то сохраняет его
        как новый аватар для текущего пользователя. После обновления, рендерится тот же шаблон,
        чтобы отобразить изменения.

        Args:
            request (HttpRequest): Объект запроса от клиента, содержащий файл с аватаром.

        Returns:
            HttpResponse: Ответ с отрендеренной страницей информации (с обновленным аватаром) о пользователе.
        """
        if "avatar" in request.FILES:
            request.user.avatar = request.FILES["avatar"]
            request.user.save()
        return render(request, "userinfo/userinfo.html")

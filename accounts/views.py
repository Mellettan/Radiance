from typing import Optional

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import FormView

from .forms import ChangeEmailForm, CustomLoginForm, CustomRegForm
from .models import CustomUser
from .tasks import send_confirmation_email


class LoginView(FormView):
    """
    Представление, которое обрабатывает вход пользователя с помощью настраиваемой
    формы входа.

    Attributes:
        template_name (str): путь к шаблону, отображающему форму входа.
        form_class (CustomLoginForm): класс формы, используемый для обработки и
            проверки пользовательского ввода.
        success_url (str): URL-адрес, на который будет перенаправлен пользователь
            после успешного входа в систему.
    """

    template_name = "accounts/login.html"
    form_class = CustomLoginForm
    success_url = reverse_lazy("custom_login_redirect")

    def form_valid(self, form: CustomLoginForm) -> HttpResponseRedirect:
        user = form.get_user()
        if user is not None:
            auth_login(self.request, user)
        return super().form_valid(form)


class ChangeEmailView(FormView):
    """
    Представление, которое обрабатывает процесс изменения адреса электронной почты
    пользователя.

    Attributes:
        template_name (str): Путь к шаблону, который отображает форму изменения
            адреса электронной почты.
        form_class (ChangeEmailForm): Класс формы, используемый для обработки
            пользовательского ввода и проверки изменения адреса электронной почты.
        success_url (str): URL-адрес для перенаправления после успешной отправки формы.
            Здесь он перенаправляется на ту же страницу.
    """

    template_name = "accounts/change_email.html"
    form_class = ChangeEmailForm
    success_url = "."

    def form_valid(self, form: ChangeEmailForm) -> HttpResponseRedirect:
        """
        Called when the form is submitted and is valid.

        Args:
            form (ChangeEmailForm): Экземпляр формы с действительными данными.

        Returns:
            HttpResponseRedirect: Перенаправление на `success_url`.

        Этот метод выполняет следующие действия:
            1. Генерирует токен для подтверждения по электронной почте, используя
               `default_token_generator`.
            2. Кодирует первичный ключ пользователя («uid») для безопасного
               использования в URL-адресах.
            3. Создает ссылку подтверждения с токеном и `uid`.
            4. Отправляет электронное письмо с подтверждением и сгенерированной
               ссылкой на новый адрес электронной почты.
            5. Сохраняет новый адрес электронной почты в поле temp_email объекта
               пользователя.
            6. Отображает информационное сообщение о том, что ссылка для подтверждения
               отправлена.
        """
        user: CustomUser = self.request.user
        token: str = default_token_generator.make_token(user)
        uid: str = urlsafe_base64_encode(force_bytes(user.pk))
        domain: str = self.request.get_host()
        subject = "Email Confirmation"
        scheme_and_domain = f"{self.request.scheme}://{domain}"
        path = reverse("accounts:confirm_email", kwargs={"uidb64": uid, "token": token})
        link = f"{scheme_and_domain}{path}"
        message = f"Please confirm your email address by clicking on the link: {link}"
        send_confirmation_email.send(subject, message, [form.cleaned_data["email"]])
        user.temp_email = form.cleaned_data["email"]
        user.save()
        messages.info(
            self.request, "Ссылка для подтверждения отправлена на указанный адрес"
        )
        return super().form_valid(form)


class ConfirmEmailView(View):
    """
    Представление, которое обрабатывает подтверждение адреса электронной
    почты пользователя.
    """

    def get(
        self, request: HttpRequest, uidb64: str, token: str
    ) -> HttpResponseRedirect:
        """
        Обрабатывает запросы GET для подтверждения адреса электронной
        почты пользователя.

        Args:
            request (HttpRequest): Текущий объект запроса.
            uidb64 (str): Идентификатор пользователя в кодировке Base64.
            token (str): Токен, созданный для подтверждения по электронной почте.

        Returns:
            HttpResponseRedirect: Перенаправляет пользователя на определенный URL-адрес
                после обработки подтверждения.

        Этот метод выполняет следующие действия:
            1. Декодирует идентификатор пользователя (uidb64) для извлечения
               соответствующего пользователя из базы данных.
            2. Проверяет, существует ли пользователь и действителен ли токен.
            3. Если токен действителен и у пользователя есть временный адрес
               электронной почты, адрес электронной почты подтверждается:
                 - Для параметра `email_verified` устанавливается значение True.
                 - Временный адрес электронной почты («temp_email») перемещен в
                   основное поле «email».
                 - Поле temp_email очищается.
            4. Если подтверждение прошло успешно, отобразится сообщение об успехе.
               Если нет, отображается сообщение об ошибке.
            5. Перенаправляет пользователя на страницу с его постами.
        """
        try:
            uid: bytes = force_bytes(urlsafe_base64_decode(uidb64))
            user: Optional[CustomUser] = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if user.temp_email:
                user.email_verified = True
                user.email = user.temp_email
                user.temp_email = None
                user.save()
                messages.success(request, "Ваш адрес электронной почты подтвержден.")
            else:
                messages.error(
                    request,
                    (
                        "Ссылка для подтверждения недействительна "
                        "или уже использована.",
                    ),
                )
        else:
            messages.error(request, "Ссылка для подтверждения недействительна.")

        return redirect("custom_login_redirect")


class RegView(FormView):
    """
    Представление, которое обрабатывает регистрацию пользователей.

    Attributes:
        template_name (str): Путь к шаблону, отображающему форму регистрации.
        form_class (CustomRegForm): Класс формы, используемый для обработки
            пользовательского ввода и проверки регистрации.
        success_url (str): URL-адрес для перенаправления после успешной регистрации.
            В данном случае это страница с постами пользователя.
    """

    template_name = "accounts/reg.html"
    form_class = CustomRegForm
    success_url = reverse_lazy("custom_login_redirect")

    def form_valid(self, form: CustomRegForm) -> HttpResponseRedirect:
        user = form.save()
        auth_login(self.request, user)
        return super().form_valid(form)


class DeleteView(View):
    """
    Представление, которое обрабатывает удаление аккаунта пользователя.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "accounts/delete.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        if "delete_button" in request.POST:
            user = request.user
            user.delete()
            return redirect("custom_login_redirect")
        else:
            return render(request, "accounts/delete.html")


class CustomPasswordChangeView(PasswordChangeView):
    """
    Представление, которое обрабатывает процесс изменения пароля пользователя.

    Attributes:
        template_name (str): Путь к шаблону, отображающему форму смены пароля.
        success_url (str): URL-адрес для перенаправления после успешной смены пароля.
    """

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("custom_login_redirect")

    def form_valid(self, form: PasswordChangeForm) -> HttpResponseRedirect:
        messages.success(self.request, "Ваш пароль был успешно изменён!")
        return super().form_valid(form)

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import ChangeEmailForm, CustomLoginForm


class LoginViewTestCase(TestCase):
    """
    Тестовый класс для проверки функциональности представления входа в систему.

    Этот класс содержит тесты для проверки корректности отображения формы входа,
    успешного входа в систему и обработки ошибок при неверных данных.
    """

    def setUp(self):
        """
        Подготавливает данные для тестов:
        - Создает клиента для выполнения запросов.
        - Создает тестового пользователя с указанным email и паролем.
        - Определяет URL для входа и успешного редиректа после входа.
        """
        self.client = Client()
        self.email = "testuser@test.com"
        self.password = "testpassword"
        self.user = get_user_model().objects.create_user(
            email=self.email, password=self.password
        )
        self.login_url = reverse("accounts:login")
        self.success_url = reverse("custom_login_redirect")

    def test_login_form_view(self):
        """
        Проверяет отображение формы входа в систему.

        Выполняет GET-запрос к странице входа и проверяет:
        - Код статуса ответа (должен быть 200).
        - Используемый шаблон (должен быть 'accounts/login.html').
        - Тип формы в контексте ответа (должен быть CustomLoginForm).
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertIsInstance(response.context["form"], CustomLoginForm)

    def test_login_success(self):
        """
        Проверяет успешный вход в систему с правильными данными.

        Выполняет POST-запрос с правильными данными (email и пароль) и проверяет:
        - Редирект на успешный URL.
        - Пользователь аутентифицирован.
        """
        response = self.client.post(
            self.login_url,
            {
                "email": self.email,
                "password": self.password,
            },
        )
        self.assertRedirects(response, self.success_url, fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        """
        Проверяет обработку ошибки при неверных данных для входа.

        Выполняет POST-запрос с неправильным паролем и проверяет:
        - Код статуса ответа (должен быть 200).
        - Наличие ошибки формы (должна быть ошибка 'Invalid email or password').
        """
        response = self.client.post(
            self.login_url,
            {
                "email": self.email,
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], None, "Invalid email or password"
        )


class ChangeEmailViewTestCase(TestCase):
    """
    Тестовый класс для проверки функциональности представления изменения email.

    Этот класс содержит тесты для проверки отображения формы изменения email,
    успешного изменения email и обработки ошибок при неверных данных.
    """

    def setUp(self):
        """
        Подготавливает данные для тестов:
        - Создает клиента для выполнения запросов.
        - Создает тестового пользователя с указанным email и паролем.
        - Выполняет вход пользователя.
        - Определяет URL для изменения email.
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.client.login(email="testuser@test.com", password="testpassword")
        self.change_email_url = reverse("accounts:change_email")
        self.success_url = reverse("accounts:change_email")

    def test_change_email_form_view(self):
        """
        Проверяет отображение формы изменения email.

        Выполняет GET-запрос к странице изменения email и проверяет:
        - Код статуса ответа (должен быть 200).
        - Используемый шаблон (должен быть 'accounts/change_email.html').
        - Тип формы в контексте ответа (должен быть ChangeEmailForm).
        """
        response = self.client.get(self.change_email_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/change_email.html")
        self.assertIsInstance(response.context["form"], ChangeEmailForm)

    def test_change_email_success(self):
        """
        Проверяет успешное изменение email с правильными данными.

        Выполняет POST-запрос с новым email и проверяет:
        - Редирект на успешный URL.
        - Обновление email у пользователя в базе данных.
        """
        new_email = "newemail@example.com"
        response = self.client.post(
            self.change_email_url,
            {
                "email": new_email,
            },
        )
        self.assertRedirects(response, self.success_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.temp_email, new_email)

    def test_change_email_invalid(self):
        """
        Проверяет обработку ошибки при изменении email с некорректными данными.

        Выполняет POST-запрос с пустым email и проверяет:
        - Код статуса ответа (должен быть 200).
        - Наличие ошибки формы (должна быть ошибка 'This field is required.').
        """
        response = self.client.post(
            self.change_email_url,
            {
                "email": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "This field is required."
        )


class ConfirmEmailViewTestCase(TestCase):
    """
    Тестовый класс для проверки функциональности подтверждения email.

    Этот класс содержит тесты для проверки успешного подтверждения email
    и обработки ошибок при использовании недействительного токена.
    """

    def setUp(self):
        """
        Подготавливает данные для тестов:
        - Создает клиента для выполнения запросов.
        - Создает тестового пользователя с указанным email и временным email.
        - Генерирует токен подтверждения и закодированный идентификатор пользователя.
        - Определяет URL для подтверждения email.
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user.temp_email = "newemail@example.com"
        self.user.save()
        self.token = default_token_generator.make_token(self.user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.confirm_email_url = reverse(
            "accounts:confirm_email",
            kwargs={"uidb64": self.uidb64, "token": self.token},
        )

    def test_confirm_email_success(self):
        """
        Проверяет успешное подтверждение email.

        Выполняет GET-запрос по URL подтверждения email и проверяет:
        - Редирект на URL успешного логина.
        - Обновление email у пользователя в базе данных.
        - Удаление временного email.
        """
        response = self.client.get(self.confirm_email_url)
        self.assertRedirects(
            response, reverse("custom_login_redirect"), fetch_redirect_response=False
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        self.assertIsNone(self.user.temp_email)

    def test_confirm_email_invalid_token(self):
        """
        Проверяет обработку ошибки при использовании недействительного токена.

        Выполняет GET-запрос с недействительным токеном и проверяет:
        - Редирект на URL успешного логина.
        - Наличие сообщения об ошибке в сообщениях.
        """
        invalid_token = "invalidtoken"
        url = reverse(
            "accounts:confirm_email",
            kwargs={"uidb64": self.uidb64, "token": invalid_token},
        )
        response = self.client.get(url)
        self.assertRedirects(
            response, reverse("custom_login_redirect"), fetch_redirect_response=False
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertTrue(
            str(messages[0]).startswith("Ссылка для подтверждения недействительна")
        )

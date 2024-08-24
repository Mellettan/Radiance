from django.db.models import Q
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import CustomUser

from .models import Message
from .views import get_chat_users


class ChatViewTests(TestCase):
    """
    Тесты для проверки функциональности представления чата.

    Этот класс содержит тесты для проверки работы представления чата,
    включая проверку доступа, отображения сообщений и пользователей,
    а также правильности обработки ситуации без сообщений.
    """

    def setUp(self):
        """
        Подготавливает данные для тестов:
        - Создает нескольких пользователей.
        - Создает сообщения между некоторыми пользователями.
        - Создает клиент для выполнения запросов.
        """
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com", username="user1", password="password1"
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@example.com", username="user2", password="password2"
        )
        self.user3 = CustomUser.objects.create_user(
            email="user3@example.com", username="user3", password="password3"
        )

        Message.objects.create(
            sender=self.user1, recipient=self.user2, content="Hello user2 from user1"
        )
        Message.objects.create(
            sender=self.user2, recipient=self.user1, content="Hello user1 from user2"
        )

        self.client = Client()

    def test_login_required(self):
        """
        Проверяет требование аутентификации для доступа к представлению чата.

        Выполняет GET-запрос к странице чата для другого пользователя без аутентификации и проверяет:
        - Переадресацию на страницу входа с параметром next, указывающим на страницу чата.
        """
        response = self.client.get(reverse("chat:chat", args=[self.user2.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/chat/{self.user2.id}/")

    def test_chat_view_with_messages(self):
        """
        Проверяет отображение сообщений в чате при наличии сообщений.

        Выполняет GET-запрос к странице чата для пользователя `user1`, предварительно войдя в систему, и проверяет:
        - Код статуса ответа (должен быть 200).
        - Используемый шаблон (должен быть 'chat/chat.html').
        - Корректность данных в контексте ответа:
          - other_user: Пользователь, с которым ведется чат.
          - user_id: ID пользователя, с которым ведется чат.
          - message_list: Список сообщений между пользователями, отсортированный по времени отправки.
          - chat_users: Список чатов текущего пользователя.
        """
        self.client.login(email="user1@example.com", password="password1")

        response = self.client.get(reverse("chat:chat", args=[self.user2.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/chat.html")

        self.assertEqual(response.context["other_user"], self.user2)
        self.assertEqual(response.context["user_id"], self.user2.id)
        self.assertQuerySetEqual(
            Message.objects.filter(
                Q(sender=self.user1, recipient=self.user2)
                | Q(sender=self.user2, recipient=self.user1)
            )
            .select_related("sender", "recipient")
            .order_by("timestamp"),
            response.context["message_list"],
        )
        self.assertQuerySetEqual(
            get_chat_users(self.user1), response.context["chat_users"]
        )

    def test_chat_view_with_no_messages(self):
        """
        Проверяет отображение представления чата, когда нет сообщений.

        Выполняет GET-запрос к странице чата для пользователя 1 с другим пользователем, с которым нет сообщений, и проверяет:
        - Код статуса ответа (должен быть 200).
        - Используемый шаблон (должен быть 'chat/chat.html').
        - Корректность данных в контексте ответа:
          - other_user: Пользователь, с которым ведется чат.
          - user_id: ID пользователя, с которым ведется чат.
          - message_list: Пустой список сообщений.
          - chat_users: Список чатов текущего пользователя.
        """
        self.client.login(email="user1@example.com", password="password1")

        response = self.client.get(reverse("chat:chat", args=[self.user3.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/chat.html")

        self.assertEqual(response.context["other_user"], self.user3)
        self.assertEqual(response.context["user_id"], self.user3.id)
        self.assertQuerySetEqual(
            CustomUser.objects.none(), response.context["message_list"]
        )
        self.assertQuerySetEqual(
            get_chat_users(self.user1), response.context["chat_users"]
        )

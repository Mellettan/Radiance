from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser, Subscription
from notifications.models import Notification


class NotificationViewTest(TestCase):
    """
    Тесты для представления NotificationView.

    Этот тестовый класс проверяет корректность работы представления уведомлений для пользователя,
    включая проверки на необходимость авторизации, правильность отображаемых уведомлений и
    обновление статуса прочтения уведомлений.
    """

    def setUp(self):
        """
        Устанавливает тестовую среду.

        Этот метод создает тестового пользователя и другого пользователя, а также создает для них уведомления.
        Кроме того, выполняется авторизация тестового пользователя для последующего использования в тестах.
        """
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.client.login(email="testuser@example.com", password="password")

        self.other_user = CustomUser.objects.create_user(
            email="otheruser@example.com", password="password"
        )

        self.user_notification = Notification.objects.create(
            user=self.user, message="Notification 1", created_at=timezone.now()
        )
        self.other_user_notification = Notification.objects.create(
            user=self.other_user,
            message="Other user notification",
            created_at=timezone.now(),
        )

    def test_login_required(self):
        """
        Проверяет, что доступ к странице уведомлений требует авторизации.

        Этот тест проверяет, что если пользователь не авторизован, он перенаправляется на страницу логина
        при попытке доступа к странице уведомлений.
        """
        self.client.logout()
        response = self.client.get(reverse("notifications:notifications"))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('notifications:notifications')}"
        )

    def test_correct_notifications_displayed(self):
        """
        Проверяет, что отображаются только уведомления текущего пользователя.

        Этот тест проверяет, что на странице уведомлений отображаются только те уведомления,
        которые принадлежат текущему авторизованному пользователю.
        """
        response = self.client.get(reverse("notifications:notifications"))
        self.assertEqual(response.status_code, 200)
        notifications = response.context["notifications"]
        self.assertEqual(len(notifications), 1)
        self.assertNotIn(self.other_user_notification, notifications)

    def test_notifications_marked_as_read(self):
        """
        Проверяет, что уведомления отмечаются как прочитанные после просмотра.

        Этот тест проверяет, что после посещения страницы уведомлений все уведомления текущего пользователя
        помечаются как прочитанные.
        """
        self.assertFalse(self.user_notification.is_read)
        self.client.get(reverse("notifications:notifications"))
        self.user_notification.refresh_from_db()
        self.assertTrue(self.user_notification.is_read)


class SignalTests(TestCase):
    """
    Тесты для проверки сигналов, создающих уведомления о подписках и изменениях данных пользователя.

    Этот класс содержит тесты для проверки корректности работы сигналов, которые создают уведомления
    при подписке на пользователя, изменении пароля или email. Также проверяется, что уведомления не создаются
    при начальной сохранении объекта пользователя.
    """

    def setUp(self):
        """
        Подготавливает тестовые данные для выполнения тестов.

        Создает двух пользователей и подписку между ними. Эти данные используются в тестах для проверки
        сигналов и создания уведомлений.
        """
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com", username="user1", password="password"
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@example.com", username="user2", password="password"
        )

        self.subscription = Subscription.objects.create(
            follower=self.user1, following=self.user2
        )

    def test_create_notification_on_follow(self):
        """
        Проверяет создание уведомления при подписке на пользователя.

        Этот тест проверяет, что при создании подписки между двумя пользователями создается уведомление
        для пользователя, на которого подписались. Проверяются тема и содержание уведомления, чтобы убедиться,
        что они соответствуют ожиданиям.
        """
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 1)
        notification = notifications.first()
        self.assertEqual(notification.topic, "Подписка")
        self.assertIn(self.user1.username, notification.message)
        self.assertIn(
            reverse("posts:home", kwargs={"pk": self.user1.pk}), notification.message
        )

    def test_user_change_notifications(self):
        """
        Проверяет создание уведомлений при изменении данных пользователя.

        Этот тест проверяет, что при изменении email и пароля пользователя создаются соответствующие уведомления.
        Также проверяется, что уведомления содержат правильные сообщения об изменении пароля и email.
        """
        self.user1.email = "new_email@example.com"
        self.user1.set_password("new_password")
        self.user1.save()

        notifications = Notification.objects.filter(user=self.user1)
        self.assertEqual(notifications.count(), 2)

        password_notification = notifications.get(topic="Изменение пароля")
        self.assertIsNotNone(password_notification)
        self.assertEqual(
            password_notification.message, "Ваш пароль был успешно изменен."
        )

        email_notification = notifications.get(topic="Изменение email")
        self.assertIsNotNone(email_notification)
        self.assertEqual(
            email_notification.message,
            f"Ваш email был успешно изменен на {self.user1.email}.",
        )

    def test_user_change_no_notifications_on_initial_save(self):
        """
        Проверяет отсутствие уведомлений при инициализации пользователя.

        Этот тест проверяет, что при инициализации объекта пользователя не создаются уведомления.
        """
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)
        self.user1.save()
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)

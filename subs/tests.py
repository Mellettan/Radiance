from django.test import TestCase
from django.urls import reverse

from accounts.models import Subscription, CustomUser


class SubsViewTest(TestCase):
    """
    Тесты для представления `SubsView`, отвечающего за отображение списка подписок
    и поиск пользователей.

    Этот класс проверяет функциональность различных аспектов представления подписок,
    включая отображение подписок, поиск пользователей, пагинацию и работу с анонимными пользователями.
    """

    def setUp(self):
        """
        Настраивает тестовые данные для выполнения тестов.

        Создает несколько пользователей и подписку между двумя из них.
        """
        self.user1 = CustomUser.objects.create_user(email='user1@example.com', password='password', username='user1')
        self.user2 = CustomUser.objects.create_user(email='user2@example.com', password='password', username='user2')
        self.user3 = CustomUser.objects.create_user(email='user3@example.com', password='password', username='user3')
        self.user4 = CustomUser.objects.create_user(email='user4@example.com', password='password', username='user4')
        self.user5 = CustomUser.objects.create_user(email='user5@example.com', password='password', username='user5')
        self.user6 = CustomUser.objects.create_user(email='user6@example.com', password='password', username='user6')

        self.subscription = Subscription.objects.create(follower=self.user1, following=self.user2)

    def test_display_subscriptions(self):
        """
        Проверяет отображение списка подписок текущего пользователя.

        Подтверждает, что подписки пользователя отображаются корректно
        и что пользователи, на которых нет подписки, не отображаются.
        """
        self.client.force_login(self.user1)
        url = reverse('subs:subs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)
        self.assertNotContains(response, self.user3.username)

    def test_search_users(self):
        """
        Проверяет функциональность поиска пользователей.

        Подтверждает, что пользователи, соответствующие запросу поиска, отображаются,
        а пользователи, не соответствующие запросу, не отображаются.
        """
        self.client.force_login(self.user1)
        url = reverse('subs:subs')
        response = self.client.get(url, {'q': self.user3.email})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user3.username)
        self.assertNotContains(response, self.user4.username)

    def test_pagination(self):
        """
        Проверяет работу пагинации для списка пользователей.

        Создает дополнительного пользователя и проверяет, что при запросе первой страницы
        пагинации отображаются только пользователи, подходящие под запрос.
        """
        self.client.force_login(self.user1)
        self.user7 = CustomUser.objects.create_user(email='user7@example.com', password='password', username='user7')

        url = reverse('subs:subs')
        response = self.client.get(url, {'q': 'user', 'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.user2.username)
        self.assertNotContains(response, self.user7.username)

    def test_no_subscriptions_for_anonymous_user(self):
        """
        Проверяет отсутствие подписок у анонимного пользователя.

        Подтверждает, что анонимные пользователи ни на кого не подписаны.
        """
        url = reverse('subs:subs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.user1.username)

    def test_search_without_query(self):
        """
        Проверяет поведение при поиске без запроса.

        Подтверждает, что отображается сообщение о том, что пользователи не найдены,
        если запрос поиска пуст.
        """
        self.client.force_login(self.user1)
        url = reverse('subs:subs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователи не найдены')  # н + а + и +  ̆ + д + е + н + ы

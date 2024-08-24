from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser, Subscription
from posts.models import Post


class HomeViewTest(TestCase):
    """
    Тесты для представления домашней страницы пользователя, включая создание постов, комментариев,
    лайков и подписок.

    Этот класс содержит тесты для проверки функциональности домашней страницы, такие как создание постов,
    комментариев, лайков и подписок. Он также проверяет, что при выполнении различных действий возвращаются
    ожидаемые результаты.
    """

    def setUp(self):
        """
        Подготавливает тестовые данные для выполнения тестов.

        Создает двух пользователей, пост и подписку между пользователями. Эти данные используются в тестах
        для проверки функциональности домашней страницы.
        """
        self.user1 = CustomUser.objects.create_user(email='user1@example.com', password='password', username='user1')
        self.user2 = CustomUser.objects.create_user(email='user2@example.com', password='password', username='user2')

        self.post = Post.objects.create(user=self.user1, content='Test post', created_at=timezone.now())

        self.subscription = Subscription.objects.create(follower=self.user1, following=self.user2)

    def test_get_home_page(self):
        """
        Проверяет успешное получение домашней страницы пользователя.

        Этот тест проверяет, что домашняя страница пользователя загружается успешно, используется правильный
        шаблон и передается необходимый контекст.
        """
        url = reverse('posts:home', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/home.html')
        self.assertIn('user_of_posts', response.context)
        self.assertIn('posts', response.context)
        self.assertIn('subscriptions', response.context)
        self.assertIn('user_of_posts_in_followers', response.context)

    def test_create_post(self):
        """
        Проверяет создание нового поста.

        Этот тест проверяет, что после отправки формы для создания нового поста, пост добавляется в базу данных
        и отображается на странице.
        """
        self.client.force_login(self.user1)
        url = reverse('posts:home', kwargs={'pk': self.user1.pk})
        data = {
            'new-post': '',
            'content': 'New test post'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 2)
        response_after_redirect = self.client.get(response['Location'])
        self.assertContains(response_after_redirect, 'New test post')

    def test_create_comment(self):
        """
        Проверяет создание нового комментария к посту.

        Этот тест проверяет, что после отправки формы для создания комментария, комментарий добавляется к посту
        и отображается на странице.
        """
        self.client.force_login(self.user2)
        url = reverse('posts:home', kwargs={'pk': self.user1.pk})
        data = {
            'new-comment': '',
            'post-pk': self.post.pk,
            'content': 'New test comment'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.comments.count(), 1)
        response_after_redirect = self.client.get(response['Location'])
        self.assertContains(response_after_redirect, 'New test comment')

    def test_like_unlike_post(self):
        """
        Проверяет добавление и удаление лайков к посту.

        Этот тест проверяет, что пользователь может поставить лайк и снять лайк с поста. Проверяется, что
        состояние лайка меняется при повторной отправке запроса.
        """
        self.client.force_login(self.user2)
        url = reverse('posts:home', kwargs={'pk': self.user1.pk})
        data = {
            'like-post': '',
            'post-pk': self.post.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user2 in self.post.liked_by.all())

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user2 in self.post.liked_by.all())

    def test_subscribe_unsubscribe_user(self):
        """
        Проверяет подписку и отписку от пользователя.

        Этот тест проверяет, что пользователь может подписаться на другого пользователя и отписаться от него.
        Проверяется изменение состояния подписки при повторной отправке запроса.
        """
        self.client.force_login(self.user2)
        url = reverse('posts:home', kwargs={'pk': self.user1.pk})
        data = {
            'subscribe': ''
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user2.is_following(self.user1))

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user2.is_following(self.user1))


class ScheduleBotPostsCommandTest(TestCase):
    """
    Тесты для команды планирования ежедневных постов для ботов.

    Этот класс содержит тесты для команды `schedule_daily_posts`, которая планирует создание постов
    для ботов в случайное время в течение дня. Тесты проверяют, что посты планируются правильно
    и что только боты получают задачи на создание постов.
    """

    def setUp(self):
        """
        Создаёт тестовые данные для проверки команды планирования постов.

        Создаются два бота и один обычный пользователь. Эти данные используются для проверки
        функциональности команды.
        """
        self.bot1 = CustomUser.objects.create_user(username='bot1', email='bot1@example.com', password='password', is_bot=True)
        self.bot2 = CustomUser.objects.create_user(username='bot2', email='bot2@example.com', password='password', is_bot=True)
        self.user = CustomUser.objects.create_user(username='user', email='user@example.com', password='password', is_bot=False)

    @patch('posts.tasks.create_bot_post.send_with_options')
    @patch('random.randint')
    def test_schedules_posts_for_bots(self, mock_randint: MagicMock, mock_send_with_options: MagicMock) -> None:
        """
        Проверяет, что команда правильно планирует создание постов для ботов.

        Этот тест проверяет, что для каждого бота создаются три задачи на создание постов в
        случайные моменты времени утром, днём и вечером. Используются фиктивные значения для
        проверки правильности планирования задач.

        Args:
            mock_randint (MagicMock): Мок для функции random.randint, возвращает фиксированные значения.
            mock_send_with_options (MagicMock): Мок для метода create_bot_post.send_with_options.
        """
        mock_randint.side_effect = [21600, 43200, 64800] * 2  # Соответствует 6:00, 12:00, 18:00

        # Выполнение команды
        call_command('schedule_daily_posts')

        # Проверяем, что create_bot_post.send_with_options был вызван 6 раз (по 3 на каждого бота)
        self.assertEqual(mock_send_with_options.call_count, 6)

        # Проверяем, что задачи планируются с правильной задержкой для бота 1
        mock_send_with_options.assert_any_call(args=(self.bot1.id,), delay=timedelta(seconds=21600))
        mock_send_with_options.assert_any_call(args=(self.bot1.id,), delay=timedelta(seconds=43200))
        mock_send_with_options.assert_any_call(args=(self.bot1.id,), delay=timedelta(seconds=64800))

        # Проверяем, что задачи планируются с правильной задержкой для бота 2
        mock_send_with_options.assert_any_call(args=(self.bot2.id,), delay=timedelta(seconds=21600))
        mock_send_with_options.assert_any_call(args=(self.bot2.id,), delay=timedelta(seconds=43200))
        mock_send_with_options.assert_any_call(args=(self.bot2.id,), delay=timedelta(seconds=64800))

    @patch('posts.tasks.create_bot_post.send_with_options')
    @patch('random.randint')
    def test_no_tasks_for_non_bots(self, mock_randint: MagicMock, mock_send_with_options: MagicMock) -> None:
        """
        Проверяет, что команда не планирует задачи на создание постов для обычных пользователей.

        Этот тест проверяет, что команда `schedule_daily_posts` не планирует задачи для обычных
        пользователей.

        Args:
            mock_randint (MagicMock): Мок для функции random.randint, возвращает фиксированные значения.
            mock_send_with_options (MagicMock): Мок для метода create_bot_post.send_with_options.
        """
        mock_randint.side_effect = [10000] * 6

        # Выполнение команды
        call_command('schedule_daily_posts')

        # Проверяем, что create_bot_post.send_with_options был вызван только для ботов
        self.assertEqual(mock_send_with_options.call_count, 6)
        mock_send_with_options.assert_any_call(args=(self.bot1.id,), delay=timedelta(seconds=10000))
        mock_send_with_options.assert_any_call(args=(self.bot2.id,), delay=timedelta(seconds=10000))
        # Убедимся, что обычный пользователь не задействован
        with self.assertRaises(AssertionError):
            mock_send_with_options.assert_any_call(args=(self.user.id,), delay=timedelta(seconds=10000))

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

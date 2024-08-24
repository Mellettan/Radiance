import os
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class UserInfoViewTest(TestCase):
    """
    Набор тестов для проверки представления UserInfoView.

    Эти тесты проверяют доступность страницы информации о пользователе, а также
    корректность обновления аватара пользователя.
    """

    def setUp(self):
        """
        Настройка тестового окружения.

        Создает пользователя и выполняет его аутентификацию перед
        выполнением каждого теста.
        """
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="password", username="testuser"
        )
        self.client.force_login(self.user)

    def test_get_user_info_page(self):
        """
        Проверяет успешное отображение страницы информации о пользователе.

        Запрашивает страницу userinfo и проверяет, что возвращаемый статус - 200,
        и что используется правильный шаблон.
        """
        url = reverse("userinfo:userinfo")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "userinfo/userinfo.html")

    def test_update_avatar(self):
        """
        Проверяет успешное обновление аватара пользователя.

        Отправляет POST-запрос с изображением для обновления аватара, затем проверяет,
        что аватар был успешно сохранен в базе данных.
        """
        url = reverse("userinfo:userinfo")
        with open("media/test_avatar.png", "rb") as img:
            avatar = SimpleUploadedFile(
                "test_image.png", img.read(), content_type="image/png"
            )

        response = self.client.post(url, {"avatar": avatar})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIn("test_image", self.user.avatar.name)

    def test_no_avatar_update(self):
        """
        Проверяет, что аватар пользователя не изменяется при отсутствии
        загрузки нового файла.

        Отправляет POST-запрос без файла аватара и проверяет, что аватар пользователя
        остается неизменным.
        """
        url = reverse("userinfo:userinfo")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIn("default_avatar", self.user.avatar.name)

    def test_unauthorized_access(self):
        """
        Проверяет, что неавторизованный пользователь может получить доступ к
        странице информации, однако отображается не вся информация.
        """
        self.client.logout()
        url = reverse("userinfo:userinfo")
        response = self.client.get(url)
        self.assertContains(response, "Login")
        self.assertNotContains(response, "Email")

    def tearDown(self):
        """
        Удаляет созданные медиафайлы после выполнения тестов.

        Удаляет директорию с файлами тестового пользователя, если она существует.
        """
        user_media_path = os.path.join("media", "users", self.user.email)
        if os.path.exists(user_media_path):
            shutil.rmtree(user_media_path)

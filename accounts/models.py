from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import FileExtensionValidator


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользовательской модели пользователя, где адрес электронной почты является
    уникальным идентификатором для аутентификации вместо имен пользователей.
    """
    def create_user(self, email: str, password: str = None, **extra_fields) -> 'CustomUser':
        """
        Создаёт и сохраняет пользователя с указанным адресом электронной почты и паролем.

        Args:
            email: адрес электронной почты
            password: пароль
            extra_fields: дополнительные параметры пользователя

        Returns:
            CustomUser: созданный пользователь
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user: 'CustomUser' = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields) -> 'CustomUser':
        """
        Создает и сохраняет суперпользователя с указанным адресом электронной почты и паролем.

        Args:
            email: адрес электронной почты
            password: пароль
            extra_fields: дополнительные параметры пользователя

        Returns:
            CustomUser: созданный суперпользователь
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


def user_avatar_path(instance: 'CustomUser', filename: str) -> str:
    """
    Генерирует путь к файлу аватара пользователя.

    Args:
        instance: пользователь
        filename: имя файла

    Returns:
        str: путь к файлу аватара пользователя
    """
    return 'users/{user_email}/avatars/{filename}'.format(user_email=instance.email, filename=filename)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Модель пользователя, наследуемая от AbstractBaseUser и PermissionsMixin.

    Attributes:
        email (EmailField): Адрес электронной почты пользователя (уникальный идентификатор для аутентификации).
        username (CharField): Имя пользователя.
        password (CharField): Пароль пользователя.
        is_staff (BooleanField): Указывает, является ли пользователь сотрудником.
        is_bot (BooleanField): Указывает, является ли пользователь ботом.
        bot_description (TextField): Описание личности бота.
        is_active (BooleanField): Определяет, активна ли учетная запись пользователя.
        avatar (ImageField): Изображение аватара пользователя с ограничениями на типы файлов.
        email_verified (BooleanField): Указывает, подтвержден ли адрес электронной почты пользователя.
        temp_email (EmailField): Временный адрес электронной почты для проверки электронной почты.
        date_joined (DateTimeField): Дата и время создания учетной записи пользователя.
        USERNAME_FIELD (str): Поле, которое будет использоваться в качестве уникального идентификатора для аутентификации (электронная почта).
        REQUIRED_FIELDS (list): Поля, которые будут запрашиваться (помимо USERNAME_FIELD) при создании пользователя через командную строку.
        objects (CustomUserManager): Менеджер, который занимается созданием экземпляров пользователей и управлением ими.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)

    is_staff = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    bot_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to=user_avatar_path,
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
                               default='default_avatar.png')

    email_verified = models.BooleanField(default=False)

    temp_email = models.EmailField(blank=True, null=True)  # Временный адрес для подтверждения почты

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        """
        Example:
            "user1@example.com"
        """
        return self.email

    def follow(self, user: 'CustomUser') -> None:
        """
        Подписывает пользователя на другого пользователя.

        Args:
            user: пользователь, на которого подписывается текущий пользователь
        """
        if user != self and not self.is_following(user):
            Subscription.objects.create(follower=self, following=user)

    def unfollow(self, user: 'CustomUser') -> None:
        """
        Отписывает пользователя от другого пользователя.

        Args:
            user: пользователь, от которого отписывается текущий пользователь
        """
        Subscription.objects.filter(follower=self, following=user).delete()

    def is_following(self, user: 'CustomUser') -> bool:
        """
        Определяет, подписан ли пользователь на другого пользователя.

        Args:
            user: пользователь, на которого проверяется подписка

        Returns:
            bool: True, если пользователь подписан на другого пользователя, иначе False
        """
        return Subscription.objects.filter(follower=self, following=user).exists()

    def get_following(self) -> models.QuerySet:
        """
        Возвращает список пользователей, на которых подписан текущий пользователь.

        Returns:
            models.QuerySet: список пользователей
        """
        return CustomUser.objects.filter(followers__follower=self)

    def get_followers(self) -> models.QuerySet:
        """
        Возвращает список пользователей, которые подписаны на текущего пользователя.

        Returns:
            models.QuerySet: список пользователей
        """
        return CustomUser.objects.filter(following__following=self)


class Subscription(models.Model):
    """
    Модель подписки. Представляет отношения подписки между двумя пользователями в системе, где один пользователь подписан на другого.

    Attributes:
        follower (ForeignKey): Пользователь, который подписывается.
        following (ForeignKey): Пользователь, на которого подписываются.
    """

    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        """
        Example:
            "user1@example.com follows user2@example.com"
        """
        return f"{self.follower.email} follows {self.following.email}"

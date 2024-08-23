from django.db import models
from accounts.models import CustomUser


class Post(models.Model):
    """
    Модель для хранения постов пользователей.

    Эта модель представляет собой пост, созданный пользователем. Он включает в себя содержание поста,
    информацию о пользователе, который создал пост, дату создания и список пользователей, которые отметили
    пост как понравившийся.

    Attributes:
        user (ForeignKey): Пользователь, который создал пост. Связано с моделью CustomUser.
        content (TextField): Содержимое поста.
        created_at (DateTimeField): Дата и время создания поста. Устанавливается автоматически при создании.
        liked_by (ManyToManyField): Список пользователей, которые отметили пост как понравившийся. Связано с моделью CustomUser.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True, default=None)

    def __str__(self):
        """
        Возвращает строковое представление объекта Post.

        Возвращает строку, содержащую идентификатор поста и первые 20 символов содержимого поста.

        Returns:
            str: Строка с идентификатором поста и кратким содержанием.
        """
        return f"Post #{self.pk}: {self.content[:20]}"


class Comment(models.Model):
    """
    Модель для хранения комментариев к постам.

    Эта модель представляет собой комментарий к посту, созданный пользователем. Он включает в себя содержание комментария,
    информацию о посте, к которому относится комментарий, пользователя, который создал комментарий, и дату создания.

    Attributes:
        post (ForeignKey): Пост, к которому относится комментарий. Связано с моделью Post.
        user (ForeignKey): Пользователь, который создал комментарий. Связано с моделью CustomUser.
        content (TextField): Содержимое комментария.
        created_at (DateTimeField): Дата и время создания комментария. Устанавливается автоматически при создании.
    """

    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Возвращает строковое представление объекта Comment.

        Возвращает строку, содержащую идентификатор комментария и первые 20 символов содержимого комментария.

        Returns:
            str: Строка с идентификатором комментария и кратким содержанием.
        """
        return f"Comment #{self.pk}: {self.content[:20]}"

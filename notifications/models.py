from django.db import models

from accounts.models import CustomUser


class Notification(models.Model):
    """
    Модель для хранения уведомлений пользователей.

    Эта модель описывает структуру уведомлений, которые могут быть отправлены пользователям.
    Уведомление содержит тему, сообщение, информацию о дате создания и статус прочтения.

    Attributes:
        user (ForeignKey): Пользователь, к которому относится уведомление. Связано с моделью CustomUser.
        topic (CharField): Тема уведомления. Максимальная длина - 255 символов.
        message (TextField): Содержимое уведомления.
        created_at (DateTimeField): Дата и время создания уведомления. Устанавливается автоматически при создании.
        is_read (BooleanField): Флаг, указывающий, прочитано уведомление или нет. По умолчанию - False.
    """

    user = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        """
        Возвращает строковое представление объекта Notification.

        Returns:
            str: Строка, содержащая адрес электронной почты пользователя и текст сообщения.
        """
        return f"Notification for {self.user.email}: {self.message}"

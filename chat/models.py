from django.db import models

from accounts.models import CustomUser


class Message(models.Model):
    """
    Модель, представляющая сообщение, передаваемое между пользователями.

    Эта модель хранит подробную информацию о сообщении, включая отправителя, получателя,
    содержание и временная метка создания сообщения.

    Attributes:
        sender (ForeignKey): Ссылка на CustomUser, отправившего сообщение.
            Связанное имя — «sent_messages».
        recipient (ForeignKey): Ссылка на CustomUser, получившего сообщение.
            Связанное имя — «received_messages».
        content (TextField): Содержание сообщения.
        timestamp (DateTimeField): Дата и время создания сообщения.
            Автоматически устанавливается текущая дата и время при сохранении сообщения.
    """

    sender = models.ForeignKey(
        CustomUser, related_name="sent_messages", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        CustomUser, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Возвращает содержимое сообщения в виде его строкового представления."""
        return self.content

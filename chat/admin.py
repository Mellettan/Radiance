from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Message.

    Attributes:
        list_display (list): Список полей, которые будут отображаться в
            административной панели.
        search_fields (list): Список полей, которые будут использоваться для
            поиска в административной панели.
        list_filter (list): Список полей, которые будут использоваться для
            фильтрации в административной панели.
        ordering (list): Список полей, которые будут использоваться для
            упорядочивания в административной панели.
        readonly_fields (list): Список полей, которые будут отображаться
            только для чтения в административной панели.
    """

    list_display = ("pk", "sender", "recipient", "content_preview", "timestamp")

    search_fields = ("sender__username", "recipient__username", "content")

    list_filter = ("sender", "recipient", "timestamp")

    ordering = ("-timestamp",)

    readonly_fields = ("timestamp",)

    def content_preview(self, obj: Message) -> str:
        """
        Возвращает предварительный просмотр содержимого сообщения.

        Отображает первые 50 символов содержимого сообщения, чтобы
        администратор мог быстро увидеть его начало в списке сообщений.

        Args:
            obj: Модель сообщения.

        Returns:
            str: Предварительный просмотр содержимого сообщения.
        """
        return obj.content[:50]

    content_preview.short_description = "Content Preview"

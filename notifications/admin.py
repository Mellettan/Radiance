from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Класс конфигурации интерфейса админки для модели Notification.

    Определяет, как объекты модели Notification будут отображаться и
    управляться в админ-панели Django.

    Attributes:
        list_display (tuple): Поля модели Notification, которые будут отображаться
            в списке объектов.
        list_filter (tuple): Поля, по которым можно фильтровать объекты в админ-панели.
        search_fields (tuple): Поля, по которым можно выполнять поиск в админ-панели.
        ordering (tuple): Порядок сортировки объектов в списке (по умолчанию по дате
            создания в обратном порядке).
        readonly_fields (tuple): Поля, которые будут доступны только для чтения в
            форме редактирования объекта.
    """

    list_display = ("user", "topic", "message", "created_at", "is_read")
    list_filter = ("is_read", "created_at", "user")
    search_fields = ("user__email", "topic", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

from django import template
from django.db.models import QuerySet

register = template.Library()


@register.filter
def unread_notifications_count(notifications: QuerySet) -> int:
    """
    Возвращает количество непрочитанных уведомлений.

    Этот фильтр принимает QuerySet объектов уведомлений и подсчитывает количество
    уведомлений, у которых поле `is_read` установлено в `False`.

    Args:
        notifications (QuerySet): QuerySet объектов уведомлений, которые нужно
            отфильтровать.

    Returns:
        int: Количество непрочитанных уведомлений.

    Example:
        Кол-во сообщений: {{ request.user.notifications|unread_notifications_count }}.
    """
    return notifications.filter(is_read=False).count()

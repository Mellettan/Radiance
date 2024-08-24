from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from accounts.models import CustomUser, Subscription

from .models import Notification


@receiver(post_save, sender=Subscription)
def create_notification_on_follow(
    sender: Subscription, instance: Subscription, created: bool, **kwargs
) -> None:
    """
    Создает уведомление, когда пользователь подписывается на другого.

    Этот сигнал срабатывает после сохранения объекта Subscription.
    Если подписка была создана, создается уведомление для пользователя,
    на которого подписались.

    Args:
        sender (Model): Модель, отправляющая сигнал (Subscription).
        instance (Subscription): Экземпляр модели Subscription, который был сохранен.
        created (bool): Флаг, указывающий, было ли создание новой записи (True)
            или обновление существующей (False).
        **kwargs: Дополнительные параметры.
    """
    if created:
        follower = instance.follower
        following = instance.following
        Notification.objects.create(
            user=following,
            topic="Подписка",
            message=(
                f'<a href="{reverse("posts:home", kwargs={"pk": follower.pk})}"'
                f">{follower.username}</a> подписался на вас."
            ),
        )


@receiver(pre_save, sender=CustomUser)
def check_user_changes(sender: CustomUser, instance: CustomUser, **kwargs):
    """
    Проверяет изменения в модели пользователя перед сохранением.

    Этот сигнал срабатывает перед сохранением объекта модели CustomUser. Он проверяет,
    были ли изменены пароль или email пользователя, и добавляет соответствующие
    флаги к экземпляру пользователя.

    Args:
        sender (Model): Модель, отправляющая сигнал (CustomUser).
        instance (CustomUser): Экземпляр модели CustomUser, который будет сохранен.
        **kwargs: Дополнительные параметры.
    """
    try:
        old_instance = CustomUser.objects.get(pk=instance.pk)
    except CustomUser.DoesNotExist:
        return

    if instance.password != old_instance.password:
        instance._password_changed = True

    if instance.email != old_instance.email:
        instance._email_changed = True


@receiver(post_save, sender=CustomUser)
def create_notification(sender, instance, **kwargs):
    """
    Создает уведомления после изменения пароля или email пользователя.

    Этот сигнал срабатывает после сохранения объекта модели CustomUser.
    Если были изменены пароль или email пользователя, создаются соответствующие
    уведомления.

    Args:
        sender (Model): Модель, отправляющая сигнал (CustomUser).
        instance (CustomUser): Экземпляр модели CustomUser, который был сохранен.
        **kwargs: Дополнительные параметры.
    """
    if hasattr(instance, "_password_changed") and instance._password_changed:
        Notification.objects.create(
            user=instance,
            topic="Изменение пароля",
            message="Ваш пароль был успешно изменен.",
        )

    if hasattr(instance, "_email_changed") and instance._email_changed:
        Notification.objects.create(
            user=instance,
            topic="Изменение email",
            message=f"Ваш email был успешно изменен на {instance.email}.",
        )

import dramatiq
from django.conf import settings
from django.core.mail import send_mail


@dramatiq.actor
def send_confirmation_email(
    subject: str, message: str, recipient_list: list[str]
) -> None:
    """
    Асинхронно отправляет электронное письмо с подтверждением списку получателей.

    Args:
        subject (str): Тема письма.
        message (str): Тело письма.
        recipient_list (list[str]): Список адресов электронной почты получателей.

    Эта функция использует Dramatiq для асинхронной обработки процесса отправки электронной почты.
    Это означает, что электронное письмо будет отправлено в фоновом режиме, не блокируя основной поток приложения.

    Example:
        send_confirmation_email.send("Account Confirmation",
        "Please confirm your account by clicking the link.", ["user@example.com"])

    Note:
        - Аргумент `fail_silly=False` гарантирует, что любые исключения во время процесса отправки
          электронной почты будут вызваны, что облегчит отладку проблем.
        - `settings.DEFAULT_FROM_EMAIL` используется в качестве адреса электронной почты отправителя.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

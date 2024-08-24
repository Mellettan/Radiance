from django.core.management.base import BaseCommand
from crontab import CronTab


class Command(BaseCommand):
    """
    Удаляет CRON задачу для планирования ежедневных постов.

    Этот класс представляет команду управления Django, которая удаляет
    CRON задачу для планирования ежедневных постов, если таковая существует.
    Команда ищет задачи по комментарию и удаляет их.

    Attributes:
        help (str): Описание команды для вывода в справке.
    """

    help = 'Removes the CRON job for scheduling daily posts'

    def handle(self, *args, **kwargs) -> None:
        """
        Выполняет команду удаления CRON задачи.

        Этот метод подключается к CRON-таблице текущего пользователя, ищет
        задачи с комментарием 'Django Bot Posts' и удаляет их. После этого
        сохраняет изменения в CRON-таблице.

        Args:
            *args: Позиционные аргументы команды.
            **kwargs: Именованные аргументы команды.
        """
        user_cron = CronTab(user=True)

        # Ищем задачу по комментарию
        user_cron.remove_all(comment='Django Bot Posts')

        # Сохраняем изменения
        user_cron.write()

        self.stdout.write(self.style.SUCCESS('Successfully removed CRON job for scheduling daily posts'))
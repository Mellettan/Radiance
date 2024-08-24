from django.core.management.base import BaseCommand
from crontab import CronTab
import os
from pathlib import Path


class Command(BaseCommand):
    """
    Добавляет CRON задачу для планирования ежедневных постов ботами.

    Этот класс представляет команду управления Django, которая добавляет
    CRON задачу для выполнения команды Django по расписанию. Команда
    запускает задачу `schedule_daily_posts` каждый день в полночь.

    Attributes:
        help (str): Описание команды для вывода в справке.
    """

    help = 'Adds a CRON job to schedule daily posts for bots'

    def handle(self, *args, **kwargs) -> None:
        """
        Выполняет команду добавления CRON задачи.

        Этот метод подключается к CRON-таблице текущего пользователя, создает
        новую задачу, которая будет запускать команду Django `schedule_daily_posts`
        каждый день в полночь. Путь к `manage.py` определяется автоматически.

        Args:
            *args: Позиционные аргументы команды.
            **kwargs: Именованные аргументы команды.
        """
        user_cron = CronTab(user=True)

        # Определяем путь к manage.py
        project_dir = Path(__file__).resolve().parent.parent.parent.parent
        manage_py = os.path.join(project_dir, 'manage.py')

        # Создаем новую CRON задачу
        job = user_cron.new(command=f'python3 {manage_py} schedule_daily_posts', comment='Django Bot Posts')

        # Устанавливаем расписание: ежедневно в полночь
        job.setall('0 0 * * *')

        # Сохраняем изменения в CRON-таблице
        user_cron.write()

        self.stdout.write(self.style.SUCCESS('Successfully added CRON job to schedule daily posts'))

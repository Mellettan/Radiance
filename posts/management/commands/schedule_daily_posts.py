import random
from datetime import timedelta

from django.core.management import BaseCommand

from accounts.models import CustomUser
from posts.tasks import create_bot_post


class Command(BaseCommand):
    """
    Планирует создание ежедневных постов для ботов в случайные интервалы времени утром, днём и вечером.

    Этот класс используется для планирования трёх постов в день для каждого бота в системе.
    Посты планируются на случайные моменты времени в пределах утреннего, дневного и вечернего интервалов.
    Для создания постов используется задача Dramatiq.

    Attributes:
        help (str): Описание команды для помощи.
    """

    help = "Schedules daily posts. Call this daily at midnight (with cron or smth similar)."

    def handle(self, *args, **options) -> None:
        """
        Основной метод, который выполняет логику планирования постов для ботов.

        Метод извлекает всех пользователей с флагом `is_bot=True`, затем для каждого бота планирует три
        поста на случайное время утром, днём и вечером. Время задержки до выполнения задачи вычисляется
        случайным образом для каждого периода суток.

        Args:
            *args: Аргументы командной строки, которые могут быть переданы команде.
            **options: Дополнительные опции командной строки.
        """
        bots = CustomUser.objects.filter(is_bot=True)
        for bot in bots:
            seconds_since_midnight_morning = random.randint(6 * 3600, 12 * 3600)
            seconds_since_midnight_afternoon = random.randint(12 * 3600, 18 * 3600)
            seconds_since_midnight_evening = random.randint(18 * 3600, 24 * 3600)

            create_bot_post.send_with_options(args=(bot.id,), delay=timedelta(seconds=seconds_since_midnight_morning))
            create_bot_post.send_with_options(args=(bot.id,), delay=timedelta(seconds=seconds_since_midnight_afternoon))
            create_bot_post.send_with_options(args=(bot.id,), delay=timedelta(seconds=seconds_since_midnight_evening))

            self.stdout.write(
                self.style.NOTICE(f'Created bot "{bot.username}" posts: {seconds_since_midnight_morning}, '
                                  f'{seconds_since_midnight_afternoon}, {seconds_since_midnight_evening}'))

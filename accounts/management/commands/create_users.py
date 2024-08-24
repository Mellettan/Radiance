import time

from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from accounts.models import CustomUser


class Command(BaseCommand):
    """
    Команда управления Django, создающая указанное количество пользователей.
    """

    help = "Creates a specified number of users."

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Добавляет аргумент «число» к команде.

        Args:
            parser: Синтаксический анализатор аргументов
        """
        parser.add_argument("number", type=int, help="The number of users to create")

    def handle(self, *args, **kwargs) -> None:
        """
        Создает указанное количество пользователей.
        """
        number = kwargs["number"]
        timestamp = time.strftime("%Y%m%d%H%M%S")
        for i in range(number):
            username = f"user{i}_{timestamp}"
            email = f"user{i}_{timestamp}@example.com"
            password = "password"
            CustomUser.objects.create_user(
                username=username, email=email, password=password
            )

import secrets
import string

from django.core.management import BaseCommand

from accounts.models import CustomUser


def generate_password(length: int = 12) -> str:
    """
    Генерирует пароль с заданным количеством символов.

    Args:
        length (int): Количество символов в пароле.

    Returns:
        str: Сгенерированный пароль.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    """
    Команда управления Django, создающая ботов.

    Список ботов:
        - Ава АйТек
        - Итан Спортсмен
        - Луна Музыкант
    """

    help = "Creates bots"

    def handle(self, *args, **kwargs) -> None:
        """
        Создает ботов. Все боты имеют случайно сгенерированный пароль
        (аутентификация через веб-сайт не подразумевается).
        """
        if CustomUser.objects.filter(is_bot=True).count() == 3:
            self.stdout.write(self.style.SUCCESS("3 Bots already created"))
            return
        username = "Ава АйТек"
        email = "ava_ai_tech@bot.com"
        password = generate_password()
        is_bot = True
        bot_description = (
            "Тебя зовут Ава. Ты девушка. Ты любишь современные технологии и "
            "искусственный интеллект."
        )
        avatar = "users/ava_ai_tech@bot.com/avatars/ava_bot.jpg"
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar,
        )

        self.stdout.write(self.style.SUCCESS(f"Bots created: {email}"))

        username = "Итан Спортсмен"
        email = "ethan_health@bot.com"
        password = generate_password()
        is_bot = True
        bot_description = (
            "Тебя зовут Итан. Ты парень. Ты приверженец здорового образа "
            "жизни и фитнес-тренер."
        )
        avatar = "users/ethan_health@bot.com/avatars/ethan_bot.png"
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar,
        )

        self.stdout.write(self.style.SUCCESS(f"Bots created: {email}"))

        username = "Луна Музыкант"
        email = "luna_melody@bot.com"
        password = generate_password()
        is_bot = True
        bot_description = """
        Тебя зовут Луна. Ты девушка. Ты музыкант и меломан.
        """
        avatar = "users/luna_melody@bot.com/avatars/luna_bot.png"
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar,
        )

        self.stdout.write(self.style.SUCCESS(f"Bots created: {email}"))

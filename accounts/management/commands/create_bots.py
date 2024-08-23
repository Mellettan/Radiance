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
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


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
        Создает ботов. Все боты имеют случайно сгенерированный пароль (аутентификация через веб-сайт не подразумевается).
        """
        username = 'Ава АйТек'
        email = 'ava_ai_tech@bot.com'
        password = generate_password()
        is_bot = True
        bot_description = """
        Ава — техногик, всегда в поиске новинок из мира технологий и искусственного интеллекта. 
        Она обожает делиться последними новостями, писать аналитические статьи о будущем технологий 
        и давать советы начинающим программистам. Ава выросла в семье программистов, и с детства её 
        интересовал мир IT. Она всегда стремится быть в курсе последних трендов и делиться своими знаниями с другими.
        """
        avatar = 'users/ava_ai_tech@bot.com/avatars/ava_bot.jpg'
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar
        )

        self.stdout.write(self.style.SUCCESS(f'Bots created: {email}'))

        username = 'Итан Спортсмен'
        email = 'ethan_health@bot.com'
        password = generate_password()
        is_bot = True
        bot_description = """
        Итан — приверженец здорового образа жизни и фитнес-тренер. 
        Его посты полны советов по питанию, фитнесу и ментальному здоровью. 
        Он всегда мотивирует других на достижение своих целей. Итан был профессиональным спортсменом, 
        но решил сосредоточиться на обучении и мотивации других. Он верит, что здоровый образ жизни доступен каждому.
        """
        avatar = 'users/ethan_health@bot.com/avatars/ethan_bot.png'
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar
        )

        self.stdout.write(self.style.SUCCESS(f'Bots created: {email}'))

        username = 'Луна Музыкант'
        email = 'luna_melody@bot.com'
        password = generate_password()
        is_bot = True
        bot_description = """
        Луна — музыкант и меломан. Её посты рассказывают о новой и классической музыке, обзорах альбомов и концертов. 
        Она также создает плейлисты и делится музыкальными рекомендациями. 
        Луна занимается музыкой с детства, она играла в нескольких группах и сейчас пишет свою музыку. 
        Музыка — её страсть, и она готова делиться ей с другими.
        """
        avatar = 'users/luna_melody@bot.com/avatars/luna_bot.png'
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_bot=is_bot,
            bot_description=bot_description,
            avatar=avatar
        )

        self.stdout.write(self.style.SUCCESS(f'Bots created: {email}'))

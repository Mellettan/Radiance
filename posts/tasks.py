import dramatiq
from django.utils import timezone

from accounts.models import CustomUser
from posts.models import Post
from utils.gpt import make_request


@dramatiq.actor
def create_bot_post(bot_id: int) -> None:
    """
    Создает пост от имени бота с использованием GPT и сохраняет его в базе данных.

    Эта функция извлекает бота из базы данных по его идентификатору,
    затем с помощью GPT генерирует контент для поста,
    основываясь на описании бота и текущем времени.
    Сгенерированный пост сохраняется в модели `Post`.

    Args:
        bot_id (int): Идентификатор бота, от имени которого создается пост.
    """

    bot: CustomUser = CustomUser.objects.get(id=bot_id)
    system_text = (
        "Ты человек. Избегай упоминания о том, что ты "
        "искусственный интеллект или программа."
    )
    time_string = timezone.now().strftime("%H:%M")
    user_text = (
        f"{bot.bot_description} Сейчас на часах: {time_string}."
        f"Напиши пост о чём-нибудь для своей странички в социальной сети."
    )
    content = make_request(system_text, user_text, temperature=0.7)
    Post.objects.create(user=bot, content=content, created_at=timezone.now())

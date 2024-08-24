import asyncio
import json

import loguru
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import CustomUser
from utils.gpt import make_request

from .models import Message

logger = loguru.logger


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer для WebSocket, который обрабатывает сообщения чата между пользователями.

    Этот потребитель управляет жизненным циклом соединения (подключение, отключение) и
    обрабатывает входящие сообщения, передавая их группе помещений. Также
    сохраняет сообщения в базу данных.

    Attributes:
        user_id (int): Идентификатор пользователя, с которым общается текущий пользователь.
        current_user (int): Идентификатор пользователя, подключенного в данный момент к WebSocket.
        room_name (str): Название чата, основанное на идентификаторах пользователей.
        room_group_name (str): Имя группы помещений для рассылки сообщений.
    """

    async def connect(self):
        """Обрабатывает настройку соединения WebSocket и присоединяется к `группе`."""
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.current_user = self.scope["user"].id

        logger.debug(
            f"Connecting... Current user_id: {self.current_user}, other user_id: {self.user_id}"
        )
        self.room_name = f"{min(self.current_user, self.user_id)}_{max(self.current_user, self.user_id)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """Обрабатывает отключение WebSocket и удаляет пользователя из `группы`."""
        logger.debug(
            f"Disconnecting chat consumer with room_group_name: {self.room_group_name}"
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """
        Обрабатывает входящие сообщения WebSocket, сохраняет их в базу данных,
        и передает сообщение `группе`.
        Грубо говоря: обработчик.

        Args:
            text_data (str): строка в формате JSON, содержащая данные сообщения.
                JSON должен включать в себя `message`, `receiver_id`, `sender_id` и `time`.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        receiver_id = text_data_json.get("receiver_id")
        sender_id = text_data_json.get("sender_id")
        time = text_data_json.get("time")

        # Сохраняем сообщение в базе данных
        await database_sync_to_async(self.save_message)(message, receiver_id, sender_id)

        # Немедленная отправка сообщения всем участникам группы
        logger.debug("receive_group_send_user")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "receiver_id": receiver_id,
                "sender_id": sender_id,
                "time": time,
            },
        )

        # Параллельное выполнение задачи получения ответа от GPT
        asyncio.create_task(
            self.process_bot_response(message, receiver_id, sender_id, time)
        )

    async def process_bot_response(
        self, message: str, receiver_id: str, sender_id: str, time: str
    ) -> None:
        """
        Обрабатывает ответ бота на входящее сообщение и отправляет его всем участникам группы.

        Этот метод проверяет, является ли получатель сообщения ботом, и если это так, он использует GPT для генерации ответа.
        Затем ответ сохраняется в базе данных и отправляется обратно участникам чата.

        Args:
            message (str): Сообщение, отправленное пользователем.
            receiver_id (str): Идентификатор получателя сообщения.
            sender_id (str): Идентификатор отправителя сообщения.
            time (str): Время отправки сообщения.
        """
        receiver_user: CustomUser = await database_sync_to_async(
            self.get_custom_user_by_id
        )(receiver_id)

        if receiver_user.is_bot:
            logger.debug("starting GPT request")
            # Обработка сообщения с использованием GPT
            gpt_response = await asyncio.get_event_loop().run_in_executor(
                None,
                make_request,
                "Ты человек. Избегай упоминания о том, что ты искусственный интеллект или программа.",  # system_text
                f"{receiver_user.bot_description} Я пишу тебе сообщение, ответь на него (можешь не здороваться): {message}",
                False,  # stream
                0.3,  # temperature
                100,  # max_tokens
            )

            # Сохраняем ответ GPT в базу данных
            await database_sync_to_async(self.save_message)(
                gpt_response, sender_id, receiver_id
            )

            # Отправка ответа GPT всем участникам группы
            logger.debug("receive_group_send_bot")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": gpt_response,
                    "receiver_id": sender_id,
                    "sender_id": receiver_id,
                    "time": time,
                },
            )

    async def chat_message(self, event):
        """
        Отправляет полученное сообщение (от одного участника) всем участникам `группы`.
        Грубо говоря: отображатель.

        Args:
            event (dict): Данные о событии, содержащие `message`, `receiver_id`, `sender_id` и `time`.
        """
        logger.debug(f"Send a message to all chat participants: {event}")
        message = event["message"]
        receiver_id = event["receiver_id"]
        sender_id = event["sender_id"]
        time = event["time"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "receiver_id": receiver_id,
                    "sender_id": sender_id,
                    "time": time,
                }
            )
        )

    def save_message(self, message, receiver_id, sender_id):
        """
        Сохраняет сообщение чата в базе данных.

        Args:
            message (str): Содержание сообщения.
            receiver_id (int): Идентификатор получателя сообщения.
            sender_id (int): Идентификатор отправителя сообщения.
        """
        Message.objects.create(
            sender=CustomUser.objects.get(id=sender_id),
            recipient=CustomUser.objects.get(id=receiver_id),
            content=message,
        )

    def get_custom_user_by_id(self, user_id) -> CustomUser:
        """
        Получает объект CustomUser по его идентификатору.
        """
        return CustomUser.objects.get(id=user_id)

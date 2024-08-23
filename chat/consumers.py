import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import loguru

from accounts.models import CustomUser
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
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.current_user = self.scope['user'].id

        logger.debug(f"Connecting... Current user_id: {self.current_user}, other user_id: {self.user_id}")
        self.room_name = f'{min(self.current_user, self.user_id)}_{max(self.current_user, self.user_id)}'
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Обрабатывает отключение WebSocket и удаляет пользователя из `группы`."""
        logger.debug(f"Disconnecting chat consumer with room_group_name: {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Обрабатывает входящие сообщения WebSocket, сохраняет их в базу данных,
        и передает сообщение `группе`.

        Args:
            text_data (str): строка в формате JSON, содержащая данные сообщения.
                JSON должен включать в себя `message`, `receiver_id`, `sender_id` и `time`.
        """
        logger.debug(f"Received text data: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver_id = text_data_json.get('receiver_id')
        sender_id = text_data_json.get('sender_id')
        time = text_data_json.get('time')

        await database_sync_to_async(self.save_message)(message, receiver_id, sender_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'receiver_id': receiver_id,
                'sender_id': sender_id,
                'time': time
            }
        )

    async def chat_message(self, event):
        """
        Отправляет полученное сообщение (от одного участника) всем участникам `группы`.

        Args:
            event (dict): Данные о событии, содержащие `message`, `receiver_id`, `sender_id` и `time`.
        """
        logger.debug(f"Send a message to all chat participants: {event}")
        message = event['message']
        receiver_id = event['receiver_id']
        sender_id = event['sender_id']
        time = event['time']

        await self.send(text_data=json.dumps({
            'message': message,
            'receiver_id': receiver_id,
            'sender_id': sender_id,
            'time': time
        }))

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
            content=message
        )

from aiogram import Bot

from config import settings


class TelegramNotification:
    @staticmethod
    async def new_request(phone: str, name: str):
        await Bot(token=settings.tg_bot_token).send_message(
            chat_id=settings.tg_request_chat_id,
            text=settings.tg_new_request_message.format(phone=phone, name=name),
            parse_mode='html',
        )

    @staticmethod
    async def new_purchase(fullname: str, username: str):
        await Bot(token=settings.tg_bot_token).send_message(
            chat_id=settings.tg_request_chat_id,
            text=settings.tg_new_purchase_message.format(fullname=fullname, username=username)
        )

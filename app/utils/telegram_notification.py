from aiogram import Bot

from config import settings


class TelegramNotification:
    __bot = Bot(token=settings.tg_bot_token)

    async def new_request(self, phone: str):
        await self.__bot.send_message(
            chat_id=settings.tg_request_chat_id,
            text=settings.tg_new_request_message.format(phone=phone)
        )

    async def new_purchase(self, fullname: str, username: str):
        await self.__bot.send_message(
            chat_id=settings.tg_request_chat_id,
            text=settings.tg_new_purchase_message.format(fullname=fullname, username=username)
        )

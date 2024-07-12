import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from handlers import survey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\nЯ - бот, который поможет тебе создать вакансию и опубликовать ее.", reply_markup= ReplyKeyboardRemove())
    await message.answer("\nВведи /survey, если хочешь начать заполнение.")



async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(survey.router)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
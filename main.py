import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

from handlers import survey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

# Создаем экземпляр Router для обработки команд и сообщений
router = Router()

# Получаем токен бота из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

# Инициализируем диспетчер с памятью для хранения состояний
dp = Dispatcher(storage=MemoryStorage())


# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    # Проверяем, является ли чат группой или каналом (ID < 0)
    if message.chat.id < 0:
        pass  # Игнорируем группы и каналы
    else:
        # Отправляем приветственное сообщение пользователю
        await message.answer(
            f"Привет, {html.bold(message.from_user.full_name)}!\nЯ — бот, который поможет тебе создать вакансию и опубликовать ее.",
            reply_markup=ReplyKeyboardRemove())
        await message.answer("\nВведи /survey, если хочешь начать заполнение.")


# Основная асинхронная функция для запуска бота
async def main() -> None:
    # Инициализируем экземпляр бота с токеном и настройками по умолчанию
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Подключаем маршрутизатор с обработчиками
    dp.include_router(survey.router)

    # Запускаем опрос событий (polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Настройка логирования: выводим логи в файл main_logs.txt и на консоль
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs.txt"),
            logging.StreamHandler()  # Чтобы логи также выводились в консоль
        ]
    )

    logging.info("Приложение запущено")

    # Запускаем основную асинхронную функцию
    asyncio.run(main())
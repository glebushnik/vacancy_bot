import asyncio
import logging
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

from keyboards.inline_row import make_inline_keyboard

# Загружаем переменные окружения из .env файла
load_dotenv()

from handlers import survey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from utils import logging_config

# Создаем экземпляр Router для обработки команд и сообщений
router = Router()

# Получаем токен бота из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

# Инициализируем диспетчер с памятью для хранения состояний
dp = Dispatcher(storage=MemoryStorage())

# Функция для проверки подключения к базе данных
def check_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")  # Пытаемся выполнить запрос для проверки соединения
        db = cursor.fetchone()
        if db:
            logging.info(f"Успешное подключение к базе данных: {db[0]}")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Ошибка доступа: неверное имя пользователя или пароль.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("Ошибка: база данных не существует.")
        else:
            logging.error(f"Ошибка при подключении к базе данных: {err}")

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    # Проверяем, является ли чат группой или каналом (ID < 0)
    if message.chat.id < 0:
        pass  # Игнорируем группы и каналы
    else:
        await message.answer(
            f"👋 Привет! Я помогу вам разместить вакансию.",
            reply_markup=ReplyKeyboardRemove()
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🆘 Поддержка", callback_data="contact_support"),
                InlineKeyboardButton(text="📜 Правила", callback_data="publication_rules")
            ],
            [
                InlineKeyboardButton(text="📝 Разместить вакансию", callback_data="post_vacancy"),
            ]
        ])

        await message.answer(
            text="Автоматически оформлю текст, подберу теги и проверю данные. Поехали!",
            reply_markup=keyboard
        )

# Основная асинхронная функция для запуска бота
async def main() -> None:
    # Проверка подключения к базе данных
    check_db_connection()

    # Инициализируем экземпляр бота с токеном и настройками по умолчанию
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Подключаем маршрутизатор с обработчиками
    dp.include_router(survey.router)

    # Запускаем опрос событий (polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging_config.setup_logging()

    logger = logging.getLogger(__name__)

    logging.info("Приложение запущено")

    # Запускаем основную асинхронную функцию
    asyncio.run(main())

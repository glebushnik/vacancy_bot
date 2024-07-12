from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_inline_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items:
        builder.row(InlineKeyboardButton(
            text=item, callback_data=item
        ))

    return builder.as_markup()

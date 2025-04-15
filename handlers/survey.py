import os
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
from db_utils.db_handler import check_and_save_job, mark_job_as_posted, check_data_length, is_job_posted
from utils.logging_config import setup_logging
from utils.variants import available_categories, available_grades, available_locations, available_subject_areas, \
    variants, data_dict, common_tags, rules, vacancy_form, help_msg, available_job_formats
from keyboards.inline_row import make_inline_keyboard
from utils.logic import routing, repeat_sending
import requests
from aiogram.types import KeyboardButton

setup_logging()
logger = logging.getLogger(__name__)

router = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")


class VacancySurvey(StatesGroup):
    waiting_inline_choice = State()
    additional = State()
    update_edited_field = State()
    edit_field = State()
    edit_vacancy = State()
    send_vacancy = State()
    finish = State()
    tags = State()
    contacts = State()
    bonus = State()
    wishes = State()
    tasks = State()
    requirements = State()
    responsibilities = State()
    salary = State()
    project_theme = State()
    choosing_subject_area = State()
    job_format = State()
    subject_area = State()
    timezone = State()
    location = State()
    grade = State()
    company_url = State()
    company_name = State()
    vacancy_name = State()
    choosing_category = State()


state_order = {
    0: VacancySurvey.vacancy_name,
    1: VacancySurvey.choosing_category,
    2: VacancySurvey.company_name,
    3: VacancySurvey.grade,
    4: VacancySurvey.location,
    5: VacancySurvey.timezone,
    6: VacancySurvey.job_format,
    7: VacancySurvey.subject_area,
    8: VacancySurvey.choosing_subject_area,
    9: VacancySurvey.project_theme,
    10: VacancySurvey.salary,
    11: VacancySurvey.requirements,
    12: VacancySurvey.tasks,
    13: VacancySurvey.wishes,
    14: VacancySurvey.bonus,
    15: VacancySurvey.additional,
    16: VacancySurvey.contacts,
    17: VacancySurvey.finish,
    18: VacancySurvey.edit_vacancy,
    19: VacancySurvey.edit_field,
    20: VacancySurvey.update_edited_field
}


async def go_back(state: FSMContext):
    current_state = await state.get_state()
    for index, s in state_order.items():
        if current_state == s:
            if index > 0:
                previous_state = state_order[index - 1]
                return previous_state.state.replace(":", ".")
    return None


async def send_prompt_for_state(state: FSMContext, message: Message, correct_input=True):
    current_state = await state.get_state()
    print(current_state)

    class FakeCallback:
        def __init__(self):
            self.message = message
            self.data = "fake_callback_data"

    if current_state == "VacancySurvey.vacancy_name":
        fake_callback = FakeCallback()
        await vacancy_name(fake_callback, state)
    elif current_state == "VacancySurvey.edit_vacancy":
        await finish_state(message, state)
    elif current_state == "VacancySurvey.choosing_category":
        await state.set_state(VacancySurvey.vacancy_name)
    elif current_state == "VacancySurvey.company_name":
        await vacancy_choose_category(message, state)
    elif current_state == "VacancySurvey.grade":
        await vacancy_company_name(message, state)
    elif current_state == "VacancySurvey.location":
        await state.set_state(VacancySurvey.grade)
        await vacancy_grade(message, state)
    elif current_state == "VacancySurvey.timezone":
        await vacancy_location(message, state)
    elif current_state == "VacancySurvey.job_format":
        await vacancy_timezone(message, state)
    elif current_state == "VacancySurvey.subject_area":
        await vacancy_job_format(message, state)
    elif current_state == "VacancySurvey.choosing_subject_area":
        await vacancy_timezone(message, state)
    elif current_state == "VacancySurvey.project_theme":
        global selected_subjects
        selected_subjects = []
        fake_callback = FakeCallback()
        await vacancy_subject_area(fake_callback, state)
    elif current_state == "VacancySurvey.salary":
        await vacancy_project_theme(message, state)
    elif current_state == "VacancySurvey.requirements":
        await vacancy_salary(message, state)
    elif current_state == "VacancySurvey.tasks":
        await vacancy_tasks(message, state)
    elif current_state == "VacancySurvey.wishes":
        await vacancy_requirements(message, state)
    elif current_state == "VacancySurvey.additional":
        await vacancy_wishes(message, state)
    elif current_state == "VacancySurvey.bonus":
        await vacancy_bonus(message, state)
    elif current_state == "VacancySurvey.contacts":
        if correct_input:
            await vacancy_additional(message, state)
        else:
            await vacancy_contacts(message, state)
    elif current_state == "VacancySurvey.finish":
        await vacancy_contacts(message, state)


@router.message(Command("back"))
async def back_command(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            current_state = await state.get_state()
            print(current_state)
            previous_state = await go_back(state)
            print(previous_state)
            if previous_state:
                await state.set_state(previous_state)
                await message.answer(f"Возвращаюсь к предыдущему шагу.")
                await send_prompt_for_state(state, message)
            else:
                await message.answer("Вы находитесь в начале опроса.")
                await vacancy_name(message, state)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(F.data == "publication_rules")
async def send_publication_rules_msg(call: CallbackQuery, state: FSMContext) -> None:
    if call.message.chat.id > 0:  # Только в личных чатах
        await call.message.answer(
            text=rules,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="← Главное меню", callback_data="main_menu"),
                        InlineKeyboardButton(text="📝 Начать заполнение", callback_data="post_vacancy")
                    ]
                ]
            )
        )
    await call.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(call: CallbackQuery) -> None:
    await call.message.answer(
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

    await call.message.answer(
        text="Автоматически оформлю текст, подберу теги и проверю данные. Поехали!",
        reply_markup=keyboard
    )
    await call.answer()


@router.callback_query(F.data == "contact_support")
async def send_contact_support_msg(call: CallbackQuery, state: FSMContext) -> None:
    if call.message.chat.id > 0:  # Только в личных чатах
        await call.message.answer(
            text=help_msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="← Главное меню", callback_data="main_menu"),
                        InlineKeyboardButton(text="📝 Начать заполнение", callback_data="post_vacancy")
                    ]
                ]
            )
        )
    await call.answer()


@router.callback_query(F.data == "post_vacancy")
async def vacancy_name(call: CallbackQuery, state: FSMContext) -> None:
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            await state.set_state(VacancySurvey.vacancy_name)
            await call.message.answer(
                text=vacancy_form,
                parse_mode="HTML"
            )
            await call.message.answer(
                text="🔹 Введите название вакансии. Например: 'Системный аналитик на проект внедрения CRM'.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await call.message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.vacancy_name)
async def vacancy_choose_category(message: Message, state: FSMContext):
    if message.text:
        if message.chat.id < 0:
            pass
        else:
            if message.text != "/back":
                await state.update_data(vacancy_name=message.text)
            else:
                await state.update_data(vacancy_name="")
            await state.set_state(VacancySurvey.choosing_category)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "🖍 Выберите категорию позиции. Это поможет нам правильно направить вашу вакансию.",
                reply_markup=make_inline_keyboard(available_categories),
            )
    else:
        await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.choosing_category)
async def vacancy_category_chosen(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            await state.update_data(category=call.data)
            await call.message.answer(
                text=f"Выбранная вами категория: {call.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(VacancySurvey.company_name)
            await vacancy_company_name(call.message, state)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.company_name)
async def vacancy_company_name(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "🏢 Введите название компании. Например: 'Bell Integrator'."
            )
            await state.set_state(VacancySurvey.grade)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.grade)
async def vacancy_grade(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(company_name=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            state = await state.get_state()
            await message.answer(
                "🧑‍💻 Выберите грейд.",
                reply_markup=make_inline_keyboard(available_grades),
            )

        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.grade)
async def vacancy_grade_chosen(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            if call.message.text != "/back":
                await state.update_data(grade=call.data)
            await call.message.answer(
                text=f"Выбранный вами грейд: {call.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await vacancy_location(call.message, state)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


async def vacancy_location(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "🌍 Укажите локацию кандидата.",
                reply_markup=make_inline_keyboard(available_locations)
            )
            await state.set_state(VacancySurvey.timezone)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.timezone)
async def vacancy_location_chosen(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            await state.update_data(location=call.data)
            await call.message.answer(
                text=f"Выбранная вами локация: {call.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await vacancy_timezone(call.message, state)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


async def vacancy_timezone(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                text="🕕 Следующий пункт: город и/или часовой пояс."
            )
            await state.set_state(VacancySurvey.job_format)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.job_format)
async def vacancy_job_format(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(timezone=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "💼 Выберите формат работы. Например: 'Удалённо', 'Офис' или 'Гибридный'.",
                reply_markup=make_inline_keyboard(available_job_formats)
            )
            await state.set_state(VacancySurvey.subject_area)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.subject_area)
async def vacancy_subject_area(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            if call.data != "fake_callback_data":
                await state.update_data(job_format=call.data)
            global selected_subjects
            selected_subjects = []
            await call.message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await call.message.answer(
                text="📊 Следующий пункт: предметная область. Это поле обязательное.\n\nДоступные варианты:",
                reply_markup=make_inline_keyboard(available_subject_areas)
            )
            await state.set_state(VacancySurvey.choosing_subject_area)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.choosing_subject_area)
async def vacancy_choosing_subject_area(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            global selected_subjects

            subject = call.data
            if subject not in selected_subjects:
                selected_subjects.append(subject)
            subjects = ", ".join(selected_subjects)
            if any(value in subjects for value in ["medtech", "госсистемы", "стройтех"]):
                await vacancy_skip_subject_area(call.message, state)
            else:
                if len(selected_subjects) < 3:
                    await call.message.answer(
                        f"Вы выбрали {subjects}. Хотите добавить еще предметные области или перейти к след пункту?",
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    KeyboardButton(text="Добавить еще"),
                                    KeyboardButton(text="Перейти к следующему пункту"),
                                ]
                            ],
                            resize_keyboard=True,
                        ),
                    )
                else:
                    await vacancy_skip_subject_area(call.message, state)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.choosing_subject_area, F.text == "Добавить еще")
async def vacancy_add_subject_are(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            global selected_subjects
            subjects = ', '.join(selected_subjects)
        if len(selected_subjects) < 3:
            if any(value in subjects for value in ["medtech", "госсистемы", "стройтех"]):
                await message.delete(reply_markup=ReplyKeyboardRemove())
                await state.set_state(VacancySurvey.project_theme)
                await vacancy_project_theme(message, state)
                await state.update_data(subjects=subjects)
            else:
                await message.answer(
                    f"Вы выбрали: {subjects}. Пожалуйста, выберите еще {3 - len(selected_subjects)} вариант(а).",
                    reply_markup=make_inline_keyboard(available_subject_areas))
        else:
            await message.delete(reply_markup=ReplyKeyboardRemove())
            await state.set_state(VacancySurvey.project_theme)
            await vacancy_project_theme(message, state)
            await state.update_data(subjects=subjects)


@router.message(VacancySurvey.choosing_subject_area, F.text == "Перейти к следующему пункту")
async def vacancy_skip_subject_area(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            global selected_subjects
            subjects = ', '.join(selected_subjects)
            if message.text != "/back":
                selected_subjects = []
                await state.update_data(subjects=subjects)

            await message.answer(f"Ваши предметные области: {subjects}",
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(VacancySurvey.project_theme)
            await vacancy_project_theme(message, state)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.project_theme)
async def vacancy_project_theme(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer("Следующий пункт — тематика проекта. Например, нейросети.")
            await state.set_state(VacancySurvey.salary)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.salary)
async def vacancy_salary(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(project_theme=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "💰 Укажите зарплату. Например: '200-250k Gross' или 'от 150k Net'. Пожалуйста, укажите, Gross это или "
                "Net."
            )
            await state.set_state(VacancySurvey.requirements)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.requirements)
async def vacancy_requirements(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(salary=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "🎯 Опишите требования к кандидату. Например: 'Опыт работы от 3 лет, знание SQL и Python'.",
                parse_mode='HTML'
            )
            await state.set_state(VacancySurvey.tasks)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.tasks)
async def vacancy_tasks(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(requirements=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "✅ Опишите рабочие задачи. Например: 'Разработка ТЗ, анализ бизнес-процессов'."
            )
            await state.set_state(VacancySurvey.bonus)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.bonus)
async def vacancy_bonus(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(tasks=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "📌 Опишите условия работы и бонусы. Например: 'Компенсация английского, гибкий график'.",
            )
            await state.set_state(VacancySurvey.wishes)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.wishes)
async def vacancy_wishes(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(bonus=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "✨ Введите пожелания.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.additional)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.additional)
async def vacancy_additional(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(wishes=message.text)
            else:
                await state.update_data(wishes="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "ℹ️ Укажите дополнительную информацию, если нужно. Например, ссылку на сайт компании или другие детали.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.contacts)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.contacts)
async def vacancy_contacts(message: Message, state: FSMContext):
    if message.chat.id < 0:
        return

    if message.text:
        if message.text != "Пропустить этот пункт" and message.text != "/back":
            await state.update_data(additional=message.text)
        else:
            await state.update_data(additional="")
        await message.answer(
            text="Чтобы вернуться к предыдущему шагу,\nвведите /back",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "📩 Укажите контакты для связи. Например: '@' или 'example@mail.ru'.",
            reply_markup=ReplyKeyboardRemove()
        )

        await state.set_state(VacancySurvey.finish)
    else:
        await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.finish)
async def finish_state(message: Message, state: FSMContext):
    if message.chat.id < 0:
        return

    if not message.text:
        await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")
        return
    data = await state.get_data()
    print(data)
    if 'contacts' not in data or not data['contacts']:
        if "@" not in message.text:
            await message.answer("Введите ваши контакты через @")
            return

    if message.text != "Выберите поле, которое хотите отредактировать.\n\nДоступные варианты:":
        data['contacts'] = message.text
        await state.update_data(contacts=message.text)
    result_output = f"Ваша вакансия:\n"
    result = ""
    result += f"🚀 <b>Вакансия</b>: {data['vacancy_name']} ({data['grade']})\n"

    result += f"🏢 <b>Компания</b>: {data['company_name']}\n"

    result += f"🌎 <b>Локация</b>: {data['location']}\n"
    result += f"🕕 <b>Часовой пояс</b>: {data['timezone']}\n"
    result += f"💼 <b>Формат работы</b>: {data['job_format']}\n\n"

    result += f"💰 <b>Зарплата</b>: {data['salary']}\n"
    result += f"📊 <b>Отрасли</b>: {data['subjects']}\n\n"

    result += f"🎯 <b>Требования</b>:\n" + data['requirements'] + "\n\n"
    if data['wishes']:
        result += f"✨ <b>Пожелания</b>:\n" + data['wishes'] + "\n\n"
    result += f"✅ <b>Рабочие задачи</b>:\n" + data['tasks'] + "\n\n"
    result += f"📌 <b>Условия</b>:\n" + data['bonus'] + "\n\n"
    result += f"📩 <b>Контакты</b>:\n {data['contacts']}\n\n"
    if data['additional']:
        result += f"ℹ️ <b>Дополнительно</b>:\n" + data['additional'] + "\n\n"

    if "tags" not in data:
        tags = ""
        for tag in common_tags:
            if tag in result.lower():
                tags += f"{common_tags[tag]} "
    else:
        tags = data['tags']
    result += f"{tags}"
    await state.update_data(tags=tags)
    data['tags'] = tags
    if len(str(result_output + result)) > 4096:
        await message.answer(
            "Ваша вакансия длиннее 4096 символов.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="/start"),
                        KeyboardButton(text="Редактировать вакансию")
                    ]
                ],
                resize_keyboard=True,
            )
        )
    else:
        await message.answer(
            result_output + result,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="/start"),
                        KeyboardButton(text="Опубликовать вакансию"),
                        KeyboardButton(text="Редактировать вакансию"),
                    ]
                ],
                resize_keyboard=True,
            )
        )
    await state.update_data(result=result)
    await state.set_state(VacancySurvey.send_vacancy)
    field_validation = check_data_length(data)

    if field_validation is None:
        status, result = check_and_save_job(data)
        if status:
            job_id = result
            await state.update_data(job_id=job_id)
            await message.answer("Вакансия успешно сохранена.")
        else:
            if is_job_posted(result):
                error_message = result
                await message.answer(f"Ошибка: {error_message}")
    else:
        # Если проверка длины не прошла, выводим сообщение об ошибке
        await message.answer(
            field_validation + " Отредактируйте это поле.",
            reply_markup=None
        )


@router.message(VacancySurvey.send_vacancy)
async def process_vacancy_sending(message: Message, state: FSMContext):
    if message.chat.id < 0:
        return
    else:
        data = await state.get_data()
        result = data['result']

        if message.text == 'Редактировать вакансию':
            await state.set_state(VacancySurvey.edit_vacancy)
            await edit_vacancy(message, state)
        elif message.text == 'Опубликовать вакансию':
            db_result = mark_job_as_posted(data['job_id'])
            if not db_result:
                await message.answer(
                    "Такая вакансия уже есть! Заполните ее заново",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="/start"),
                            ]
                        ],
                        resize_keyboard=True,
                    )
                )
            else:
                channel = routing(data)
                chat_id = channel["chat_id"]
                message_thread_id = channel["message_thread_id"]
                chat_id_without_at = channel['chat_id'].replace("@", "")
                repeat_channel = repeat_sending(data)
                if repeat_channel is None:
                    if message_thread_id is not None:
                        await message.answer(
                            f"Вакансия отправлена в чат: t.me/{chat_id_without_at}/{message_thread_id}"
                        )
                    else:
                        await message.answer(
                            f"Вакансия отправлена в чат: t.me/{chat_id_without_at}"
                        )
                else:
                    repeat_chat_id = repeat_channel["chat_id"]
                    repeat_message_thread_id = repeat_channel["message_thread_id"]
                    repeat_chat_id_without_at = repeat_channel['chat_id'].replace("@", "")
                    if message_thread_id is not None:
                        chat_link = f"t.me/{chat_id_without_at}/{message_thread_id}"
                    else:
                        chat_link = f"t.me/{chat_id_without_at}"

                    if repeat_message_thread_id is not None:
                        repeat_chat_link = f"t.me/{repeat_chat_id_without_at}/{repeat_message_thread_id}"
                    else:
                        repeat_chat_link = f"t.me/{repeat_chat_id_without_at}"

                    await message.answer(
                        f"Вакансия отправлена в чаты: {chat_link} и {repeat_chat_link}"
                    )
                    post_vacancy(repeat_chat_id, result, repeat_message_thread_id)

                post_vacancy(chat_id, result, message_thread_id)

                await message.answer(
                    "Заполните еще одну вакансию!",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="/start"),
                            ]
                        ],
                        resize_keyboard=True,
                    )
                )
        else:
            await message.answer(
                "Заполните еще одну вакансию!",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/start"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )


@router.message(VacancySurvey.edit_vacancy)
async def edit_vacancy(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        await message.answer(
            text="Выберите поле, которое хотите отредактировать.\n\nДоступные варианты:",
            reply_markup=make_inline_keyboard(variants)
        )
        await state.set_state(VacancySurvey.edit_field)


@router.callback_query(VacancySurvey.edit_field)
async def edit_field(call: CallbackQuery, state: FSMContext):
    if call.data == "Вернуться к вакансии":
        await state.set_state(VacancySurvey.finish)
        await finish_state(call.message, state)
    else:
        data = await state.get_data()
        if call.data in data_dict:
            editing_field_key = data_dict[call.data]
            current_value = data.get(editing_field_key)

            if current_value:
                await call.message.answer(
                    text=f"Сейчас поле {call.data} выглядит так: {current_value}."
                )
            else:
                await call.message.answer(
                    text=f"Сейчас поле {call.data} не заполнено."
                )

            # Сохраняем ключ редактируемого поля в состоянии
            await state.update_data(editing_field_key=editing_field_key)

            # Определяем, какое поле редактируем и настраиваем клавиатуру
            inline_keyboards = {
                "Категория": available_categories,
                "Грейд": available_grades,
                "Формат работы": available_job_formats,
                "Предметные области": available_subject_areas,
                "Локация": available_locations
            }

            if call.data in inline_keyboards:
                await call.message.answer(
                    "Выберите из предложенных вариантов:",
                    reply_markup=make_inline_keyboard(inline_keyboards[call.data])
                )
                # Переходим в состояние ожидания выбора из инлайн-клавиатуры
                await state.set_state(VacancySurvey.waiting_inline_choice)
            else:
                # Для полей с текстовым вводом
                await call.message.answer(
                    text="Заполните поле заново:",
                    reply_markup=ReplyKeyboardRemove()
                )
                await state.set_state(VacancySurvey.update_edited_field)
        else:
            await call.message.answer(text="Неизвестное поле для редактирования.")


# Обработчик выбора из инлайн-клавиатуры
@router.callback_query(VacancySurvey.waiting_inline_choice)
async def handle_inline_choice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    editing_field_key = data.get('editing_field_key')

    # Сохраняем выбранное значение
    await state.update_data(**{editing_field_key: call.data})

    # Удаляем инлайн-клавиатуру
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer("✅ Значение успешно обновлено!")
    await state.set_state(VacancySurvey.finish)
    await edit_vacancy(call.message, state)


# Обработчик текстового ввода для полей без инлайн-клавиатуры
@router.message(VacancySurvey.update_edited_field)
async def update_edited_field(message: Message, state: FSMContext):
    data = await state.get_data()
    editing_field_key = data.get('editing_field_key')

    current_data = await state.get_data()

    current_data = await state.get_data()

    if editing_field_key == "tags":
        current_tags = current_data.get("tags", "")

        formatted_new_tags = format_hashtags(message.text, delimiter=' ')

        separator = " " if current_tags else ""
        new_tags = f"{current_tags}{separator}{formatted_new_tags}".strip()

        await state.update_data(tags=new_tags)
    else:
        await state.update_data(**{editing_field_key: message.text})
    await message.reply("✅ Значение успешно обновлено!")

    await state.set_state(VacancySurvey.finish)
    await edit_vacancy(message, state)


@router.message(F.text)
async def any_message_handler(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        current_state = await state.get_state()
        print(current_state)
        if current_state in ["VacancySurvey:choosing_category", "VacancySurvey:location",
                             "VacancySurvey:choosing_subject_area",
                             "VacancySurvey:timezone", "VacancySurvey:job_format", "VacancySurvey:grade",
                             "VacancySurvey:subject_area"]:
            await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())

            if current_state == "VacancySurvey:choosing_category":
                await vacancy_choose_category(message, state)
            if current_state == "VacancySurvey:grade":
                await vacancy_grade(message, state)
            if current_state == "VacancySurvey:subject_area":
                await vacancy_job_format(message, state)
            if current_state == "VacancySurvey:timezone":
                await vacancy_location(message, state)
            if current_state == "VacancySurvey:choosing_subject_area":
                class FakeCallback:
                    def __init__(self):
                        self.message = message
                        self.data = "fake_callback_data"

                fake = FakeCallback()
                await vacancy_subject_area(fake, state)
        else:
            await message.answer(
                "Я не знаю такой команды,\nнапишите /start"
            )


def post_vacancy(chat_id, result, message_thread_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": result,
        "message_thread_id": message_thread_id,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=data)
    logging.info(f'Response status code: {response.status_code}')
    logging.info(f'Response body: {response.text}')


def format_hashtags(tags: str, delimiter: str = ' ') -> str:
    tags_list = tags.split(delimiter)
    processed = []

    for tag in tags_list:
        clean_tag = tag.strip()
        if not clean_tag:
            continue

        if not clean_tag.startswith('#'):
            processed.append(f"#{clean_tag}")
        else:
            processed.append(clean_tag)

    return delimiter.join(processed)
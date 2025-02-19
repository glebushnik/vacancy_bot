import os
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
from db_utils.db_handler import check_and_save_job, mark_job_as_posted, check_data_length
from utils.logging_config import setup_logging
from utils.variants import available_categories, available_grades, available_locations, available_subject_areas, \
    variants, data_dict
from keyboards.inline_row import make_inline_keyboard
from utils.logic import routing, repeat_sending
import requests
from aiogram.types import KeyboardButton

setup_logging()
logger = logging.getLogger(__name__)

router = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")


class VacancySurvey(StatesGroup):
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
    vacancy_code = State()
    choosing_category = State()


state_order = {
    0: VacancySurvey.vacancy_name,
    1: VacancySurvey.vacancy_code,
    2: VacancySurvey.choosing_category,
    3: VacancySurvey.company_name,
    4: VacancySurvey.company_url,
    5: VacancySurvey.grade,
    6: VacancySurvey.location,
    7: VacancySurvey.timezone,
    8: VacancySurvey.subject_area,
    9: VacancySurvey.choosing_subject_area,
    10: VacancySurvey.job_format,
    11: VacancySurvey.project_theme,
    12: VacancySurvey.salary,
    13: VacancySurvey.responsibilities,
    14: VacancySurvey.requirements,
    15: VacancySurvey.tasks,
    16: VacancySurvey.wishes,
    17: VacancySurvey.bonus,
    18: VacancySurvey.contacts,
    19: VacancySurvey.tags,
    20: VacancySurvey.finish,
    21: VacancySurvey.edit_vacancy,
    22: VacancySurvey.edit_field,
    23: VacancySurvey.update_edited_field
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
    if current_state == "VacancySurvey.vacancy_name":
        await cmd_vacancy_name(message, state)
    elif current_state == "VacancySurvey.edit_vacancy":
        await finish_state(message, state)
    elif current_state == "VacancySurvey.vacancy_code":
        await process_vacancy_name(message, state)
    elif current_state == "VacancySurvey.choosing_category":
        await process_vacancy_code(message, state)
    elif current_state == "VacancySurvey.company_name":
        await process_vacancy_code(message, state)
    elif current_state == "VacancySurvey.company_url":
        if correct_input:
            await cmd_company_name(message, state)
        else:
            await cmd_company_url(message, state)
    elif current_state == "VacancySurvey.grade":
        if correct_input:
            await cmd_company_url(message, state)
        else:
            await cmd_grade(message, state)
    elif current_state == "VacancySurvey.location":
        await cmd_grade(message, state)
    elif current_state == "VacancySurvey.timezone":
        await cmd_location(message, state)
    elif current_state == "VacancySurvey.subject_area":
        await cmd_timezone(message, state)
    elif current_state == "VacancySurvey.choosing_subject_area":
        await cmd_timezone(message, state)
    elif current_state == "VacancySurvey.job_format":
        await cmd_subject_area(message, state)
    elif current_state == "VacancySurvey.project_theme":
        global selected_subjects
        selected_subjects = []
        await cmd_job_format(message, state)
    elif current_state == "VacancySurvey.salary":
        await cmd_project_theme(message, state)
    elif current_state == "VacancySurvey.responsibilities":
        await cmd_salary(message, state)
    elif current_state == "VacancySurvey.requirements":
        await skip_salary(message, state)
    elif current_state == "VacancySurvey.tasks":
        await cmd_requirements(message, state)
    elif current_state == "VacancySurvey.wishes":
        await cmd_tasks(message, state)
    elif current_state == "VacancySurvey.bonus":
        await cmd_wishes(message, state)
    elif current_state == "VacancySurvey.contacts":
        if correct_input:
            await cmd_bonus(message, state)
        else:
            await cmd_contacts(message, state)
    elif current_state == "VacancySurvey.tags":
        if correct_input:
            await cmd_contacts(message, state)
        else:
            await cmd_tags(message, state)
    elif current_state == "VacancySurvey.finish":
        await cmd_tags(message, state)


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
                await cmd_vacancy_name(message, state)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(Command("survey"))
async def cmd_vacancy_name(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await state.set_state(VacancySurvey.vacancy_name)
            await message.answer(
                text=(
                    "<b>Все вакансии в нашей группе соответствуют форме:</b>\n\n"
                    "<b>Название:</b> [текст]\n"
                    "<b>Код вакансии:</b> [Код]\n"
                    "<b>Категория позиции:</b> [Список: аналитик 1С, BI-аналитик, аналитик данных, "
                    "продуктовый аналитик, бизнес-аналитик, аналитик бизнес-процессов, системный аналитик, "
                    "system owner, проектировщик ИТ-решений]\n"
                    "<b>Название компании:</b> [текст]\n"
                    "<b>Ссылка на сайт компании:</b> [домен]\n"
                    "<b>Уровень позиции:</b> [Junior/Middle/Senior/Lead]\n"
                    "<b>Локация кандидата:</b> [РФ, Казахстан, Беларусь, не важно]\n"
                    "<b>Город и/или тайм-зона:</b> [текст]\n"
                    "<b>Формат работы:</b> [Дистанционная, офис, гибрид]\n"
                    "<b>Предметная область проекта:</b> [Список: финтех, e-commerce, ритейл, логистика, "
                    "foodtech, edtech, стройтех, medtech, госсистемы, ERP, CRM, traveltech, авиация, другая]\n"
                    "<b>Тематика проекта:</b> [текст]\n"
                    "<b>Зарплата:</b> [текст]\n"
                    "<b>Ключевая ответственность:</b> [текст]\n"
                    "<b>Требования к кандидату:</b> [текст]\n"
                    "<b>Рабочие задачи:</b> [текст]\n"
                    "<b>Пожелания:</b> [текст]\n"
                    "<b>Бонусы:</b> [текст]\n"
                    "<b>Контакты:</b> [текст]\n"
                    "<b>Теги поста:</b> [текст]"
                ),
                parse_mode="HTML"
            )
            await message.answer(
                text="Введите название вакансии-позиции. Например, Системный аналитик на проект внедрения CRM.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.vacancy_name)
async def process_vacancy_name(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(vacancy_name=message.text)
            await state.set_state(VacancySurvey.vacancy_code)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Хорошо, теперь введите код вакансии. Например, DAT-617.\nЭто поле можно пропустить.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.vacancy_code)
async def process_vacancy_code(message: Message, state: FSMContext):
    if message.text:
        if message.chat.id < 0:
            pass
        else:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(vacancy_code=message.text)
            else:
                await state.update_data(vacancy_code="")
            await state.set_state(VacancySurvey.choosing_category)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Хорошо, теперь выберите категорию позиции.\nЭто поле обязательное.",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "Доступные варианты категорий:",
                reply_markup=make_inline_keyboard(available_categories),
            )
    else:
        await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(F.data.in_(available_categories))
async def category_chosen(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.message.chat.id < 0:
        pass
    else:
        if callback_query.message.text:
            await state.update_data(category=callback_query.data)
            await callback_query.message.answer(
                text=f"Выбранная вами категория: {callback_query.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(VacancySurvey.company_name)
            await cmd_company_name(callback_query.message, state)
        else:
            await callback_query.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.company_name)
async def cmd_company_name(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — название компании.\nЭто поле обязательное."
            )
            await state.set_state(VacancySurvey.company_url)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.company_url)
async def cmd_company_url(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back":
                await state.update_data(company_name=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Хорошо, теперь добавьте ссылку сайт вашей компании или проекта. Например: https:/domen.ru\nЭто поле можно пропустить.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.grade)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.grade)
async def cmd_grade(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            is_correct_input = True
            is_grade_state = True
            current_state = await state.get_state()
            if current_state == "VacancySurvey.location":
                is_grade_state = False
            if is_grade_state:
                if message.text != "Пропустить этот пункт":
                    if "." not in message.text:
                        is_correct_input = False
                        previous_state = await go_back(state)
                        await state.set_state(previous_state)
                        await message.answer(f"Введите корректный сайт компании, например, kremlin.ru",
                                             reply_markup=ReplyKeyboardRemove())
                        await send_prompt_for_state(state, message, False)
                    else:
                        if message.text != "/back":
                            await state.update_data(company_url=message.text)
                else:
                    await state.update_data(company_url="")
            if is_correct_input:
                await message.answer(
                    text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
                )
                await message.answer(
                    "Выберите грейд. Это поле можно пропустить.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="Пропустить этот пункт"),
                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
                await message.answer(
                    "Доступные варианты грейдов:",
                    reply_markup=make_inline_keyboard(available_grades),
                )
                await state.set_state(VacancySurvey.location)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.location, F.text == "Пропустить этот пункт")
async def grade_skipped(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await state.update_data(grade="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — локация.\nЭто поле обязательное.",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "Доступные варианты локации:",
                reply_markup=make_inline_keyboard(available_locations)
            )
            await state.set_state(VacancySurvey.timezone)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(F.data.in_(available_grades))
async def grade_chosen(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.message.chat.id < 0:
        pass
    else:
        if callback_query.message.text:
            await state.update_data(grade=callback_query.data)
            await callback_query.message.answer(
                text=f"Выбранный вами грейд: {callback_query.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await cmd_location(callback_query.message, state)
        else:
            await callback_query.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


async def cmd_location(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — локация.\nЭто поле обязательное.",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "Доступные варианты локации:",
                reply_markup=make_inline_keyboard(available_locations)
            )
            await state.set_state(VacancySurvey.timezone)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(F.data.in_(available_locations))
async def location_chosen(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.message.chat.id < 0:
        pass
    else:
        if callback_query.message.text:
            await state.update_data(location=callback_query.data)
            await callback_query.message.answer(
                text=f"Выбранная вами локация: {callback_query.data}.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await cmd_timezone(callback_query.message, state)
        else:
            await callback_query.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


async def cmd_timezone(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                text="Следующий пункт: город и/или часовой пояс.\nЭто поле обязательное."
            )
            await state.set_state(VacancySurvey.subject_area)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.subject_area)
async def cmd_subject_area(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            global selected_subjects
            selected_subjects = []
            if message.text != "/back":
                await state.update_data(timezone=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                text="Следующий пункт: предметная область. Это поле обязательное.\n\nДоступные варианты:",
                reply_markup=make_inline_keyboard(available_subject_areas)
            )
            await state.set_state(VacancySurvey.choosing_subject_area)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.callback_query(VacancySurvey.choosing_subject_area)
async def choosing_subject_area(call: CallbackQuery, state: FSMContext):
    if call.message.chat.id < 0:
        pass
    else:
        if call.message.text:
            global selected_subjects

            subject = call.data
            if subject not in selected_subjects:
                selected_subjects.append(subject)
            subjects = ", ".join(selected_subjects)

            if len(selected_subjects) >= 1:
                await call.message.answer(
                    "Вы можете перейти к следующему шагу.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="Пропустить этот пункт"),

                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
            if len(selected_subjects) < 3:
                if any(value in subjects for value in ["medtech", "госсистемы", "стройтех"]):
                    await call.message.answer(f"Вы выбрали: {subjects}.",
                                              reply_markup=ReplyKeyboardRemove())
                    await call.message.delete()
                    await state.set_state(VacancySurvey.job_format)
                    await cmd_job_format(call.message, state)
                    await state.update_data(subjects=subjects)
                else:
                    await call.message.answer(
                        f"Вы выбрали: {subjects}. Пожалуйста, выберите еще {3 - len(selected_subjects)} вариант(а).",
                        reply_markup=make_inline_keyboard(available_subject_areas))
            else:
                await call.message.answer(f"Вы выбрали: {subjects}.",
                                          reply_markup=ReplyKeyboardRemove())
                await call.message.delete()
                await state.set_state(VacancySurvey.job_format)
                await cmd_job_format(call.message, state)
                await state.update_data(subjects=subjects)
        else:
            await call.message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.choosing_subject_area, F.text == "Пропустить этот пункт")
async def skip_subject_area(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            global selected_subjects
            subjects = ' ,'.join(selected_subjects)
            if message.text != "/back":
                selected_subjects = []
                await state.update_data(subjects=subjects)

            await message.answer(f"Вы выбрали:{subjects}",
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(VacancySurvey.job_format)
            await cmd_job_format(message, state)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


async def cmd_job_format(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer("Следующий пункт — формат работы. Например, гибрид.\nЭто поле обязательное.")
            await state.set_state(VacancySurvey.project_theme)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.project_theme)
async def cmd_project_theme(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            await state.update_data(job_format=message.text)
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer("Следующий пункт — тематика проекта. Например, нейросети.\nЭто поле обязательное.")
            await state.set_state(VacancySurvey.salary)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.salary)
async def cmd_salary(message: Message, state: FSMContext):
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
                "Хорошо, теперь введите зарплату. Например, 100000₽.\nЭто поле можно пропустить.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.responsibilities)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.responsibilities)
async def skip_salary(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(salary=message.text)
            else:
                await state.update_data(salary="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — ключевая зона ответственности. Это основная обязанность кандидата.\nНапример, разрабатывать "
                "ТЗ и проектировать интеграции."
                "\nТребования к кандидату будут заполняться на следующих шагах."
                "\nЭто поле можно пропустить.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.requirements)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.requirements)
async def cmd_requirements(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back" and message.text != "Пропустить этот пункт":
                await state.update_data(responsibilities=message.text)
            else:
                await state.update_data(responsibilities="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — <b>требования</b>. Например, быть онлайн 24/7.\n"
                "Здесь указываются <b>обязательные</b> требования к кандидату. Поле для <b>пожеланий</b> и основных задач "
                "будет предложено "
                "для заполнения далее.\n"
                "Это поле обязательное.",
                parse_mode='HTML'
            )
            await state.set_state(VacancySurvey.tasks)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.tasks)
async def cmd_tasks(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "/back" and message.text != "Пропустить этот пункт":
                await state.update_data(requirements=message.text)
            else:
                await state.update_data(requirements="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Хорошо, теперь введите основные задачи. Например, писать код.\nЭто поле можно пропустить.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Пропустить этот пункт"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
            await state.set_state(VacancySurvey.wishes)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.wishes)
async def cmd_wishes(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(tasks=message.text)
            else:
                await state.update_data(tasks="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Хорошо, теперь введите пожелания. Например, Английский C1.\nЭто поле можно пропустить.",
            )
            await state.set_state(VacancySurvey.bonus)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.bonus)
async def cmd_bonus(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(wishes=message.text)
            else:
                await state.update_data(wishes="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Теперь введите бонусы. Например, мерч, ДМС, 13-я ЗП.\n"
                "Здесь же вы можете указать особенности и преимущества вашей компании.\n"
                "Это поле можно пропустить.",
            )
            await state.set_state(VacancySurvey.contacts)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.contacts)
async def cmd_contacts(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            if message.text != "Пропустить этот пункт" and message.text != "/back":
                await state.update_data(bonus=message.text)
            else:
                await state.update_data(bonus="")
            await message.answer(
                text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
            )
            await message.answer(
                "Следующий пункт — контакты. Например, @telegramuser Ivan Ivanov, CEO.\nЭто поле обязательное.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(VacancySurvey.tags)
        else:
            await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.tags)
async def cmd_tags(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            is_correct_input = True
            is_contacts = True
            current_state = await state.get_state()
            if current_state == "VacancySurvey.tags":
                is_contacts = False
            if "@" not in message.text and is_contacts:
                is_correct_input = False
                previous_state = await go_back(state)
                await state.set_state(previous_state)
                await message.answer(f"Введите ваш telegram через @")
                await send_prompt_for_state(state, message, False)
            if is_correct_input:
                await state.set_state(VacancySurvey.finish)
                if is_contacts:
                    if message.text != "/back":
                        await state.update_data(contacts=message.text)
                await message.answer(
                    text="Чтобы вернуться к предыдущему шагу,\nвведите /back"
                )
                await message.answer(
                    "Хорошо, теперь теги. Например, #интеграция, #B2B, #SaaS, #API\nЭто поле можно пропустить.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="Пропустить этот пункт"),
                            ]
                        ],
                        resize_keyboard=True,
                    )
                )
            else:
                await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


@router.message(VacancySurvey.finish)
async def finish_state(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        if message.text:
            correct_input = True
            if message.text != "Выберите поле, которое хотите отредактировать.\n\nДоступные варианты:":
                await state.update_data(tags=message.text)
            if correct_input:
                data = await state.get_data()

                result_output = f"Ваша вакансия:\n"
                result = ""
                result += f"<b>{data['vacancy_name']}</b>\n"

                if data['grade']:
                    result += f"<b>Грейд</b>: {data['grade']}\n"

                result += f"<b>Название компании</b>: {data['company_name']}\n"

                if data['company_url']:
                    result += f"<b>URL компании</b>: {data['company_url']}\n"

                result += f"\n<b>Локация</b>: {data['location']}\n"

                result += f"<b>Часовой пояс</b>: {data['timezone']}\n"

                result += f"<b>Предметные области</b>: {data['subjects']}\n"

                result += f"<b>Формат работы</b>: {data['job_format']}\n"

                result += f"\n<b>Тема проекта</b>: {data['project_theme']}\n"

                if data['salary']:
                    result += f"\n<b>Зарплата</b>: {data['salary']}\n"

                if data['responsibilities']:
                    result += f"\n<b>Обязанности</b>:\n" + data['responsibilities'] + "\n"

                if data['requirements']:
                    result += f"\n<b>Требования</b>:\n" + data['requirements'] + "\n"

                if data['tasks']:
                    result += f"\n<b>Задачи</b>:\n" + data['tasks'] + "\n"

                if data['wishes']:
                    result += f"\n<b>Пожелания</b>:\n" + data['wishes'] + "\n"

                if data['bonus']:
                    result += f"\n<b>Бонусы</b>:\n" + data['bonus'] + "\n"

                result += f"\n<b>Контактные данные</b>: {data['contacts']}\n"

                if data['tags']:
                    tags=data['tags']
                    valid_tags = ' '.join(
                    f'#{word}' if not word.startswith('#') else word for word in tags.split())
                    result += f"\n" + valid_tags + "\n"
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
                # Проверяем длину полей
                field_validation = check_data_length(data)

                if field_validation is None:
                    # Если проверка длины прошла успешно, сохраняем данные
                    status, result = check_and_save_job(data)
                    if status:  # Если статус True, значит, запись успешно добавлена
                        job_id = result  # result содержит lastrowid
                        await state.update_data(job_id=job_id)  # Обновляем состояние
                        await message.answer("Вакансия успешно сохранена.")
                    else:  # Если статус False, значит, произошла ошибка
                        error_message = result  # result содержит сообщение об ошибке
                        await message.answer(f"Ошибка: {error_message}")
                else:
                    # Если проверка длины не прошла, выводим сообщение об ошибке
                    await message.answer(
                        field_validation + " Отредактируйте это поле.",
                        reply_markup=None
                    )

            else:
                await message.reply("Пожалуйста, отправьте текст, а не фото или другой тип данных.")


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
            # Проверка и вставка вакансии
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
async def edit_field(query: CallbackQuery, state: FSMContext):
    if query.data == "Вернуться к вакансии":
        await state.set_state(VacancySurvey.finish)
        await finish_state(query.message, state)
    else:
        data = await state.get_data()
        if query.data in data_dict:
            editing_field_key = data_dict[query.data]
            current_value = data.get(editing_field_key)

            if current_value != "":
                await query.message.answer(
                    text=f"Сейчас поле {query.data} выглядит так: {current_value}."
                )
            else:
                await query.message.answer(
                    text=f"Сейчас поле {query.data} не заполнено."
                )

            await state.set_state(VacancySurvey.update_edited_field)
            await state.update_data(editing_field_key=editing_field_key)

            await query.message.answer(
                text="Заполните поле заново.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await query.message.answer(text="Неизвестное поле для редактирования.")


@router.message(VacancySurvey.update_edited_field)
async def update_edited_field(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        data = await state.get_data()
        editing_field_key = data.get('editing_field_key')

        await state.update_data(**{editing_field_key: message.text})

        await message.reply(
            text="Отлично, сохранил отредактированное поле."
        )

        await state.set_state(VacancySurvey.finish)
        await edit_vacancy(message, state)


@router.message(F.text)
async def any_message_handler(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        current_state = await state.get_state()

        if current_state in ["VacancySurvey:choosing_category", "VacancySurvey:location",
                             "VacancySurvey:choosing_subject_area",
                             "VacancySurvey:timezone"]:
            await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())

            if current_state == "VacancySurvey:choosing_category":
                await process_vacancy_code(message, state)
            if current_state == "VacancySurvey:location":
                await message.answer(
                    "Выберите грейд. Это поле можно пропустить.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text="Пропустить этот пункт"),
                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
                await message.answer(
                    "Доступные варианты грейдов:",
                    reply_markup=make_inline_keyboard(available_grades),
                )
                await state.set_state(VacancySurvey.location)

            if current_state == "VacancySurvey:timezone":
                await cmd_location(message, state)
            if current_state == "VacancySurvey:choosing_subject_area":
                await cmd_subject_area(message, state)
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

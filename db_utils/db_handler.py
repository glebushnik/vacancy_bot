import mysql.connector
import os
from mysql.connector import errorcode
import logging
# Ограничения длины полей на основе вашей таблицы
FIELD_MAX_LENGTHS = {
    'vacancy_name': 255,
    'vacancy_code': 50,
    'category': 100,
    'company_name': 255,
    'company_url': 255,
    'grade': 50,
    'location': 255,
    'timezone': 50,
    'subjects': 500,
    'job_format': 50,
    'project_theme': 255,
    'salary': 50,
    'contacts': 255,
    'tags': 255,
    'responsibilities': 65535,  # Ограничение для TEXT поля
    'requirements': 65535,      # Ограничение для TEXT поля
    'tasks': 65535,             # Ограничение для TEXT поля
    'wishes': 65535,            # Ограничение для TEXT поля
    'bonus': 65535,             # Ограничение для TEXT поля
}

def check_data_length(data):
    for field, max_length in FIELD_MAX_LENGTHS.items():
        value = data.get(field)
        if value and len(str(value)) > max_length:
            return f"Поле '{field}' превышает максимальную длину {max_length} символов."
    return None

def check_and_save_job(data):
    try:
        # Проверка длины данных перед вставкой
        length_error = check_data_length(data)
        if length_error:
            return length_error

        # Устанавливаем подключение к базе данных
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()

        check_query = """
            SELECT COUNT(*) 
            FROM job 
            WHERE vacancy_name = %s 
            AND company_name = %s 
            AND grade = %s
        """
        cursor.execute(check_query, (
            data["vacancy_name"],
            data["company_name"],
            data["grade"]
        ))
        count = cursor.fetchone()[0]

        if count == 0:
            # Если запись не существует, вставляем новую
            insert_query = """
                INSERT INTO job (
                    vacancy_name, vacancy_code, category, company_name, 
                    company_url, grade, location, timezone, subjects, 
                    job_format, project_theme, salary, responsibilities, 
                    requirements, tasks, wishes, bonus, contacts, tags, is_posted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                          %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data['vacancy_name'],
                data.get('vacancy_code'),  # Может быть None
                data['category'],
                data['company_name'],
                data.get('company_url'),
                data.get('grade'),
                data['location'],
                data['timezone'],
                data['subjects'],
                data['job_format'],
                data['project_theme'],
                data.get('salary'),
                data.get('responsibilities'),
                data.get('requirements'),
                data.get('tasks'),
                data.get('wishes'),
                data.get('bonus'),
                data['contacts'],
                data.get('tags'),
                False
            ))
            conn.commit()
            logging.info(f"Вакансия '{data['vacancy_name']}' успешно сохранена с ID {cursor.lastrowid}.")
            return cursor.lastrowid
        else:
            logging.info(f"Вакансия '{data['vacancy_name']}' уже существует.")
            return False

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Ошибка с именем пользователя или паролем")
            return
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("База данных не существует")
            return
        elif err.errno == errorcode.ER_DUP_ENTRY:
            logging.error("Ошибка: дублирующая запись. Вакансия с такими данными уже существует.")
            return
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW:
            logging.error("Ошибка: нарушение ссылочной целостности. Проверьте корректность данных.")
            return
        elif err.errno == errorcode.ER_DATA_TOO_LONG:
            logging.error("Ошибка: данные слишком длинные для одного из полей.")
            return
        else:
            logging.error(f"Произошла ошибка при сохранении вакансии: {err}")
            return

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def mark_job_as_posted(job_id):
    try:
        # Устанавливаем подключение к базе данных
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()

        update_query = """
            UPDATE job 
            SET is_posted = TRUE 
            WHERE id = %s
        """
        cursor.execute(update_query, (job_id,))
        conn.commit()

        if cursor.rowcount > 0:
            logging.info(f"Вакансия с ID {job_id} успешно помечена как опубликованная.")
            return True
        else:
            logging.warning(f"Вакансия с ID {job_id} не найдена.")
            return False

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Ошибка с именем пользователя или паролем")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("База данных не существует")
        else:
            logging.error(f"Произошла ошибка при обновлении вакансии: {err}")
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
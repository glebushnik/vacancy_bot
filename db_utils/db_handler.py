import mysql.connector
import os
from mysql.connector import errorcode
import logging

# Обновленные ограничения длины для актуальных полей
FIELD_MAX_LENGTHS = {
    'vacancy_name': 255,
    'category': 100,
    'company_name': 255,
    'grade': 50,
    'location': 255,
    'job_format': 250,
    'timezone': 100,
    'subjects': 500,
    'project_theme': 500,
    'salary': 250,
    'requirements': 65535,
    'tasks': 65535,
    'bonus': 65535,
    'wishes': 65535,
    'additional': 65535,
    'contacts': 255,
    'tags': 255,
}


def check_data_length(data):
    for field, max_length in FIELD_MAX_LENGTHS.items():
        if field in data and len(str(data[field])) > max_length:
            return f"Поле '{field}' превышает максимальную длину {max_length} символов."
    return None


def check_and_save_job(data):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # Проверка существования вакансии
        check_query = """
            SELECT COUNT(*) 
            FROM job 
            WHERE vacancy_name = %s 
            AND company_name = %s 
            AND project_theme = %s
        """
        cursor.execute(check_query, (
            data["vacancy_name"],
            data["company_name"],
            data["project_theme"]
        ))

        if cursor.fetchone()[0] > 0:
            logging.warning(f"Дубликат вакансии: {data['vacancy_name']}")
            return False, "Вакансия уже существует"

        # Вставка только существующих полей
        insert_query = """
            INSERT INTO job (
                vacancy_name, category, company_name, grade, 
                location, job_format, timezone, subjects, 
                project_theme, salary, requirements, tasks, 
                bonus, wishes, additional, contacts, tags, is_posted
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        insert_data = (
            data['vacancy_name'],
            data['category'],
            data['company_name'],
            data.get('grade'),
            data['location'],
            data['job_format'],
            data['timezone'],
            data['subjects'],
            data['project_theme'],
            data.get('salary'),
            data.get('requirements'),
            data.get('tasks'),
            data.get('bonus'),
            data.get('wishes'),
            data.get('additional'),
            data['contacts'],
            data.get('tags'),
            False
        )

        cursor.execute(insert_query, insert_data)
        conn.commit()
        return True, cursor.lastrowid

    except mysql.connector.Error as err:
        error_msg = f"Ошибка базы данных: {err}"
        logging.error(error_msg)
        return False, error_msg

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def mark_job_as_posted(job_id):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE job SET is_posted = TRUE WHERE id = %s", (job_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logging.error(f"Ошибка отметки публикации: {e}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def is_job_posted(job_id: int) -> bool:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT is_posted FROM job WHERE id = %s", (job_id,))
        result = cursor.fetchone()

        if result:
            return bool(result[0])
        return False

    except Exception as e:
        logging.error(f"Ошибка проверки статуса публикации: {e}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
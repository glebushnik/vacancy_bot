import mysql.connector
import os
from mysql.connector import errorcode
import logging
# Ограничения длины полей на основе вашей таблицы
FIELD_MAX_LENGTHS = {
    'vacancy_name': 255,       # VARCHAR(255)
    'vacancy_code': 50,        # VARCHAR(50)
    'category': 100,           # VARCHAR(100)
    'company_name': 255,       # VARCHAR(255)
    'company_url': 255,        # VARCHAR(255)
    'grade': 50,               # VARCHAR(50)
    'location': 255,           # VARCHAR(255)
    'timezone': 100,           # VARCHAR(100)
    'subjects': 500,           # VARCHAR(500)
    'job_format': 250,         # VARCHAR(250)
    'project_theme': 500,      # VARCHAR(500)
    'salary': 250,             # VARCHAR(250)
    'contacts': 255,           # VARCHAR(255)
    'tags': 255,               # VARCHAR(255)
    'responsibilities': 65535, # TEXT (максимум 65 535 символов)
    'requirements': 65535,     # TEXT (максимум 65 535 символов)
    'tasks': 65535,            # TEXT (максимум 65 535 символов)
    'wishes': 65535,           # TEXT (максимум 65 535 символов)
    'bonus': 65535,            # TEXT (максимум 65 535 символов)
}

def check_data_length(data):
    for field, max_length in FIELD_MAX_LENGTHS.items():
        value = data.get(field)
        if value and len(str(value)) > max_length:
            return f"Поле '{field}' превышает максимальную длину {max_length} символов."
    return None

def check_and_save_job(data):
    try:
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
            return True, cursor.lastrowid  # Возвращаем True и ID новой записи
        else:
            logging.info(f"Вакансия '{data['vacancy_name']}' уже существует.")
            return False, "Вакансия уже существует."  # Возвращаем False и сообщение

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            error_msg = "Ошибка с именем пользователя или паролем"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            error_msg = "База данных не существует"
        elif err.errno == errorcode.ER_DUP_ENTRY:
            error_msg = "дублирующая запись. Вакансия с такими данными уже существует."
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW:
            error_msg = "нарушение ссылочной целостности. Проверьте корректность данных."
        elif err.errno == errorcode.ER_DATA_TOO_LONG:
            error_msg = "данные слишком длинные для одного из полей."
        else:
            error_msg = f"Произошла ошибка при сохранении вакансии: {err}"

        logging.error(error_msg)
        return False, error_msg

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
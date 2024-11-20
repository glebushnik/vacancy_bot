import mysql.connector
import os
from mysql.connector import errorcode

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
                    requirements, tasks, wishes, bonus, contacts, tags 
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                          %s, %s, %s, %s, %s, %s, %s)
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
            ))
            conn.commit()
            print(f"Job '{data['vacancy_name']}' saved successfully with ID {cursor.lastrowid}.")
            return True  # Успешное сохранение записи
        else:
            print(f"Job '{data['vacancy_name']}' already exists.")
            return False  # Запись уже существует

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Ошибка с именем пользователя или паролем")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("База данных не существует")
        else:
            print(f"Произошла ошибка: {err}")
    finally:
        cursor.close()
        conn.close()

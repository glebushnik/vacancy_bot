-- Создание базы данных analyst_job
CREATE DATABASE IF NOT EXISTS analyst_job;

-- Использование базы данных analyst_job
USE analyst_job;

-- Создание таблицы job
CREATE TABLE IF NOT EXISTS job (
    id BIGINT NOT NULL AUTO_INCREMENT,  -- Автоинкрементный идентификатор
    vacancy_name VARCHAR(255) NOT NULL,    -- Название вакансии
    vacancy_code VARCHAR(50) DEFAULT NULL,              -- Код вакансии
    category VARCHAR(100) DEFAULT NULL,                 -- Категория
    company_name VARCHAR(255) NOT NULL,    -- Название компании
    company_url VARCHAR(255) DEFAULT NULL,              -- URL компании
    grade VARCHAR(50) DEFAULT NULL,                     -- Грейд
    location VARCHAR(255) DEFAULT NULL,                 -- Локация
    timezone VARCHAR(50) DEFAULT NULL,                  -- Часовой пояс
    subjects VARCHAR(500) DEFAULT NULL,                 -- Предметные области
    job_format VARCHAR(50) DEFAULT NULL,                -- Формат работы
    project_theme VARCHAR(255) DEFAULT NULL,            -- Тема проекта
    salary VARCHAR(50) DEFAULT NULL,                    -- Зарплата
    responsibilities TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,        -- Обязанности
    requirements TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,            -- Требования
    tasks TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,                   -- Задачи
    wishes TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,                  -- Пожелания
    bonus TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,                   -- Бонусы
    contacts VARCHAR(255) DEFAULT NULL,                 -- Контактные данные
    tags VARCHAR(255) DEFAULT NULL,                     -- Теги
    is_posted TINYINT(1) DEFAULT NULL,                  -- Флаг публикации
);
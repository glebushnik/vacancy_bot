-- Создание базы данных analyst_job
CREATE DATABASE IF NOT EXISTS analyst_job;

-- Использование базы данных analyst_job
USE analyst_job;

-- Создание таблицы job
CREATE TABLE IF NOT EXISTS job (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- Автоинкрементный идентификатор
    vacancy_name VARCHAR(255) NOT NULL,    -- Название вакансии
    vacancy_code VARCHAR(50),              -- Код вакансии
    category VARCHAR(100),                 -- Категория
    company_name VARCHAR(255) NOT NULL,    -- Название компании
    company_url VARCHAR(255),              -- URL компании
    grade VARCHAR(50),                     -- Грейд
    location VARCHAR(255),                 -- Локация
    timezone VARCHAR(50),                  -- Часовой пояс
    subjects VARCHAR(500),                 -- Предметные области
    job_format VARCHAR(50),                -- Формат работы
    project_theme VARCHAR(255),            -- Тема проекта
    salary VARCHAR(50),                    -- Зарплата
    responsibilities VARCHAR(1000),        -- Обязанности
    requirements VARCHAR(1000),            -- Требования
    tasks VARCHAR(1000),                   -- Задачи
    wishes VARCHAR(1000),                  -- Пожелания
    bonus VARCHAR(1000),                   -- Бонусы
    contacts VARCHAR(255),                 -- Контактные данные
    tags VARCHAR(255)                      -- Теги
);

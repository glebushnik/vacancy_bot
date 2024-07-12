// init-mongo.js

// Подключение к административной базе данных
const adminDb = db.getSiblingDB('admin');

// Аутентификация с учетными данными root
adminDb.auth('admin', 'admin');

// Создание базы данных и коллекции
adminDb.getSiblingDB('vacancy_bot').createCollection('vacancies');

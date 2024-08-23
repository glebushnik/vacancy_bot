db = db.getSiblingDB('vacancy_bot');

db.createCollection('vacancies');

db.vacancies.insert([
  {
    id: 1,
    description: 'Описание вакансии 1'
  },
  {
    id: 2,
    description: 'Описание вакансии 2'
  },
  {
    id: 3,
    description: 'Описание вакансии 3'
  }
]);


# Queue System

Минимальный Django-проект для системы электронной очереди. Проект описывает типы талонов, талоны, операторов и события обслуживания.

## Стек

- Python 3.12+
- Django 6.0.5
- Django REST Framework 3.17.1
- SQLite для локальной разработки

## Возможности

- Модель типов талонов (`TicketType`)
- Связь операторов с типами талонов (`OperatorTicketType`)
- Модель талона со статусами очереди (`Ticket`)
- Журнал событий по талонам (`TicketEvent`)
- Регистрация моделей в Django Admin
- Базовые DRF-сериализаторы для сущностей очереди

## Установка и запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После запуска админ-панель доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

## Структура проекта

```text
config/      настройки и маршруты Django-проекта
tickets/     приложение с моделями очереди, сериализаторами и админкой
manage.py    CLI-утилита Django
```

## Примечание

На текущем этапе API-маршруты ещё не подключены в `config/urls.py`; работа с данными доступна через Django Admin и ORM.

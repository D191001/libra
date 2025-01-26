# Libra

Libra - это приложение для управления библиотекой, созданное с использованием FastAPI и SQLAlchemy.

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone git@github.com:D191001/libra.git

    cd libra
    ```

2. Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

## Запуск приложения

1. Запустите Docker Compose:

    ```bash
    docker-compose up --build
    docker-compose exec web alembic revision --autogenerate -m "Описание миграции"
    docker-compose exec web alembic upgrade head
    ```

2. Приложение будет доступно по адресу `http://localhost:8000`.

## Тестирование

1. Убедитесь, что виртуальное окружение активировано.
2. Запустите тесты с помощью pytest:

    ```bash
    docker-compose exec web pytest
    ```

## Маршруты API

- `POST /token` - Получение токена доступа
- `POST /users/` - Создание нового пользователя
- `GET /users/me/` - Получение информации о текущем пользователе
- `PUT /users/me/` - Обновление информации о текущем пользователе
- `GET /users/` - Получение списка пользователей (только для администраторов)
- `POST /authors/` - Создание нового автора (только для администраторов)
- `GET /authors/{author_id}` - Получение информации об авторе
- `PUT /authors/{author_id}` - Обновление информации об авторе (только для администраторов)
- `DELETE /authors/{author_id}` - Удаление автора (только для администраторов)
- `GET /authors/` - Получение списка авторов
- `POST /books/` - Создание новой книги (только для администраторов)
- `GET /books/{book_id}` - Получение информации о книге
- `PUT /books/{book_id}` - Обновление информации о книге (только для администраторов)
- `DELETE /books/{book_id}` - Удаление книги (только для администраторов)
- `GET /books/` - Получение списка книг
- `POST /book_issues/` - Выдача книги пользователю
- `PUT /book_issues/{book_issue_id}` - Обновление информации о выдаче книги
- `GET /book_issues/` - Получение списка выданных книг для текущего пользователя

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности см. в файле LICENSE.
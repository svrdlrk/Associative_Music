# 🎧 Backend - Associative Playlist
Pet- проект

Асинхронное backend-приложение на FastAPI для музыкального сервиса с возможностью регистрации пользователей, входа по JWT, создания плейлистов и управления треками. Включено логгирование действий, валидация и защита конфиденциальных данных через `.env`.

---

## 🚀 Функциональность

- 🔐 Регистрация и авторизация по JWT
- 🎼 Создание, удаление и просмотр плейлистов
- 🎵 Добавление и удаление треков в плейлистах
- 👮 Ограничения доступа (добавлять треки может только админ)
- 📦 Асинхронная работа с БД (PostgreSQL + SQLAlchemy)
- 🔄 Alembic миграции
- 📝 Логгирование ошибок, действий и запросов
- 📁 Защита конфигурации через `.env`

---

## 🛠️ Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy (async)** — ORM
- **PostgreSQL** — база данных
- **Alembic** — миграции
- **Pydantic** — валидация данных
- **JWT (jose)** — токены авторизации
- **dotenv** — переменные окружения
- **Logging** — логгирование

---

## 📦 Установка

### 1. Клонировать проект
```bash
git clone https://github.com/svrdlrk/Associative_Music.git
cd Associative_Music
```

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить файл .env
Создайте файл `.env` в папке `backend/` и добавьте:

```
DB_LOGIN=your_db_login
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=you_db_name

ADMIN_LIST=admin1@example.com,admin2@example.com
SECRET_KEY=your_secret_key
```

### 5. Применить миграции
```bash
alembic -c backend/alembic.ini upgrade head
```

### 6. Запустить сервер
```bash
uvicorn backend.main:app --reload
```

---

## 🔗 Основные эндпоинты


| Метод    | Эндпоинт                            | Описание                           |
|----------|-------------------------------------|------------------------------------|
| `POST`   | `/auth/register`                    | Регистрация пользователя           |
| `POST`   | `/auth/login`                       | Получение токена                   |
| `POST`   | `/playlists`                        | Создание плейлиста                 |
| `GET`    | `/playlists`                        | Получение своих плейлистов         |
| `POST`   | `/playlists/{id}/tracks/{track_id}` | Добавление трека в плейлист        |
| `DELETE` | `/playlists/{id}/tracks/{track_id}` | Удаление трека из плейлиста        |
| `DELETE` | `/playlists/{id}`                   | Удаление плейлиста                 |
| `GET`    | `/tracks`                           | Просмотр всех треков               |
| `POST`   | `/tracks`                           | Добавление трека (только админ)    |

---

## 📁 Структура проекта

```
backend/
├── alembic/                 # Миграции
├── auth.py                  # JWT, хеширование, токены
├── auth_router.py           # Роуты регистрации/входа
├── database.py              # БД и модели SQLAlchemy
├── logger_config.py         # Настройка логгера
├── main.py                  # Точка входа FastAPI
├── models.py                # Pydantic-схемы
├── router.py                # Роуты треков и плейлистов
├── requirements.txt         # Зависимости
└── .env                     # Настройки окружения
```

---

## 📌 TODO

- [ ] 🔍 Тестирование (pytest, httpx)
- [ ] 🐳 Docker-контейнеризация проекта
- [ ] ⏳ Ограничение запросов (rate limiting)
- [ ] 📄 Поддержка Swagger-документации (уже есть на `/docs`)
- [ ] 🧹 Улучшить читаемость кода: структурировать модули, добавить docstring-комментарии
- [ ] 🔧 Провести рефакторинг для улучшения архитектуры (при необходимости)

---

## 👤 Автор

[svrdlrk](https://github.com/svrdlrk)

---
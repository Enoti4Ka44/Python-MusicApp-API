# MusicApp API (FastAPI + SQLAlchemy + PostgreSQL)

Этот проект — серверная часть MusicApp. Приложение позволяет работать с плейлистами, треками и пользователями. Написан на **FastAPI**, использует **PostgreSQL** и **SQLAlchemy ORM**.

---

## 🚀 Стек технологий

* **Python 3.9+**
* **FastAPI** — веб‑фреймворк
* **SQLAlchemy** — ORM
* **PostgreSQL** — база данных
* **Pydantic v2** — сериализация данных

---

## 📁 Структура проекта

```
musicApp/
│
├── app/
│   ├── main.py
│   ├── database.py
|   ├── config.py
|   |
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── jwt_handler.py
│   │   └── security.py
│   ├── models/
|   |   ├── album.py
|   |   ├── playlist_track.py
│   │   ├── playlist.py
│   │   ├── track.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── playlist.py
│   │   ├── track.py
│   │   ├── album.py
│   │   └── user.py
│   ├── routes/
│   │   ├── playlist.py
│   │   ├── track.py
│   │   ├── album.py
│   │   └── auth.py
│   └── services/
│       ├── playlist_service.py
│       ├── track_service.py
│       └── album_service.py
│
├── run.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Настройка окружения

### 1. Клонируем проект

```
git clone https://github.com/Enoti4Ka44/Python-MusicApp-API.git
cd Python-MusicApp-API
```

### 2. Создаём виртуальное окружение

```
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3. Устанавливаем зависимости

```
pip install -r requirements.txt
```

### 4. Настраиваем переменные окружения

Создайте файл `.env` в корне проекта:

```
DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/musicapp_db"
SECRET_KEY="SECRET_KEY" (Ваш секретный ключ)
```

---

## ▶️ Запуск проекта

```
uvicorn app.main:app --reload
```

API будет доступен по адресу:

```
http://localhost:8000
```

Swagger документация:

```
http://127.0.0.1:8000/docs#/
```
<img width="950" height="964" alt="image" src="https://github.com/user-attachments/assets/c574d994-ab6b-447d-97ec-6ebccc9e1ed8" />

---

Учебный проект, разработан для практики FastAPI и SQLAlchemy.

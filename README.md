# Machine Learning & Big Data Portfolio

В этом репозитории собраны учебные проекты по **Машинному обучению (Machine Learning)** и **Анализу больших данных (Big Data)**, выполненные в рамках обучения в колледже. 

Каждый проект представляет собой законченный pipeline: от сбора и очистки данных до построения моделей и создания полноценного приложения.

---

##  Структура репозитория и семестры

> **Примечание о нейме:** 
> Исторически папки в репозитории названы по номерам семестров. В будущем планируется их переименование для большей прозрачности, но пока навигация выглядит следующим образом:

* 📁 **`1semestr`** — Проекты за **6 семестр** *(2-й семестр 3-го курса, весенний)*.
* 📁 **`2semestr`** — Проекты за **7 семестр** *(1-й семестр 4-го курса, осенний)*.

---

## Проекты

# 🎬 Movie Recommendation System

**Система рекомендаций фильмов** на основе MovieLens Small Dataset. Веб-приложение с FastAPI-бэкендом, MySQL-базой и Streamlit-интерфейсом.

---

## Быстрая навигация для преподавателя

| Что нужно найти | Куда смотреть |
|---|---|
| Задание на проект | [`Задание по РС2.pdf`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/Задание%20по%20РС2.pdf) |
| Исследование данных, очистка, обучение моделей | [`notebooks/movie_recommendation.ipynb`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/notebooks/) |
| Исходный код интерфейса приложения | [`app/main.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/app/main.py) |
| Исходный код API (бэкенд) | [`api/main.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/api/main.py) |
| Логика рекомендательных моделей | [`api/recommender.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/api/recommender.py) |
| Файлы базы данных MySQL | [`database/`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/database/) |
| Исходные датасеты с Kaggle | [`data/`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/data/) |
| Готовые таблицы с результатами | Корень проекта (`.csv`) |
| Зависимости проекта | [`requirements.txt`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/requirements.txt) |

---

## Стек технологий

| Слой | Технология |
|---|---|
| Интерфейс | **Streamlit** |
| Бэкенд / API | **FastAPI** |
| База данных | **MySQL** |

---

## 📁 Структура проекта

```
2semestr/
└── Movie Recommendation System/
    └── Recommendation3Last/
        │
        ├── 📁 api/                  ← Бэкенд на FastAPI
        │   ├── __init__.py
        │   ├── main.py              ← Роуты и запуск API
        │   └── recommender.py       ← Логика рекомендательных моделей
        │
        ├── 📁 app/                  ← Frontend на Streamlit
        │   ├── pic/                 ← Изображения приложения
        │   └── main.py              ← Главный файл интерфейса
        │
        ├── 📁 data/                 ← Сырые данные с Kaggle + README
        ├── 📁 database/             ← Файлы MySQL-базы
        ├── 📁 notebooks/            ← Jupyter-ноутбук с исследованием
        │   └── movie_recommendation.ipynb
        │
        ├── 📄 requirements.txt      ← Зависимости проекта
        ├── 📊 popular_movies.csv           ← Топ популярных фильмов
        ├── 📊 similar_movies.csv           ← Таблица похожих фильмов
        ├── 📊 user_recommendations.csv     ← Персональные рекомендации
        ├── 📦 archive.zip                  ← Архив исходных данных
        └── 📄 Задание по РС2.pdf           ← Текст задания
```

---

## Подробное описание папок

### `api/` — Бэкенд FastAPI

Серверная часть приложения. Содержит два ключевых файла:

**[`api/main.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/api/main.py)** — роуты и запуск API:

| Метод | Эндпоинт | Что делает |
|---|---|---|
| `GET` | `/api/status` | Статус API: кол-во фильмов и оценок |
| `GET` | `/api/movies/popular?limit=10` | Топ популярных фильмов (Weighted Rating) |
| `GET` | `/api/recommendations/{user_id}?method=user\|item\|content` | Персональные рекомендации |
| `GET` | `/api/recommendations/content/{movie_id}` | Похожие фильмы по содержанию |
| `GET` | `/api/movies/search?title=...` | Поиск фильма по названию |
| `POST` | `/api/ratings` | Сохранение оценки пользователя в БД |
| `GET` | `/api/users/{user_id}/ratings` | История оценок пользователя |
| `GET` | `/api/help` | Справка по API |

**[`api/recommender.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/api/recommender.py)** — реализация алгоритмов рекомендаций (Weighted Rating, User-Based CF, Item-Based CF, Content-Based).

> Интерактивная документация Swagger доступна по адресу: `http://127.0.0.1:8000/docs`

---

### `app/` — Интерфейс Streamlit

Клиентская часть — то, что видит пользователь.

**[`app/main.py`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/app/main.py)** — главный файл приложения.

**[`app/pic/`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/app/pic/)** — папка с изображениями (иконка приложения и др.).

**Вкладки приложения:**
1. **Популярные** — топ-10 фильмов по взвешенному рейтингу
2. **Рекомендации** — персональная подборка (User-Based / Item-Based / Content-Based)
3. **По содержанию** — похожие фильмы по жанрам (TF-IDF + косинусное сходство)
4. **Оценить фильм** — поиск фильма и выставление оценки (сохраняется в MySQL)
5. **Справка** — описание приложения, моделей и полей

---

### `data/` — Исходные данные

[`data/`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/data/) — скачанные с Kaggle датасеты **MovieLens Small Latest Dataset** с описанием в `README.md`.

---

### `database/` — База данных MySQL

[`database/`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/database/) — файлы, связанные с базой данных (SQL-скрипты создания таблиц, дамп БД).

**Структура БД** (основные таблицы):
- `movies` — фильмы (movieId, title, genres)
- `ratings` — оценки пользователей (userId, movieId, rating, timestamp)
- `users` — пользователи

---

### `notebooks/` — Исследование и ML

**[`notebooks/movie_recommendation.ipynb`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/notebooks/movie_recommendation.ipynb)** — Jupyter Notebook с полным циклом:
1. Загрузка и исследование данных (EDA)
2. Очистка и предобработка
3. Обучение моделей
4. Оценка качества (MAE, RMSE)
5. Создание моделей рекомендаций

**Реализованные алгоритмы:**
| Модель | Подход | Метрика |
|---|---|---|
| **Weighted Rating** | Статистический | — |
| **User-Based CF** | Коллаборативная фильтрация | MAE, RMSE |
| **Item-Based CF** | Коллаборативная фильтрация | MAE, RMSE |
| **Content-Based** | TF-IDF + косинусное сходство | MAE, RMSE |

---

## Файлы в корне проекта

| Файл | Назначение |
|---|---|
| [`requirements.txt`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/requirements.txt) | Список Python-зависимостей (`pip install -r requirements.txt`) |
| [`popular_movies.csv`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/popular_movies.csv) | Готовая таблица топ-10 популярных фильмов |
| [`similar_movies.csv`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/similar_movies.csv) | Таблица пар похожих фильмов (Item-Based) |
| [`user_recommendations.csv`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/user_recommendations.csv) | Таблица персональных рекомендаций для пользователей |
| [`archive.zip`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/archive.zip) | Архив с исходными сырыми данными с Kaggle |
| [`Задание по РС2.pdf`](./2semestr/Movie%20Recommendation%20System/Recommendation3Last/Задание%20по%20РС2.pdf) | Текст задания на расчётно-семестровую работу |

---

## Как запустить

### 1. Установка зависимостей
```bash
pip install -r 2semestr/Movie\ Recommendation\ System/Recommendation3Last/requirements.txt
```

### 2. Настройка `.env`
Создайте файл `.env` в папке `Recommendation3Last/` с данными для подключения к MySQL:
```
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=movie_recommendations
API_PORT=8000
```

### 3. Запуск API (бэкенд)
```bash
cd 2semestr/Movie\ Recommendation\ System/Recommendation3Last/api
uvicorn main:app --reload
```
API будет доступен по адресу: `http://127.0.0.1:8000`

### 4. Запуск приложения (фронтенд)
```bash
cd 2semestr/Movie\ Recommendation\ System/Recommendation3Last/app
streamlit run main.py
```
Приложение откроется в браузере по адресу: `http://localhost:8501`

---

## Ссылки

- [Датасет MovieLens Small на Kaggle](https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset)

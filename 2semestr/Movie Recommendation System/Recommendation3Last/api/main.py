
import os
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from api.recommender import MovieRecommender


load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "movie_recommendation")

db_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={"charset": "utf8mb4"}
)

engine = create_engine(
    db_url,
    pool_pre_ping=True
)


def load_data():
    with engine.connect() as connection:
        movies = pd.read_sql(
            text("""
                SELECT movieId, title, genres
                FROM movies
            """),
            connection
        )

        ratings = pd.read_sql(
            text("""
                SELECT userId, movieId, rating
                FROM ratings
            """),
            connection
        )

    movies["movieId"] = movies["movieId"].astype(int)
    ratings["userId"] = ratings["userId"].astype(int)
    ratings["movieId"] = ratings["movieId"].astype(int)

    return movies, ratings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        movies, ratings = load_data()

        # Модель создаётся один раз при запуске API
        app.state.recommender = MovieRecommender(
            movies,
            ratings
        )

        app.state.ready = True

        print("Модель рекомендаций успешно загружена.")
        print(f"Фильмов: {len(movies)}")
        print(f"Оценок: {len(ratings)}")

    except Exception as error:
        app.state.ready = False
        print(f"Ошибка загрузки данных: {error}")
        raise

    yield

    engine.dispose()


app = FastAPI(
    title="Movie Recommendation API",
    description="API рекомендательной системы фильмов MovieLens",
    version="1.0.0",
    lifespan=lifespan
)


def get_model():
    if not getattr(app.state, "ready", False):
        raise HTTPException(
            status_code=503,
            detail="Модель рекомендаций не загружена"
        )

    return app.state.recommender


def clean_records(records):
    # Преобразуем numpy-типы в обычные Python-типы для JSON
    return [
        {
            key: (
                value.item()
                if hasattr(value, "item")
                else value
            )
            for key, value in record.items()
        }
        for record in records
    ]


class RatingRequest(BaseModel):
    userId: int = Field(gt=0)
    movieId: int = Field(gt=0)
    rating: float = Field(ge=0.5, le=5)


@app.get("/")
def home():
    return {
        "message": "Movie Recommendation API is running",
        "version": "1.0.0"
    }


@app.get("/api/status")
def status():
    model = get_model()

    return {
        "status": "ready",
        "movies": len(model.movies),
        "ratings": len(model.ratings)
    }


@app.get("/api/help")
def help_api():
    return {
        "application": "Movie Recommendation System",
        "version": "1.0.0",
        "description": (
            "Система рекомендаций фильмов на основе данных MovieLens."
        ),
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/movies/popular",
                "parameters": "limit",
                "description": "Топ популярных фильмов"
            },
            {
                "method": "GET",
                "path": "/api/recommendations/{user_id}",
                "parameters": "method=user|item|content, limit",
                "description": "Персональные рекомендации"
            },
            {
                "method": "GET",
                "path": "/api/recommendations/content/{movie_id}",
                "parameters": "limit",
                "description": "Похожие по жанрам фильмы"
            },
            {
                "method": "GET",
                "path": "/api/movies/search",
                "parameters": "title",
                "description": "Поиск фильмов по названию"
            },
            {
                "method": "POST",
                "path": "/api/ratings",
                "parameters": "userId, movieId, rating",
                "description": "Сохранение оценки фильма"
            },
            {
                "method": "GET",
                "path": "/api/users/{user_id}/ratings",
                "parameters": "user_id",
                "description": "Оценки выбранного пользователя"
            }
        ]
    }


@app.get("/api/movies/popular")
def popular_movies(
    limit: int = Query(default=10, ge=1, le=100)
):
    model = get_model()

    return {
        "recommendations": clean_records(
            model.popular_movies(limit)
        )
    }


@app.get("/api/movies/search")
def search_movies(
    title: str = Query(min_length=1, max_length=200)
):
    model = get_model()

    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Введите название фильма"
        )

    result = model.movies[
        model.movies["title"].str.contains(
            title,
            case=False,
            na=False,
            regex=False
        )
    ].head(100)

    return {
        "movies": clean_records(
            result[
                ["movieId", "title", "genres"]
            ].to_dict("records")
        )
    }


@app.get("/api/movies/{movie_id}")
def movie_details(movie_id: int):
    model = get_model()

    result = model.movies[
        model.movies["movieId"] == movie_id
    ]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="Фильм не найден"
        )

    return clean_records(
        result.to_dict("records")
    )[0]


@app.get("/api/recommendations/content/{movie_id}")
def content_recommendations(
    movie_id: int,
    limit: int = Query(default=10, ge=1, le=100)
):
    model = get_model()

    if movie_id not in model.movie_index:
        raise HTTPException(
            status_code=404,
            detail="Фильм не найден"
        )

    return {
        "method": "content",
        "source_movie": movie_id,
        "recommendations": clean_records(
            model.content_for_movie(movie_id, limit)
        )
    }


@app.get("/api/recommendations/{user_id}")
def recommendations(
    user_id: int,
    method: str = Query(
        default="user",
        pattern="^(user|item|content)$"
    ),
    limit: int = Query(default=10, ge=1, le=100)
):
    model = get_model()

    if user_id not in model.user_ids:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    if method == "user":
        result = model.user_based(user_id, limit)

    elif method == "item":
        result = model.item_based(user_id, limit)

    else:
        result = model.content_for_user(user_id, limit)

    return {
        "userId": user_id,
        "method": method,
        "recommendations": clean_records(result)
    }



@app.get("/api/users/{user_id}/ratings")
def user_ratings(user_id: int):
    model = get_model()

    if user_id not in model.user_ids:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    result = model.ratings[
        model.ratings["userId"] == user_id
    ].merge(
        model.movies,
        on="movieId",
        how="left"
    )

    result = result[
        ["movieId", "title", "genres", "rating"]
    ].sort_values(
        "rating",
        ascending=False
    )

    return {
        "userId": user_id,
        "total_ratings": int(len(result)),
        "average_rating": round(
            float(result["rating"].mean()), 2
        ) if not result.empty else 0,
        "ratings": clean_records(
            result.to_dict("records")
        )
    }



@app.post("/api/ratings")
def save_rating(data: RatingRequest):
    model = get_model()

    if data.rating * 2 != int(data.rating * 2):
        raise HTTPException(
            status_code=400,
            detail="Оценка должна быть кратна 0.5"
        )

    if data.userId not in model.user_ids:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    if data.movieId not in model.movie_index:
        raise HTTPException(
            status_code=404,
            detail="Фильм не найден"
        )

    try:
        with engine.begin() as connection:
            existing = connection.execute(
                text("""
                    SELECT ratingId
                    FROM ratings
                    WHERE userId = :user_id
                    AND movieId = :movie_id
                """),
                {
                    "user_id": data.userId,
                    "movie_id": data.movieId
                }
            ).fetchall()

            if existing:
                connection.execute(
                    text("""
                        UPDATE ratings
                        SET rating = :rating
                        WHERE userId = :user_id
                        AND movieId = :movie_id
                    """),
                    {
                        "rating": data.rating,
                        "user_id": data.userId,
                        "movie_id": data.movieId
                    }
                )
                action = "updated"

            else:
                connection.execute(
                    text("""
                        INSERT INTO ratings
                        (userId, movieId, rating, timestamp)
                        VALUES
                        (:user_id, :movie_id, :rating, NOW())
                    """),
                    {
                        "user_id": data.userId,
                        "movie_id": data.movieId,
                        "rating": data.rating
                    }
                )
                action = "created"

        # Обновляем данные работающей модели
        model.update_rating(
            data.userId,
            data.movieId,
            data.rating
        )

        return {
            "status": "success",
            "action": action,
            "userId": data.userId,
            "movieId": data.movieId,
            "rating": data.rating,
            "message": "Оценка сохранена в базе данных"
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сохранения оценки: {str(error)}"
        )

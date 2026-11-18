
import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class MovieRecommender:

    def __init__(self, movies, ratings):
        self.movies = movies.copy()
        self.ratings = ratings.copy()

        self.movies["genres"] = (
            self.movies["genres"].fillna("").astype(str)
        )

        self.ratings["rating"] = pd.to_numeric(
            self.ratings["rating"], errors="coerce"
        )
        self.ratings = self.ratings.dropna(
            subset=["userId", "movieId", "rating"]
        )

        self.build_models()

    def build_models(self):
        # Матрица пользователь-фильм
        self.user_movie = self.ratings.pivot_table(
            index="userId",
            columns="movieId",
            values="rating",
            aggfunc="mean"
        ).fillna(0)

        # Сходство пользователей
        self.user_similarity = cosine_similarity(
            self.user_movie
        )

        # Сходство фильмов
        self.item_similarity = cosine_similarity(
            self.user_movie.T
        )

        self.user_ids = list(self.user_movie.index)
        self.movie_ids = list(self.user_movie.columns)

        # TF-IDF по жанрам
        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b\w+\b"
        )

        self.content_matrix = self.vectorizer.fit_transform(
            self.movies["genres"].str.replace(
                "|", " ", regex=False
            )
        )

        self.movie_index = {
            int(movie_id): index
            for index, movie_id in enumerate(
                self.movies["movieId"]
            )
        }

    def update_rating(self, user_id, movie_id, rating):
        # Обновляем данные в памяти после сохранения оценки в БД
        mask = (
            (self.ratings["userId"] == user_id) &
            (self.ratings["movieId"] == movie_id)
        )

        if mask.any():
            self.ratings.loc[mask, "rating"] = rating
        else:
            new_row = pd.DataFrame([{
                "userId": user_id,
                "movieId": movie_id,
                "rating": rating
            }])
            self.ratings = pd.concat(
                [self.ratings, new_row],
                ignore_index=True
            )

        # Пересчитываем матрицы, сохраняя сам объект модели
        self.build_models()

    def popular_movies(self, limit=10):
        stats = self.ratings.groupby("movieId").agg(
            avg_rating=("rating", "mean"),
            rating_count=("rating", "count")
        ).reset_index()

        global_mean = self.ratings["rating"].mean()
        minimum_votes = 50

        stats["weighted_rating"] = (
            stats["rating_count"] /
            (stats["rating_count"] + minimum_votes)
        ) * stats["avg_rating"] + (
            minimum_votes /
            (stats["rating_count"] + minimum_votes)
        ) * global_mean

        result = stats.merge(
            self.movies,
            on="movieId",
            how="left"
        )

        result = result.sort_values(
            "weighted_rating",
            ascending=False
        ).head(limit)

        return result.to_dict("records")

    def user_based(self, user_id, limit=10):
        if user_id not in self.user_ids:
            return []

        user_index = self.user_ids.index(user_id)
        similarities = self.user_similarity[user_index]

        user_ratings = self.user_movie.iloc[user_index]
        rated_movies = set(
            user_ratings[user_ratings > 0].index
        )

        scores = np.zeros(len(self.movie_ids))

        for other_index, similarity in enumerate(similarities):
            if other_index == user_index or similarity <= 0:
                continue

            other_ratings = self.user_movie.iloc[other_index].values
            scores += similarity * other_ratings

        result = pd.DataFrame({
            "movieId": self.movie_ids,
            "score": scores
        })

        result = result[
            ~result["movieId"].isin(rated_movies)
        ]

        result = result.sort_values(
            "score",
            ascending=False
        ).head(limit)

        return self.add_movie_info(result)

    def item_based(self, user_id, limit=10):
        if user_id not in self.user_ids:
            return []

        user_index = self.user_ids.index(user_id)
        user_ratings = self.user_movie.iloc[user_index].values

        rated_indices = np.where(user_ratings > 0)[0]

        if len(rated_indices) == 0:
            return []

        scores = np.zeros(len(self.movie_ids))

        for movie_index in range(len(self.movie_ids)):
            similarities = self.item_similarity[
                movie_index, rated_indices
            ]
            scores[movie_index] = np.dot(
                similarities,
                user_ratings[rated_indices]
            ) / (np.abs(similarities).sum() + 1e-9)

        result = pd.DataFrame({
            "movieId": self.movie_ids,
            "score": scores
        })

        rated_movie_ids = set(
            self.user_movie.columns[
                user_ratings > 0
            ]
        )

        result = result[
            ~result["movieId"].isin(rated_movie_ids)
        ]

        result = result.sort_values(
            "score",
            ascending=False
        ).head(limit)

        return self.add_movie_info(result)

    def content_for_movie(self, movie_id, limit=10):
        if movie_id not in self.movie_index:
            return []

        index = self.movie_index[movie_id]

        similarities = cosine_similarity(
            self.content_matrix[index],
            self.content_matrix
        ).flatten()

        result = self.movies.copy()
        result["similarity"] = similarities

        result = result[
            result["movieId"] != movie_id
        ]

        result = result.sort_values(
            "similarity",
            ascending=False
        ).head(limit)

        return result[
            ["movieId", "title", "genres", "similarity"]
        ].to_dict("records")

    def content_for_user(self, user_id, limit=10):
        if user_id not in self.user_ids:
            return []

        user_ratings = self.user_movie.loc[user_id]
        liked_ids = user_ratings[
            user_ratings >= 4
        ].index.tolist()

        if not liked_ids:
            return self.popular_movies(limit)

        liked_indices = [
            self.movie_index[int(movie_id)]
            for movie_id in liked_ids
            if int(movie_id) in self.movie_index
        ]

        if not liked_indices:
            return self.popular_movies(limit)

        weights = np.array([
            float(user_ratings.iloc[
                self.user_movie.columns.get_loc(movie_id)
            ])
            for movie_id in liked_ids
            if int(movie_id) in self.movie_index
        ])

        profile = self.content_matrix[liked_indices].multiply(
            weights.reshape(-1, 1)
        ).mean(axis=0)

        similarities = cosine_similarity(
            np.asarray(profile),
            self.content_matrix
        ).flatten()

        result = self.movies.copy()
        result["similarity"] = similarities

        rated_ids = set(
            user_ratings[user_ratings > 0].index
        )

        result = result[
            ~result["movieId"].isin(rated_ids)
        ]

        result = result.sort_values(
            "similarity",
            ascending=False
        ).head(limit)

        return result[
            ["movieId", "title", "genres", "similarity"]
        ].to_dict("records")

    def add_movie_info(self, result):
        result["movieId"] = result["movieId"].astype(int)

        result = result.merge(
            self.movies,
            on="movieId",
            how="left"
        )

        return result[
            ["movieId", "title", "genres", "score"]
        ].to_dict("records")

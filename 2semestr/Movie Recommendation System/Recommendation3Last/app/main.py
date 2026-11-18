import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="app\\pic\\bleehh _P.jpg",
    layout="wide"
)



def api_get(endpoint, params=None):
    try:
        response = requests.get(
            API_URL + endpoint,
            params=params,
            timeout=60
        )

        if response.status_code == 404:
            try:
                detail = response.json().get(
                    "detail", "Данные не найдены"
                )
            except ValueError:
                detail = "Данные не найдены"

            st.warning(detail)
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "Не удалось подключиться к API. "
            "Проверьте, запущен ли FastAPI."
        )
    except requests.exceptions.Timeout:
        st.error("Сервер не ответил за отведённое время.")
    except requests.exceptions.HTTPError as error:
        try:
            detail = response.json().get("detail", str(error))
        except ValueError:
            detail = str(error)

        st.error(f"Ошибка API: {detail}")
    except requests.exceptions.RequestException as error:
        st.error(f"Ошибка запроса: {error}")

    return None


def api_post(endpoint, data):
    try:
        response = requests.post(
            API_URL + endpoint,
            json=data,
            timeout=60
        )

        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "detail", "Неизвестная ошибка"
                )
            except ValueError:
                detail = response.text

            st.error(f"Ошибка: {detail}")
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к API.")
    except requests.exceptions.Timeout:
        st.error("Превышено время ожидания ответа.")
    except requests.exceptions.RequestException as error:
        st.error(f"Ошибка запроса: {error}")

    return None


def show_movies(data, key="recommendations"):
    if not data:
        st.info("Список фильмов пуст.")
        return

    records = data.get(key, [])

    if not records:
        st.info("Рекомендации не найдены")
        return

    df = pd.DataFrame(records)

    if "movieId" in df.columns:
        df = df.rename(columns={"movieId": "ID фильма"})

    if "title" in df.columns:
        df = df.rename(columns={"title": "Название"})

    if "genres" in df.columns:
        df = df.rename(columns={"genres": "Жанры"})

    if "weighted_rating" in df.columns:
        df = df.rename(
            columns={"weighted_rating": "Взвешенный рейтинг"}
        )

    if "avg_rating" in df.columns:
        df = df.rename(
            columns={"avg_rating": "Средняя оценка"}
        )

    if "rating_count" in df.columns:
        df = df.rename(
            columns={"rating_count": "Количество оценок"}
        )

    if "similarity" in df.columns:
        df = df.rename(columns={"similarity": "Сходство"})

    if "score" in df.columns:
        df = df.rename(columns={"score": "Оценка модели"})

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )



st.title("Movie Recommendation System")

st.write(
    "Система рекомендаций фильмов на основе "
    "MovieLens Small Dataset"
)

st.caption(
    "От создателя 44unTAG ( •̀ ω •́ )✧"
)

status = api_get("/api/status")

if status:
    st.success(
        f"API работает. Фильмов: {status['movies']}, "
        f"оценок: {status['ratings']}."
    )



tab_popular, tab_recommend, tab_content, tab_rating, tab_help = st.tabs([
    "Популярные",
    "Рекомендации",
    "По содержанию",
    "Оценить фильм",
    "Справка"
])



with tab_popular:
    st.header("*:･ﾟ✧Топ-10 популярных фильмов*:･ﾟ✧")

    st.write(
        "Популярность определяется с учётом средней оценки "
        "и количества пользовательских оценок."
    )

    if st.button("Показать популярные фильмы"):
        result = api_get(
            "/api/movies/popular",
            params={"limit": 10}
        )

        if result:
            show_movies(result)



with tab_recommend:
    st.header("✧*:･ﾟПерсональные рекомендации✧*:･ﾟ")

    st.write(
        "Выберите пользователя и метод формирования рекомендаций."
    )

    user_id = st.number_input(
        "ID пользователя",
        min_value=1,
        value=1,
        step=1,
        key="recommend_user"
    )

    method = st.selectbox(
        "Метод рекомендаций",
        options=["user", "item", "content"],
        format_func=lambda value: {
            "user": "По пользователям (User-Based CF)",
            "item": "По фильмам (Item-Based CF)",
            "content": "По содержанию (Content-Based)"
        }[value]
    )

    if st.button("Получить рекомендации"):
        result = api_get(
            f"/api/recommendations/{user_id}",
            params={
                "method": method,
                "limit": 10
            }
        )

        if result:
            st.subheader("Рекомендованные фильмы")
            show_movies(result)



with tab_content:
    st.header("☆*:.｡Рекомендации по содержанию｡.:*☆")

    st.write(
        "Система сравнивает жанры выбранного фильма "
        "с жанрами остальных фильмов."
    )

    movie_id = st.number_input(
        "ID исходного фильма",
        min_value=1,
        value=1,
        step=1,
        key="content_movie"
    )

    if st.button("Найти 10 похожих фильмов"):
        result = api_get(
            f"/api/recommendations/content/{movie_id}",
            params={"limit": 10}
        )

        if result:
            st.subheader("Похожие фильмы")
            show_movies(result)




with tab_rating:
    st.header("d=====(￣▽￣*)b Оценки пользователя")

    rating_user = st.number_input(
        "ID пользователя",
        min_value=1,
        value=1,
        step=1,
        key="rating_user"
    )

    st.divider()

    st.subheader("Найти фильм и поставить оценку")

    search_title = st.text_input(
        "Название фильма",
        placeholder="Например, Toy Story",
        key="rating_search"
    )

    if st.button("Найти фильм", key="search_rating_movie"):
        if not search_title.strip():
            st.warning("Введите название фильма.")
        else:
            result = api_get(
                "/api/movies/search",
                params={"title": search_title.strip()}
            )

            if result:
                st.session_state["found_movies"] = (
                    result.get("movies", [])
                )

    found_movies = st.session_state.get(
        "found_movies", []
    )

    selected_movie = None

    if found_movies:
        movie_options = {
            f"{movie['title']} (ID: {movie['movieId']})": movie
            for movie in found_movies
        }

        selected_title = st.selectbox(
            "Выберите фильм",
            options=list(movie_options.keys()),
            key="selected_rating_movie"
        )

        selected_movie = movie_options[selected_title]

        st.write("Жанры:", selected_movie["genres"])
        st.write("ID фильма:", selected_movie["movieId"])

        rating_value = st.select_slider(
            "Ваша оценка",
            options=[
                0.5, 1.0, 1.5, 2.0, 2.5,
                3.0, 3.5, 4.0, 4.5, 5.0
            ],
            value=5.0,
            key="rating_value"
        )

        if st.button(
            "Сохранить оценку в MySQL",
            key="save_rating"
        ):
            result = api_post(
                "/api/ratings",
                {
                    "userId": int(rating_user),
                    "movieId": int(selected_movie["movieId"]),
                    "rating": float(rating_value)
                }
            )

            if result:
                st.success(
                    f"Оценка {rating_value} успешно сохранена!"
                )

                # Сбрасываем кэш истории оценок
                st.session_state.pop("user_ratings", None)

                st.rerun()

    st.divider()

    st.subheader("(✿◡‿◡) Мои оценки")

    if st.button(
        "Показать / обновить мои оценки",
        key="load_my_ratings"
    ):
        result = api_get(
            f"/api/users/{int(rating_user)}/ratings"
        )

        if result is not None:
            st.session_state["user_ratings"] = result

    history = st.session_state.get("user_ratings")

    if history and history.get("userId") == int(rating_user):

        ratings = history.get("ratings", [])

        if ratings:
            history_df = pd.DataFrame(ratings)

            history_df = history_df.rename(
                columns={
                    "movieId": "ID фильма",
                    "title": "Название фильма",
                    "genres": "Жанры",
                    "rating": "Моя оценка"
                }
            )

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("У этого пользователя пока нет оценок.")

    elif history:
        st.info(
            "Нажмите «Показать / обновить мои оценки» "
            "для выбранного пользователя."
        )


with tab_help:
    st.header("✧(｡•̀ᴗ-)✧Справка по приложению")

    st.subheader("1. Назначение приложения")

    st.write(
        """
        Movie Recommendation System — приложение для подбора фильмов
        на основе данных MovieLens Small Dataset.

        Система позволяет:
        - просматривать топ-10 популярных фильмов;
        - получать персональные рекомендации;
        - использовать коллаборативную фильтрацию по пользователям;
        - использовать коллаборативную фильтрацию по фильмам;
        - получать рекомендации по жанрам;
        - искать фильмы и выставлять оценки;
        - сохранять пользовательские оценки в MySQL.
        """
    )

    st.subheader("2. Как пользоваться приложением")

    st.write(
        """
        1. Откройте вкладку «Популярные» и загрузите топ-10.
        2. В разделе «Рекомендации» укажите ID пользователя
           и выберите алгоритм.
        3. В разделе «По содержанию» введите ID фильма.
        4. В разделе «Оценить фильм» найдите фильм по названию,
           выберите его и укажите оценку.
        5. Откройте вкладку Help для просмотра справочной информации.
        """
    )

    st.subheader("3. Описание входных полей")

    fields = pd.DataFrame([
        ["User ID", "Уникальный идентификатор пользователя"],
        ["Movie ID", "Уникальный идентификатор фильма"],
        ["Title", "Название фильма"],
        ["Genres", "Жанры фильма из MovieLens"],
        ["Rating", "Оценка пользователя от 0.5 до 5"],
        ["Method", "Алгоритм: user, item или content"],
        ["Similarity", "Косинусное сходство от 0 до 1"],
        ["Limit", "Количество возвращаемых рекомендаций"]
    ], columns=["Поле", "Описание"])

    st.dataframe(
        fields,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("4. Используемые модели")

    st.markdown(
        """
        **Weighted Rating**

        Рассчитывает взвешенный рейтинг фильма. Учитывает среднюю
        оценку и количество оценок, чтобы фильмы с малым числом
        оценок не получали неоправданно высокий рейтинг.

        **User-Based Collaborative Filtering**

        Находит пользователей с похожими предпочтениями
        с помощью косинусного сходства и использует их оценки
        для формирования рекомендаций.

        **Item-Based Collaborative Filtering**

        Определяет сходство фильмов на основе оценок пользователей
        и предлагает фильмы, похожие на уже оценённые.

        **Content-Based Filtering**

        Использует TF-IDF и косинусное сходство для сравнения жанров.
        Для персональной подборки учитывает жанры фильмов,
        которые пользователь оценил высоко.
        """
    )

    st.subheader("5. Ограничения моделей")

    st.write(
        """
        - Используется MovieLens Small: 610 пользователей и 9742 фильма.
        - У новых пользователей может не быть истории оценок.
        - Для новых фильмов может быть недостаточно оценок.
        - Контентная модель использует только жанры, а не сюжет,
          актёров, режиссёров или описания фильмов.
        - Рекомендации зависят от полноты и качества исходных оценок.
        - Косинусное сходство показывает близость предпочтений,
          но не гарантирует, что фильм понравится пользователю.
        """
    )

    st.subheader("6. Оценка качества")

    st.write(
        """
        Для оценки прогнозирования рейтингов используются
        MAE и RMSE. Чем меньше значения этих метрик,
        тем меньше средняя ошибка предсказания.

        Фактические результаты MAE и RMSE необходимо внести
        из экспериментов в исследовательском ноутбуке.
        """
    )

    st.subheader("7. Технологии")

    st.write(
        """
        - Python
        - Streamlit — графический интерфейс
        - FastAPI — API
        - MySQL — база данных
        - Pandas и NumPy — обработка данных
        - Scikit-learn — алгоритмы машинного обучения
        """
    )

    st.subheader("8. Авторство и версия")

    st.write("Название: Movie Recommendation System")
    st.write("Версия: 1.0")
    st.write("Автор: укажите своё имя и фамилию")
    st.write("Источник данных: MovieLens Small Latest Dataset")

    st.subheader("9. Справка по API")

    if st.button("Загрузить список API-команд"):
        result = api_get("/api/help")

        if result:
            st.json(result)

    st.markdown(
        f"[Открыть интерактивную документацию FastAPI]({API_URL}/docs)"
    )

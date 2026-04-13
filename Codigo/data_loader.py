import pandas as pd


def cargar_all_users(ruta="ratings.csv"):
    df = pd.read_csv(ruta)

    all_users = {}

    for _, row in df.iterrows():
        user = int(row["userId"])
        movie = int(row["movieId"])
        rating = row["rating"]

        if user not in all_users:
            all_users[user] = {}

        all_users[user][movie] = rating

    return all_users


# ==============================
# 🎬 NUEVO: MAPA DE PELÍCULAS
# ==============================
def cargar_movies(ruta="movies.csv"):
    df = pd.read_csv(ruta)

    # movieId -> title
    return df.set_index("movieId")[["title", "genres"]].to_dict("index")
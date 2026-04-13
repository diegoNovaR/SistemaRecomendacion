from Codigo.data_loader import cargar_all_users
from Codigo.Knn import knn
import pandas as pd


# ==============================
# cargar movies
# ==============================
def cargar_movies(ruta="movies.csv"):
    df = pd.read_csv(ruta)

    # movieId -> {title, genres}
    return df.set_index("movieId")[["title", "genres"]].to_dict("index")


# ==============================
# géneros del usuario objetivo
# ==============================
def obtener_generos_usuario(user_id, all_users, movies):

    generos = {}

    for movie_id in all_users[user_id].keys():

        if movie_id in movies:
            lista = movies[movie_id]["genres"].split("|")

            for g in lista:
                generos[g] = generos.get(g, 0) + 1

    return generos


# ==============================
# INFLUENCER RECOMMENDER
# ==============================
def ranking_influencer(user_id, all_users, vecinos, movies):

    vistos = set(all_users[user_id].keys())

    generos_usuario = obtener_generos_usuario(user_id, all_users, movies)

    scores = {}

    for vecino_id, similitud in vecinos:

        perfil_vecino = all_users[vecino_id]

        for movie_id, rating in perfil_vecino.items():

            #no recomendar lo ya visto
            if movie_id in vistos:
                continue

            if movie_id not in movies:
                continue

            #género (solo refuerzo, NO filtro)
            generos_peli = movies[movie_id]["genres"].split("|")

            coincide_genero = any(g in generos_usuario for g in generos_peli)

            #factor de refuerzo
            factor_genero = 1.3 if coincide_genero else 1.0

            #score de influencia
            aporte = similitud * rating * factor_genero

            if movie_id not in scores:
                scores[movie_id] = {
                    "total": 0,
                    "fuentes": []
                }

            scores[movie_id]["total"] += aporte
            scores[movie_id]["fuentes"].append((vecino_id, round(aporte, 3)))

    # ordenar ranking
    ranking = sorted(scores.items(), key=lambda x: x[1]["total"], reverse=True)

    return ranking


# ==============================
# MAIN
# ==============================
def menu_influencer():

    all_users = cargar_all_users("ratings.csv")
    movies = cargar_movies("movies.csv")

    print("\n===== SISTEMA INFLUENCER (GEMELOS + DIFERENCIAS) =====")
    print("Usuarios disponibles:", list(all_users.keys()))

    user_id = int(input("Usuario objetivo: "))

    #vecinos (pueden ser distancia 0 = gemelos)
    vecinos = knn(user_id, all_users, k=5, metrica="coseno")

    print("\n===== TOP RECOMENDACIONES =====\n")

    ranking = ranking_influencer(user_id, all_users, vecinos, movies)

    for i, (movie_id, data) in enumerate(ranking[:10], start=1):

        titulo = movies[movie_id]["title"]

        print(f"{i}. {titulo}")
        print(f" Score de influencia: {round(data['total'], 3)}")

        print(" Aportes de usuarios similares:")
        for vecino_id, aporte in data["fuentes"]:
            print(f"      - Usuario {vecino_id} → {aporte}")

        print()


# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    menu_influencer()
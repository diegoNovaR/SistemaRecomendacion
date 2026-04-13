import pandas as pd 
from Knn import knn
from recomendacion import recomendacion

def cargar_datos(ruta_ratings, ruta_movies):

    df_ratings = pd.read_csv(ruta_ratings)
    df_movies = pd.read_csv(ruta_movies)

    # 2. Reconstruir la matriz (Usuarios en filas, Películas en columnas)
    matriz = df_ratings.pivot(index='userId', columns='movieId', values='rating')
    
    # 3. Convertir a diccionario de diccionarios
    # Formato: {1: {1: 4.0, 3: 4.0, 6: 4.0}, 2: {...}}
    usuarios_dict = matriz.to_dict(orient='index')

    # 4. Crear mapa de nombres: {1: 'Toy Story (1995)', 2: 'Jumanji (1995)'}
    mapeo_nombres = dict(zip(df_movies['movieId'], df_movies['title']))

    return usuarios_dict, mapeo_nombres



def main():

    # Carga
    usuarios_dict, mapeo_nombres = cargar_datos("ratings.csv", "movies.csv")

    user_id = 1  # Probamos con el usuario 1
    k = 5       # Con 600 usuarios, podemos subir K a 10 o 20

    # 1. Encontrar vecinos (usando tu Knn.py y correlacion_person.py)
    vecinos = knn(user_id, usuarios_dict, k)

    print("vecinos mas cercanos")
    for valId in vecinos:
        print(f"{valId}")

    # 2. Generar recomendaciones (usando tu recomendador.py)
    # Importante: metrica_tipo='similitud' porque Pearson es similitud
    propuestas = recomendacion(user_id, usuarios_dict, vecinos)

    # 3. Mostrar resultados traducidos
    print(f"\nRecomendaciones para el Usuario {user_id}:")
    for movie_id, prediccion in propuestas[:10]: # Top 10
        titulo = mapeo_nombres.get(movie_id, f"Desconocida (ID:{movie_id})")
        print(f"- {titulo:50} | Predicción: {prediccion:.2f} estrellas")

if __name__ == "__main__":
    main()
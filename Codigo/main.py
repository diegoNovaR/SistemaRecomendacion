import pandas as pd 
from Knn import knn
from recomendacion import recomendacion

def cargar_datos(ruta_ratings, ruta_movies):
    print("Cargando datos...")
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

def menu_metricas():
    print("\n--- Selecciona la Métrica de Similitud ---")
    print("1. Correlación de Pearson")
    print("2. Similitud de Coseno")
    print("3. Distancia Manhattan")
    print("4. Distancia Euclidiana")
    opcion = input("Elige una opción (1-4): ")
    
    mapping = {
        '1': 'pearson',
        '2': 'coseno',
        '3': 'manhattan',
        '4': 'euclidiana'
    }
    return mapping.get(opcion, 'pearson')

def main():

    # Carga
    usuarios_dict, mapeo_nombres = cargar_datos("ratings.csv", "movies.csv")

    while True:
        print("\n==========================================")
        print("   SISTEMA DE RECOMENDACIÓN MOVIELENS")
        print("==========================================")
        
        try:
            user_id = int(input(f"\nIngresa el ID del usuario (1-{max(usuarios_dict.keys())}): "))
            if user_id not in usuarios_dict:
                print("Error: El ID de usuario no existe.")
                continue
        except ValueError:
            print("Por favor, ingresa un número válido.")
            continue

        # Selección de métrica
        metrica_elegida = menu_metricas()
        
        # Configuración de parámetros
        k = int(input("¿Cuántos vecinos quieres considerar? (Sugerido 10-20): ") or 10)
        min_v = int(input("Tolerancia mínima de vecinos que vieron la peli (Sugerido 3-5): ") or 3)

        print(f"\nProcesando con {metrica_elegida}...")

        # 1. Encontrar vecinos
        vecinos = knn(user_id, usuarios_dict, k, metrica=metrica_elegida)

        print("\n--- Vecinos más cercanos encontrados ---")
        for id_vecino, score in vecinos:
            print(f"ID: {id_vecino:4} | Similitud/Distancia: {score:.4f}")

        # 2. Generar recomendaciones
        # Pasamos la métrica para que el recomendador sepa si debe convertir distancia a peso
        propuestas = recomendacion(user_id, usuarios_dict, vecinos, min_vecinos=min_v, metrica=metrica_elegida)

        # 3. Mostrar resultados
        print(f"\nTop 10 recomendaciones para el Usuario {user_id}:")
        if not propuestas:
            print("No se encontraron recomendaciones con esos criterios. Intenta bajar la tolerancia.")
        else:
            for movie_id, prediccion in propuestas[:10]:
                titulo = mapeo_nombres.get(movie_id, f"Desconocida (ID:{movie_id})")
                print(f"- {titulo[:50]:50} | Predicción: {prediccion:.2f} ★")

        continuar = input("\n¿Deseas realizar otra consulta? (s/n): ").lower()
        if continuar != 's':
            break

if __name__ == "__main__":
    main()
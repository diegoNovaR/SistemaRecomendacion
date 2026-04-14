import pandas as pd 
from Knn import knn
from incluencer import items_populares, items_no_vistos, crear_influencer
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
        k = int(input("¿Cuántos vecinos quieres considerar que son similares que tú? (Sugerido 10-20): ") or 10)
        min_v = int(input("Elige la cantidad de vecinos mínima que vieron la película (Sugerido 3-5): ") or 3)

        print(f"\nProcesando con {metrica_elegida}...")

        # ==========================================
        # VECINOS
        # ==========================================

        # 1. Encontrar vecinos
        vecinos = knn(user_id, usuarios_dict, k, metrica=metrica_elegida)

        print("\n--- Vecinos más cercanos encontrados ---")
        for id_vecino, score in vecinos:
            print(f"ID: {id_vecino:4} | Similitud/Distancia: {score:.4f}")
        
        # ==========================================
        # RECOMENDACIONES SIN INFLUENCER
        # ==========================================

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
        
        # ==========================================
        # INFLUENCER
        # ==========================================

        #4. prueba con influencer.
        print("\n==========================================")
        print("   CONFIGURAR USUARIO INFLUENCER")
        print("==========================================")

        top_populares = int(input("¿Cuántas películas populares analizar? (ej: 20): ") or 20)
        num_no_vistos = int(input("¿Cuántas películas NO vistas agregar al influencer? (ej: 3): ") or 3)


        # ==========================================
        # CREAR INFLUENCER
        # ==========================================

        # Obtener populares
        populares = items_populares(usuarios_dict, top_n=top_populares)

        print(f"\n Top {top_populares} películas más populares:")
        for i, movie_id in enumerate(populares, 1):
            titulo = mapeo_nombres.get(movie_id, f"ID:{movie_id}")
            print(f"{i:2}. {titulo}")

        # Obtener no vistos
        no_vistos_populares = items_no_vistos(user_id, usuarios_dict, populares)

        print(f"\n Películas populares que el usuario {user_id} NO ha visto:")
        for i, movie_id in enumerate(no_vistos_populares, 1):
            titulo = mapeo_nombres.get(movie_id, f"ID:{movie_id}")
            print(f"{i:2}. {titulo}")

        # Control: si pide más de los disponibles
        if num_no_vistos > len(no_vistos_populares):
            num_no_vistos = len(no_vistos_populares)

        print(f"\n Se seleccionarán {num_no_vistos} películas no vistas.")

        nuevas_recomendaciones = no_vistos_populares[:num_no_vistos]

        print("\nPelículas que el influencer agregará:")
        for movie_id in nuevas_recomendaciones:
            print("-", mapeo_nombres.get(movie_id, movie_id))

        influencer = crear_influencer(user_id, usuarios_dict, nuevas_recomendaciones)

        # Insertar influencer
        usuarios_dict["influencer"] = influencer


        # ==========================================
        # PRUEBA CON INFLUENCER
        # ==========================================

        print("\n==========================================")
        print("   RESULTADOS CON INFLUENCER")
        print("==========================================")

        vecinos_inf = knn(user_id, usuarios_dict, k, metrica=metrica_elegida)

        print("\n--- Nuevos vecinos (con influencer) ---")
        for id_vecino, score in vecinos_inf:
            print(f"ID: {id_vecino:4} | Score: {score:.4f}")

        propuestas_con = recomendacion(user_id, usuarios_dict, vecinos_inf, min_vecinos=min_v, metrica=metrica_elegida)

        print(f"\nTop 10 recomendaciones CON influencer:")
        for movie_id, prediccion in propuestas_con[:10]:
            titulo = mapeo_nombres.get(movie_id, f"ID:{movie_id}")
            print(f"- {titulo[:50]:50} | {prediccion:.2f} ★")


        # ==========================================
        # COMPARACIÓN AUTOMÁTICA
        # ==========================================

        print("\n==========================================")
        print("   COMPARACIÓN")
        print("==========================================")

        top_sin = [x[0] for x in propuestas[:10]]
        top_con = [x[0] for x in propuestas_con[:10]]

        nuevas = set(top_con) - set(top_sin)

        if nuevas:
            print("\n Nuevas recomendaciones gracias al influencer:")
            for movie_id in nuevas:
                print("-", mapeo_nombres.get(movie_id, movie_id))
        else:
            print("\n No hubo nuevas recomendaciones, pero puede haber cambios en ranking.")


        print("\n Cambios de ranking (TOP 10):")
        ranking_sin = {item: i for i, item in enumerate(top_sin)}
        ranking_con = {item: i for i, item in enumerate(top_con)}

        for item in top_con:
            if item in ranking_sin:
                cambio = ranking_sin[item] - ranking_con[item]
                if cambio != 0:
                    print(f"- {mapeo_nombres.get(item,item)} | Cambio: {cambio}")


        #====== final ===#
        continuar = input("\n¿Deseas realizar otra consulta? (s/n): ").lower()
        if continuar != 's':
            break

if __name__ == "__main__":
    main()
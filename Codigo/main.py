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

#==CARGA ANTERIOR CON EXCEL B[ASICO]===#
# # Intentamos leer detectando el separador automáticamente
#     # engine='python' permite que sep=None funcione mejor
#     df = pd.read_csv(ruta, sep=None, engine='python', index_col=0)
    
#     # Limpiamos posibles espacios en blanco en los nombres de columnas y filas
#     df.index = df.index.str.strip()
#     df.columns = df.columns.str.strip()

#     # Transponemos: Ahora las columnas (Angelica, Bill...) son las filas (Índice)
#     df_transpuesto = df.transpose()
    
#     # Convertimos a diccionario
#     diccionario = df_transpuesto.to_dict(orient='index')
    
#     return diccionario




def main():

    usuarios_dict = cargar_datos("DatasetEjemplo.csv")
    print("Usuarios detectados:", list(usuarios_dict.keys()))
    usuario_objetivo = "Angelica"
    k = 5
    print(f"Calculando vecinos para {usuario_objetivo}...")

    vecinos = knn(usuario_objetivo, usuarios_dict, k)

    print(f"\nLos {k} usuarios más parecidos a {usuario_objetivo} son:")
    for nombre, score in vecinos:
        print(f"- {nombre}: {score:.4f}")
    #===========recomendacion=========#

    recomendaciones = recomendacion(usuario_objetivo, usuarios_dict, vecinos)
    
    print(f"\n las recomendaciones son:")
    for artista, prediccion in recomendaciones:
        print(f"- {artista}: {prediccion:.4f}")



if __name__ == "__main__":
    main()
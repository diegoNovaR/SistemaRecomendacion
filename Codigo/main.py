import pandas as pd 
from Knn import knn

def cargar_datos(ruta):

# Intentamos leer detectando el separador automáticamente
    # engine='python' permite que sep=None funcione mejor
    df = pd.read_csv(ruta, sep=None, engine='python', index_col=0)
    
    # Limpiamos posibles espacios en blanco en los nombres de columnas y filas
    df.index = df.index.str.strip()
    df.columns = df.columns.str.strip()

    # Transponemos: Ahora las columnas (Angelica, Bill...) son las filas (Índice)
    df_transpuesto = df.transpose()
    
    # Convertimos a diccionario
    diccionario = df_transpuesto.to_dict(orient='index')
    
    return diccionario

def main():

    usuarios_dict = cargar_datos("DatasetEjemplo.csv")
    print("Usuarios detectados:", list(usuarios_dict.keys()))
    usuario_objetivo = "Jordy"
    k = 5
    print(f"Calculando vecinos para {usuario_objetivo}...")

    vecinos = knn(usuario_objetivo, usuarios_dict, k)

    print(f"\nLos {k} usuarios más parecidos a {usuario_objetivo} son:")
    for nombre, score in vecinos:
        print(f"- {nombre}: {score:.4f}")

if __name__ == "__main__":
    main()
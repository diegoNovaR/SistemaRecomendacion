import pandas as pd 
from Knn import knn

def cargar_datos(ruta):

    # 1. Cargamos el archivo
    df = pd.read_csv(ruta, index_col=0)
    
    # 2. Limpiamos espacios en blanco en los nombres de las columnas y el índice
    df.columns = df.columns.str.strip()
    df.index = df.index.str.strip()
    
    # 3. Transponemos para que los usuarios sean las llaves principales
    df_transpuesto = df.transpose()
    
    # 4. También limpiamos el índice después de transponer (por si acaso)
    df_transpuesto.index = df_transpuesto.index.str.strip()
    
    return df_transpuesto.to_dict(orient='index')

def main():

    usuarios_dict = cargar_datos("DatasetEjemplo.csv")
    print("Usuarios detectados:", list(usuarios_dict.keys()))
    usuario_objetivo = "Angelica"
    k = 3
    print(f"Calculando vecinos para {usuario_objetivo}...")

    vecinos = knn(usuario_objetivo, usuarios_dict, k)

    print(f"\nLos {k} usuarios más parecidos a {usuario_objetivo} son:")
    for nombre, score in vecinos:
        print(f"- {nombre}: {score:.4f}")

if __name__ == "__main__":
    main()
import pandas as pd 
from Knn import knn

def cargar_datos(ruta):

    df = pd.read_csv(ruta, index_col= 0)

    df_transpuesto = df.transpose()
    return df_transpuesto.to_dict(orient='index')

def main():

    usuarios_dict = cargar_datos("DatasetEjemplo.csv")

    usuario_objetivo = "Angelica"
    k = 3
    print(f"Calculando vecinos para {usuario_objetivo}...")

    vecinos = knn(usuario_objetivo, usuarios_dict, k)

    print(f"\nLos {k} usuarios más parecidos a {usuario_objetivo} son:")
    for nombre, score in vecinos:
        print(f"- {nombre}: {score:.4f}")

if __name__ == "__main__":
    main()
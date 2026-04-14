import time
import tracemalloc
import os
import sys
import csv
import json
import pickle
from datetime import datetime


try:
    import pandas as pd
except ImportError:
    print("[ERROR] Instala pandas: pip install pandas")
    sys.exit(1)

#reutilizamos carga del main
from main import cargar_datos

# ──────────────────────────────────────────────────────────────
# MÓDULOS DEL PROYECTO
# ──────────────────────────────────────────────────────────────
from Knn import knn
from recomendacion import recomendacion

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────
K = 10
MIN_VECINOS = 3
METRICAS = ['pearson', 'coseno', 'manhattan', 'euclidiana']

TAMANIOS_BASE = [10, 30, 50, 80, 100, 150, 200, 300, 500,
                 750, 1000, 1500, 2000, 3000, 5000, 10000]

# ──────────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────────

def ram_mb():
    snap = tracemalloc.take_snapshot()
    return sum(s.size for s in snap.statistics('lineno')) / 1024 / 1024

def peso_objeto_mb(obj):
    try:
        return len(pickle.dumps(obj)) / 1024 / 1024
    except Exception:
        return sys.getsizeof(obj) / 1024 / 1024

def disco_mb(ruta):
    return os.path.getsize(ruta) / 1024 / 1024 if os.path.exists(ruta) else 0.0

# ──────────────────────────────────────────────────────────────
# CARGA
# ──────────────────────────────────────────────────────────────

def cargar_n(ruta_ratings, ruta_movies, n):
    usuarios_dict, mapeo_nombres = cargar_datos(ruta_ratings, ruta_movies)

    # Solo usuarios reales (evita "influencer")
    usuarios_ids = sorted(
        [uid for uid in usuarios_dict.keys() if isinstance(uid, int)]
    )[:n]

    usuarios_filtrados = {
        uid: usuarios_dict[uid]
        for uid in usuarios_ids
    }

    return usuarios_filtrados, mapeo_nombres

# ──────────────────────────────────────────────────────────────
# MEDICIÓN
# ──────────────────────────────────────────────────────────────

def medir_todo(ruta_ratings, ruta_movies, n, disco_ratings_mb):

    tracemalloc.start()
    antes = ram_mb()

    t0 = time.perf_counter()
    udict, mnom = cargar_n(ruta_ratings, ruta_movies, n)
    t_carga = time.perf_counter() - t0

    despues = ram_mb()
    tracemalloc.stop()

    ram_delta = max(despues - antes, 0)
    obj_mb = peso_objeto_mb(udict)

    uid = list(udict.keys())[0]
    k_real = min(K, len(udict) - 1)

    fila = {
        'n_usuarios': n,
        'comparaciones': len(udict) - 1,
        'disco_csv_mb': round(disco_ratings_mb, 2),
        'ram_mb': round(ram_delta, 3),
        'objeto_mb': round(obj_mb, 3),
        't_carga_s': round(t_carga, 4),
    }

    for metrica in METRICAS:

        # KNN
        t0 = time.perf_counter()
        vecinos = knn(uid, udict, k=k_real, metrica=metrica)
        t_knn = time.perf_counter() - t0

        # Recomendación
        t0 = time.perf_counter()
        prop = recomendacion(uid, udict, vecinos,
                             min_vecinos=MIN_VECINOS, metrica=metrica)
        t_rec = time.perf_counter() - t0

        lista = prop[0] if isinstance(prop, tuple) else prop

        fila[f'knn_{metrica}_s'] = round(t_knn, 4)
        fila[f'rec_{metrica}_s'] = round(t_rec, 4)
        fila[f'resp_{metrica}_s'] = round(t_knn + t_rec, 4)
        fila[f'nrec_{metrica}'] = len(lista)

    return fila

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ANÁLISIS DE COMPLEJIDAD COMPUTACIONAL")
    print("=" * 60)

    base = os.path.dirname(os.path.abspath(__file__))
    ruta_ratings = os.path.join(base, 'ratings.csv')
    ruta_movies = os.path.join(base, 'movies.csv')

    for ruta in [ruta_ratings, ruta_movies]:
        if not os.path.exists(ruta):
            print(f"[ERROR] No se encontró: {ruta}")
            sys.exit(1)

    disco_ratings = disco_mb(ruta_ratings)

    df_check = pd.read_csv(ruta_ratings)
    max_u = df_check['userId'].nunique()

    tamanios = [t for t in TAMANIOS_BASE if t <= max_u]
    if max_u not in tamanios:
        tamanios.append(max_u)

    tamanios = sorted(set(tamanios))

    print(f"\nUsuarios totales: {max_u}")
    print(f"Tamaños a evaluar: {tamanios}\n")

    filas = []

    for n in tamanios:
        print(f"Procesando {n} usuarios...")
        fila = medir_todo(ruta_ratings, ruta_movies, n, disco_ratings)
        filas.append(fila)

    print("\n Análisis completado" )

    # Guardar resultados
    base_path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_path, 'resultados.json'), 'w', encoding='utf-8') as f:
        json.dump(filas, f, indent=2)

    with open(os.path.join(base_path, 'resultados.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=filas[0].keys())
        writer.writeheader()
        writer.writerows(filas)

    print( "Resultados guardados en JSON y CSV" )

if __name__ == "__main__":
    main()
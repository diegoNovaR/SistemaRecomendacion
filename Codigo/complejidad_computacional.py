import time
import tracemalloc
import os
import sys
import csv
import json
import pickle
from datetime import datetime
 
# ──────────────────────────────────────────────────────────────
# LIBRERÍAS
# ──────────────────────────────────────────────────────────────
try:
    import pandas as pd
except ImportError:
    print("[ERROR] Instala pandas:  pip install pandas")
    sys.exit(1)
 
try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False
    print("[AVISO] psutil no instalado — usando tracemalloc para RAM.")
    print("        Mayor precisión con: pip install psutil\n")
 
# ──────────────────────────────────────────────────────────────
# MÓDULOS REALES DEL PROYECTO
# ──────────────────────────────────────────────────────────────
try:
    from Codigo.correlacion_person   import correlacion_person
    from Codigo.similitud_Coseno     import similitud_coseno
    from Codigo.distancia_Manhattan  import distancia_manhattan
    from Codigo.distancia_Euclidiana import distancia_euclidiana
    from Codigo.Knn                  import knn
    from Codigo.recomendacion        import recomendacion
    print("[OK] Módulos del proyecto importados.\n")
except ImportError as e:
    print(f"[ERROR] {e}")
    print("        Ejecuta desde la carpeta Codigo/")
    sys.exit(1)
 
# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────
K            = 10    # vecinos a buscar
MIN_VECINOS  = 3     # mínimo de vecinos para recomendar
METRICAS     = ['pearson', 'coseno', 'manhattan', 'euclidiana']
 
# Tamaños de dataset a probar
TAMANIOS_BASE = [10, 30, 50, 80, 100, 150, 200, 300, 500,
                 750, 1000, 1500, 2000, 3000, 5000, 10000]
 
 
# ══════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════
 
def ram_mb():
    if PSUTIL_OK:
        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    snap = tracemalloc.take_snapshot()
    return sum(s.size for s in snap.statistics('lineno')) / 1024 / 1024
 
 
def peso_objeto_mb(obj):
    try:
        return len(pickle.dumps(obj)) / 1024 / 1024
    except Exception:
        return sys.getsizeof(obj) / 1024 / 1024
 
 
def disco_mb(ruta):
    return os.path.getsize(ruta) / 1024 / 1024 if os.path.exists(ruta) else 0.0
 
 
# ══════════════════════════════════════════════════════════════
# CARGA DE SUBCONJUNTO
# ══════════════════════════════════════════════════════════════
 
def cargar_n(ruta_ratings, ruta_movies, n):
    """
    Carga los primeros N usuarios del CSV.
    Misma lógica que cargar_datos() en main.py.
    """
    df_r = pd.read_csv(ruta_ratings)
    df_m = pd.read_csv(ruta_movies)
    ids  = df_r['userId'].unique()[:n]
    df_s = df_r[df_r['userId'].isin(ids)]
    mat  = df_s.pivot(index='userId', columns='movieId', values='rating')
    udict = mat.to_dict(orient='index')
    mnom  = dict(zip(df_m['movieId'], df_m['title']))
    return udict, mnom
 
 
# ══════════════════════════════════════════════════════════════
# MEDICIÓN COMPLETA PARA UN TAMAÑO N
# ══════════════════════════════════════════════════════════════
 
def medir_todo(ruta_ratings, ruta_movies, n, disco_ratings_mb):
    """
    Para N usuarios, mide en este orden:
      1. RAM antes de cargar
      2. Tiempo de carga + RAM después
      3. Peso del objeto en memoria
      4. KNN con cada una de las 4 métricas
      5. Recomendación con cada métrica
    Retorna un dict con todos los valores.
    """
 
    # ── 1. Carga ────────────────────────────────────────────
    tracemalloc.start()
    antes = ram_mb()
 
    t0 = time.perf_counter()
    udict, mnom = cargar_n(ruta_ratings, ruta_movies, n)
    t_carga = time.perf_counter() - t0
 
    despues = ram_mb()
    tracemalloc.stop()
 
    ram_delta = max(despues - antes, 0)
    obj_mb    = peso_objeto_mb(udict)
 
    uid   = list(udict.keys())[0]
    k_real = min(K, len(udict) - 1)
 
    fila = {
        'n_usuarios'    : n,
        'comparaciones' : len(udict) - 1,
        'disco_csv_mb'  : round(disco_ratings_mb, 2),
        'ram_mb'        : round(ram_delta, 3),
        'objeto_mb'     : round(obj_mb, 3),
        't_carga_s'     : round(t_carga, 4),
    }
 
    # ── 2. KNN + Recomendación por cada métrica ─────────────
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
 
        fila[f'knn_{metrica}_s']  = round(t_knn, 4)
        fila[f'rec_{metrica}_s']  = round(t_rec, 4)
        fila[f'resp_{metrica}_s'] = round(t_knn + t_rec, 4)
        fila[f'nrec_{metrica}']   = len(lista)
 
    return fila
 
 
# ══════════════════════════════════════════════════════════════
# IMPRIMIR TABLA UNIFICADA
# ══════════════════════════════════════════════════════════════
 
def imprimir_tabla(filas, disco_ratings_mb, disco_movies_mb):
 
    DIV  = "═" * 160
    DIV2 = "─" * 160
    DIV3 = "─" * 160
 
    print(f"\n{DIV}")
    print("  ANÁLISIS DE COMPLEJIDAD COMPUTACIONAL — TABLA UNIFICADA")
    print(f"  Sistema de Recomendación MovieLens  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(DIV)
 
    # ── Bloque de explicación ────────────────────────────────
    print(f"""
  REFERENCIA DEL DATASET COMPLETO:
    ratings.csv en disco : {disco_ratings_mb:.2f} MB
    movies.csv  en disco : {disco_movies_mb:.2f} MB
    (el espacio en disco es fijo — no cambia con N usuarios)
 
  EXPLICACIÓN DE LAS COLUMNAS:
 
    Usuarios      → Cantidad de usuarios cargados en esa prueba.
    Compar.       → Comparaciones que hace KNN (= Usuarios − 1).
    Disco(MB)     → Tamaño del archivo ratings.csv en el disco duro.
    RAM(MB)       → RAM extra que consume el proceso al cargar N usuarios.
    Obj.Mem(MB)   → Peso del diccionario de usuarios en memoria (pickle).
    T.Carga(s)    → Tiempo de leer CSV y construir el dict. (ocurre 1 sola vez).
 
    Para cada métrica [Pearson | Coseno | Manhattan | Euclidiana]:
      T.KNN(s)    → Tiempo de buscar los {K} vecinos más cercanos.
      T.Rec(s)    → Tiempo de calcular las recomendaciones con esos vecinos.
      T.Resp(s)   → Tiempo total de respuesta = T.KNN + T.Rec.
      #Recs       → Cantidad de películas recomendadas generadas.
""")
 
    # ── Encabezado bloque 1: almacenamiento y carga ──────────
    print(DIV2)
    print(f"  {'':─<159}")
    print(f"  {'ALMACENAMIENTO Y CARGA':^40}  |  {'PEARSON':^30}  |  {'COSENO':^30}  |  {'MANHATTAN':^30}  |  {'EUCLIDIANA':^30}")
    print(f"  {'':─<159}")
    print(
        f"  {'Usuarios':>9} "
        f"{'Compar.':>9} "
        f"{'Disco(MB)':>9} "
        f"{'RAM(MB)':>8} "
        f"{'Obj(MB)':>8} "
        f"{'T.Carga':>8}  "
        f"  {'T.KNN':>7} {'T.Rec':>7} {'T.Resp':>7} {'#Recs':>5}  "
        f"  {'T.KNN':>7} {'T.Rec':>7} {'T.Resp':>7} {'#Recs':>5}  "
        f"  {'T.KNN':>7} {'T.Rec':>7} {'T.Resp':>7} {'#Recs':>5}  "
        f"  {'T.KNN':>7} {'T.Rec':>7} {'T.Resp':>7} {'#Recs':>5}"
    )
    print(f"  {'':─<8} {'':─<8} {'':─<9} {'':─<8} {'':─<7} {'':─<8}  "
          f"  {'':─<7} {'':─<7} {'':─<7} {'':─<5}  "
          f"  {'':─<7} {'':─<7} {'':─<7} {'':─<5}  "
          f"  {'':─<7} {'':─<7} {'':─<7} {'':─<5}  "
          f"  {'':─<7} {'':─<7} {'':─<7} {'':─<5}")
 
    # ── Filas de datos ───────────────────────────────────────
    for f in filas:
        print(
            f"  {f['n_usuarios']:>9} "
            f"{f['comparaciones']:>9} "
            f"{f['disco_csv_mb']:>9.2f} "
            f"{f['ram_mb']:>8.3f} "
            f"{f['objeto_mb']:>8.3f} "
            f"{f['t_carga_s']:>8.4f}  "
 
            # Pearson
            f"  {f['knn_pearson_s']:>7.4f} "
            f"{f['rec_pearson_s']:>7.4f} "
            f"{f['resp_pearson_s']:>7.4f} "
            f"{f['nrec_pearson']:>5}  "
 
            # Coseno
            f"  {f['knn_coseno_s']:>7.4f} "
            f"{f['rec_coseno_s']:>7.4f} "
            f"{f['resp_coseno_s']:>7.4f} "
            f"{f['nrec_coseno']:>5}  "
 
            # Manhattan
            f"  {f['knn_manhattan_s']:>7.4f} "
            f"{f['rec_manhattan_s']:>7.4f} "
            f"{f['resp_manhattan_s']:>7.4f} "
            f"{f['nrec_manhattan']:>5}  "
 
            # Euclidiana
            f"  {f['knn_euclidiana_s']:>7.4f} "
            f"{f['rec_euclidiana_s']:>7.4f} "
            f"{f['resp_euclidiana_s']:>7.4f} "
            f"{f['nrec_euclidiana']:>5}"
        )
 
    print(DIV2)
 
    # ── Análisis de crecimiento ──────────────────────────────
    if len(filas) >= 2:
        primero = filas[0]
        ultimo  = filas[-1]
        factor_u = ultimo['n_usuarios'] / primero['n_usuarios']
        factor_k = ultimo['knn_pearson_s'] / primero['knn_pearson_s'] if primero['knn_pearson_s'] > 0 else 0
 
        print(f"""
  ANÁLISIS DE CRECIMIENTO:
 
    De {primero['n_usuarios']} → {ultimo['n_usuarios']} usuarios ({factor_u:.0f}× más datos):
 
    Disco CSV      : sin cambio — el archivo es siempre el mismo ({ultimo['disco_csv_mb']:.2f} MB).
    RAM            : crece linealmente. Más usuarios = más RAM para el diccionario.
    Objeto memoria : crece linealmente con usuarios × películas promedio.
    Tiempo de carga: crece con O(N) — leer y convertir más filas del CSV.
    Tiempo KNN     : crece con O(N) por consulta — {factor_k:.1f}× más lento con {factor_u:.0f}× más usuarios.
                     Cuello de botella del sistema.
    Tiempo Rec     : casi constante O(K×P) — K=10 vecinos fijo, muy rápido.
    Tiempo respuesta: dominado por KNN.
 
  COMPARACIÓN DE MÉTRICAS (último tamaño = {ultimo['n_usuarios']} usuarios):
    · Pearson    T.KNN = {ultimo['knn_pearson_s']:.4f}s
    · Coseno     T.KNN = {ultimo['knn_coseno_s']:.4f}s
    · Manhattan  T.KNN = {ultimo['knn_manhattan_s']:.4f}s   ← más rápida (sin raíz cuadrada)
    · Euclidiana T.KNN = {ultimo['knn_euclidiana_s']:.4f}s   ← más lenta (usa sqrt)
""")
 
    print(DIV)
 
 
# ══════════════════════════════════════════════════════════════
# EXPORTAR
# ══════════════════════════════════════════════════════════════
 
def exportar(filas, reporte):
    base = os.path.dirname(os.path.abspath(__file__))
 
    ruta_json = os.path.join(base, 'resultados_complejidad.json')
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
 
    ruta_csv = os.path.join(base, 'escalabilidad.csv')
    if filas:
        with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=filas[0].keys())
            writer.writeheader()
            writer.writerows(filas)
 
    print(f"  [OK] resultados_complejidad.json → {ruta_json}")
    print(f"  [OK] escalabilidad.csv           → {ruta_csv}")
 
 
# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
 
def main():
    print("=" * 64)
    print("  ANÁLISIS DE COMPLEJIDAD COMPUTACIONAL")
    print("  Sistema de Recomendación MovieLens")
    print("=" * 64)
    print()
 
    base         = os.path.dirname(os.path.abspath(__file__))
    ruta_ratings = os.path.join(base, 'ratings.csv')
    ruta_movies  = os.path.join(base, 'movies.csv')
 
    for ruta in [ruta_ratings, ruta_movies]:
        if not os.path.exists(ruta):
            print(f"[ERROR] No se encontró: {ruta}")
            print("        Coloca ratings.csv y movies.csv en Codigo/")
            sys.exit(1)
 
    disco_ratings = disco_mb(ruta_ratings)
    disco_movies  = disco_mb(ruta_movies)
 
    # Determinar tamaños disponibles
    df_check = pd.read_csv(ruta_ratings)
    max_u    = df_check['userId'].nunique()
 
    tamanios = [t for t in TAMANIOS_BASE if t <= max_u]
    if max_u not in tamanios:
        tamanios.append(max_u)
    tamanios = sorted(set(tamanios))
 
    print(f"  Dataset: {max_u} usuarios totales en ratings.csv")
    print(f"  Tamaños a probar: {tamanios}")
    print(f"  Métricas: {METRICAS}")
    print(f"  K = {K} vecinos | min_vecinos = {MIN_VECINOS}")
    print()
    print("  Procesando", end='', flush=True)
 
    filas = []
    for n in tamanios:
        print(f" {n}...", end='', flush=True)
        fila = medir_todo(ruta_ratings, ruta_movies, n, disco_ratings)
        filas.append(fila)
 
    print(" ✓\n")
 
    # Tabla + análisis
    imprimir_tabla(filas, disco_ratings, disco_movies)
 
    # Exportar
    print("\n  Guardando archivos...")
    reporte = {
        'timestamp'       : datetime.now().isoformat(),
        'configuracion'   : {'k': K, 'min_vecinos': MIN_VECINOS, 'metricas': METRICAS},
        'disco_ratings_mb': round(disco_ratings, 3),
        'disco_movies_mb' : round(disco_movies, 3),
        'resultados'      : filas,
    }
    exportar(filas, reporte)
    print("\n  Análisis completado.")
 
 
if __name__ == "__main__":
    main()
 
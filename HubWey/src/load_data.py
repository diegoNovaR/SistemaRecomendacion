"""
01_load_data.py
---------------
Módulo de CARGA DE DATOS — Ciclo de vida de los datos
Responsabilidades:
  - Cargar los 3 datasets desde archivos CSV
  - Mostrar estructura básica (head, shape, dtypes, info)
  - Retornar los DataFrames para el siguiente paso
"""

import pandas as pd
import os

# ─────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

PATHS = {
    "stations": os.path.join(DATA_DIR, "hubway_stations.csv"),
    "trips":    os.path.join(DATA_DIR, "hubway_trips.csv"),
    #"trips_fe": os.path.join(DATA_DIR, "hubwaytrips.csv"),   # versión con features de ingeniería
}


# ─────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────
def load_all(verbose: bool = True) -> dict[str, pd.DataFrame]:
    """
    Carga los 3 CSVs y devuelve un diccionario de DataFrames.

    Parámetros
    ----------
    verbose : bool
        Si True, imprime head, shape, dtypes e info de cada dataset.

    Retorna
    -------
    dict con claves: 'stations', 'trips', 'trips_fe'
    """
    dfs = {}

    for name, path in PATHS.items():
        print(f"\n{'='*60}")
        print(f"  Cargando: {name}  →  {os.path.basename(path)}")
        print(f"{'='*60}")

        try:
            df = pd.read_csv(path, low_memory=False)
            dfs[name] = df

            if verbose:
                _inspect(df, name)

        except FileNotFoundError:
            print(f"  [ERROR] Archivo no encontrado: {path}")

    return dfs


def _inspect(df: pd.DataFrame, name: str) -> None:
    """Inspección rápida de un DataFrame."""

    print(f"\n Shape: {df.shape[0]:,} filas × {df.shape[1]} columnas")

    print(f"\n Columnas y tipos:")
    print(df.dtypes.to_string())

    print(f"\n Primeras 5 filas (.head):")
    print(df.head().to_string())

    print(f"\n Estadísticas rápidas:")
    cols = ["count", "unique", "top", "mean", "min", "max"]
    print(df.describe(include="all").T
            .reindex(columns=cols)       # si alguna columna no existe, pone NaN
            .dropna(how="all")
            .to_string())

    print(f"\n Valores nulos por columna:")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if nulls.empty:
        print("   Sin valores nulos")
    else:
        print(nulls.to_string())


# ─────────────────────────────────────────────
# Ejecución directa (testing)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    datasets = load_all(verbose=True)
    print(f"\n Datasets cargados: {list(datasets.keys())}")
"""
01b_load_clean.py
-----------------
Módulo de CARGA DE DATOS LIMPIOS — Ciclo de vida de los datos
Responsabilidades:
  - Cargar los CSVs ya procesados desde data/clean/
  - Restaurar tipos de datos que CSV no preserva (datetime, category)
  - Retornar DataFrames listos para EDA y visualización

Separado de 01_load_data.py por el principio de responsabilidad única:
  01_load_data   → datos crudos (para limpieza)
  01b_load_clean → datos limpios (para análisis)
"""

import pandas as pd
import os

CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")

PATHS_CLEAN = {
    "stations": os.path.join(CLEAN_DIR, "hubway_stations_clean.csv"),
    "trips":    os.path.join(CLEAN_DIR, "hubway_trips_clean.csv"),
    #"trips_fe": os.path.join(CLEAN_DIR, "hubwaytrips_clean.csv"),
}


def load_clean(verbose: bool = True) -> dict[str, pd.DataFrame]:
    """
    Carga los CSVs limpios y restaura los tipos correctos.

    Retorna
    -------
    dict con claves: 'stations', 'trips', 'trips_fe'
    """
    dfs = {}

    for name, path in PATHS_CLEAN.items():
        print(f"\n{'='*60}")
        print(f"  Cargando limpio: {name}  →  {os.path.basename(path)}")
        print(f"{'='*60}")

        if not os.path.exists(path):
            print(f"  [ERROR] Archivo no encontrado: {path}")
            print(f"  → Ejecuta primero 02_clean_data.py para generarlo.")
            continue

        df = _load_with_types(name, path)
        dfs[name] = df

        if verbose:
            print(f" Shape: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            print(f" Columnas: {list(df.columns)}")
            print(f"\n .head():")
            print(df.head().to_string())

    return dfs


def _load_with_types(name: str, path: str) -> pd.DataFrame:
    """Carga el CSV y restaura tipos que se pierden al serializar."""

    if name == "stations":
        df = pd.read_csv(path)
        df["status"]    = df["status"].astype("category")
        df["municipal"] = df["municipal"].astype("category")

    elif name == "trips":
        df = pd.read_csv(
            path,
            parse_dates=["start_date", "end_date"],   # restaura datetime
            low_memory=False
        )
        df["subsc_type"] = df["subsc_type"].astype("category")
        df["gender"]     = df["gender"].astype("category")

    elif name == "trips_fe":
        df = pd.read_csv(path)

    else:
        df = pd.read_csv(path)

    return df


# ─────────────────────────────────────────────────────────────
# Ejecución directa (testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clean = load_clean(verbose=True)
    print(f"\n Datasets limpios cargados: {list(clean.keys())}")
    print("\n Tipos de datos — trips:")
    if "trips" in clean:
        print(clean["trips"].dtypes.to_string())
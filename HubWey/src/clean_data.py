"""
02_clean_data.py
----------------
Módulo de LIMPIEZA DE DATOS — Ciclo de vida de los datos
Responsabilidades:
  - Recibir los DataFrames crudos del módulo 01_load_data
  - Aplicar transformaciones de limpieza documentadas
  - Guardar los CSVs limpios en data/clean/
  - Retornar los DataFrames limpios para el siguiente paso

NO carga archivos directamente (eso es responsabilidad de 01_load_data).
NO genera gráficos ni análisis (eso es responsabilidad de 03 y 04).
"""

import pandas as pd
import os

CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")


# ─────────────────────────────────────────────────────────────
# Orquestador
# ─────────────────────────────────────────────────────────────
def clean_all(datasets: dict[str, pd.DataFrame], verbose: bool = True) -> dict[str, pd.DataFrame]:
    """
    Aplica la limpieza a cada dataset y guarda los resultados.

    Parámetros
    ----------
    datasets : dict  →  {'stations': df, 'trips': df, 'trips_fe': df}
    verbose  : bool  →  imprime reporte de cambios

    Retorna
    -------
    dict con los mismos keys pero DataFrames ya limpios
    """
    os.makedirs(CLEAN_DIR, exist_ok=True)

    clean = {}

    for name, cleaner, filename in [
        ("stations", _clean_stations, "hubway_stations_clean.csv"),
        ("trips",    _clean_trips,    "hubway_trips_clean.csv"),
        ("trips_fe", _clean_trips_fe, "hubwaytrips_clean.csv"),
    ]:
        if name not in datasets:
            print(f"  ⚠️  Dataset '{name}' no encontrado — omitiendo.")
            continue
        clean[name] = cleaner(datasets[name], verbose)
        _save(clean[name], filename)

    return clean


# ─────────────────────────────────────────────────────────────
# Limpieza: stations
# ─────────────────────────────────────────────────────────────
def _clean_stations(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    _header("stations")
    original_shape = df.shape
    df = df.copy()

    # 1. Convertir columnas categóricas de baja cardinalidad
    df["status"]    = df["status"].astype("category")
    df["municipal"] = df["municipal"].astype("category")
    _log("Convertido status y municipal → category", verbose)

    # 2. Renombrar columnas para consistencia
    df = df.rename(columns={"lat": "latitude", "lng": "longitude"})
    _log("Renombrado lat/lng → latitude/longitude", verbose)

    _summary(original_shape, df.shape, verbose)
    return df


# ─────────────────────────────────────────────────────────────
# Limpieza: trips (dataset principal)
# ─────────────────────────────────────────────────────────────
def _clean_trips(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    _header("trips")
    original_shape = df.shape
    df = df.copy()

    # 1. Eliminar columna 'status' (valor único: 'Closed' — no aporta)
    df = df.drop(columns=["status"])
    _log("Eliminada columna 'status' (valor constante: 'Closed')", verbose)

    # 2. Eliminar columnas con >70% de nulos
    df = df.drop(columns=["birth_date", "zip_code"])
    _log("Eliminadas 'birth_date' (78% nulos) y 'zip_code' (30% nulos + formato sucio)", verbose)

    # 3. Rellenar nulos en 'gender' → 'No registrado'
    before = df["gender"].isnull().sum()
    df["gender"] = df["gender"].fillna("No registrado")
    _log(f"Rellenados {before:,} nulos en 'gender' → 'No registrado'", verbose)

    # 4. Eliminar filas con nulos en columnas críticas de navegación
    before = len(df)
    df = df.dropna(subset=["strt_statn", "end_statn", "bike_nr"])
    _log(f"Eliminadas {before - len(df):,} filas con nulos en strt_statn / end_statn / bike_nr", verbose)

    # 5. Filtrar duraciones inválidas (negativas o cero)
    before = len(df)
    df = df[df["duration"] > 0]
    _log(f"Eliminadas {before - len(df):,} filas con duration ≤ 0 (incluye negativos)", verbose)

    # 6. Parsear fechas a datetime
    df["start_date"] = pd.to_datetime(df["start_date"], format="%m/%d/%Y %H:%M:%S", errors="coerce")
    df["end_date"]   = pd.to_datetime(df["end_date"],   format="%m/%d/%Y %H:%M:%S", errors="coerce")
    _log("Convertidas start_date y end_date → datetime", verbose)

    # 7. Tipos categóricos para columnas de baja cardinalidad
    df["subsc_type"] = df["subsc_type"].astype("category")
    df["gender"]     = df["gender"].astype("category")
    _log("Convertidas subsc_type y gender → category", verbose)

    # 8. Convertir strt_statn y end_statn a int (eran float por nulos previos)
    df["strt_statn"] = df["strt_statn"].astype(int)
    df["end_statn"]  = df["end_statn"].astype(int)
    _log("Convertidas strt_statn y end_statn → int", verbose)

    _summary(original_shape, df.shape, verbose)
    return df


# ─────────────────────────────────────────────────────────────
# Limpieza: trips_fe (dataset con features de ingeniería)
# ─────────────────────────────────────────────────────────────
def _clean_trips_fe(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    _header("trips_fe (hubwaytrips)")
    original_shape = df.shape
    df = df.copy()

    # Este dataset ya es un producto de feature engineering
    # Solo validamos que las columnas binarias sean efectivamente 0/1
    binary_cols = ["Morning", "Afternoon", "Evening", "Night",
                   "Weekday", "Weekend", "Male"]

    for col in binary_cols:
        if col in df.columns:
            valores = df[col].dropna().unique()
            if not all(v in [0, 1] for v in valores):
                print(f"  ⚠️  Columna '{col}' contiene valores fuera de {{0,1}}: {valores}")

    _log(f"Validadas {len(binary_cols)} columnas binarias", verbose)

    # Filtrar duraciones inválidas si las hubiera
    before = len(df)
    if "Duration" in df.columns:
        df = df[df["Duration"] > 0]
        eliminadas = before - len(df)
        if eliminadas > 0:
            _log(f"Eliminadas {eliminadas:,} filas con Duration ≤ 0", verbose)

    _summary(original_shape, df.shape, verbose)
    return df


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _save(df: pd.DataFrame, filename: str) -> None:
    path = os.path.join(CLEAN_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  💾 Guardado → {path}  ({len(df):,} filas)")


def _header(name: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Limpiando: {name}")
    print(f"{'='*60}")


def _log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"  ✔  {msg}")


def _summary(before: tuple, after: tuple, verbose: bool) -> None:
    if verbose:
        filas_eliminadas = before[0] - after[0]
        print(f"\n  📉 Filas: {before[0]:,} → {after[0]:,}  (-{filas_eliminadas:,})")
        print(f"  📐 Columnas: {before[1]} → {after[1]}")


# ─────────────────────────────────────────────────────────────
# Ejecución directa (testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.load_data import load_all

    raw = load_all(verbose=False)
    clean = clean_all(raw, verbose=True)
    print(f"\n✅ Limpieza completa. Datasets: {list(clean.keys())}")
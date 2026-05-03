"""
02b_features.py
---------------
Módulo de FEATURE ENGINEERING — Ciclo de vida de los datos
Responsabilidades:
  - Recibir los DataFrames limpios de 02_clean_data
  - Crear columnas derivadas útiles para las hipótesis planteadas
  - Guardar el CSV enriquecido en data/clean/
  - Retornar el DataFrame enriquecido para EDA y visualización

Hipótesis que guían las features creadas:
  H1 — ¿Qué características determinan el nivel de uso?
  H2 — ¿Qué bicicletas tienen más viajes realizados?
  H3 — ¿Qué bicicletas acumulan mayor tiempo total de uso?
  H4 — ¿Relación entre cantidad de viajes y tiempo total por bicicleta?
  H5 — ¿El uso está asociado al género del usuario?
  H6 — ¿Cómo influye el día en el tiempo de uso?
  H7 — ¿Existen diferencias significativas a lo largo del tiempo?

NO limpia datos (responsabilidad de 02_clean_data).
NO genera gráficos ni análisis (responsabilidad de 03 y 04).
"""

import pandas as pd
import os

CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
OUTPUT_PATH = os.path.join(CLEAN_DIR, "hubway_trips_features.csv")


# ─────────────────────────────────────────────────────────────
# Orquestador
# ─────────────────────────────────────────────────────────────
def build_features(datasets: dict[str, pd.DataFrame], verbose: bool = True) -> dict[str, pd.DataFrame]:
    """
    Construye features sobre el dataset de trips limpio.

    Parámetros
    ----------
    datasets : dict  →  resultado de clean_all() o load_clean()
    verbose  : bool  →  imprime reporte de columnas creadas

    Retorna
    -------
    El mismo dict con datasets["trips"] reemplazado por la versión enriquecida
    """
    if "trips" not in datasets:
        print("  [ERROR] 'trips' no encontrado en datasets.")
        return datasets

    result = datasets.copy()
    result["trips"] = _engineer_trips(datasets["trips"], verbose)
    return result


# ─────────────────────────────────────────────────────────────
# Feature engineering: trips
# ─────────────────────────────────────────────────────────────
def _engineer_trips(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print(f"  Feature Engineering: trips")
    print(f"{'='*60}")

    df = df.copy()
    cols_before = set(df.columns)

    # ── 1. Descomposición temporal de start_date ──────────────
    # Útil para H6 (influencia del día) y H7 (diferencias en el tiempo)
    df["hour"]  = df["start_date"].dt.hour
    df["month"] = df["start_date"].dt.month
    df["year"]  = df["start_date"].dt.year
    _log("Creadas: hour, month, year  (desde start_date)", verbose)

    # ── 2. Momento del día ────────────────────────────────────
    # Útil para H1 (características de uso) y H6
    df["time_of_day"] = df["hour"].apply(_classify_time_of_day)
    df["time_of_day"] = df["time_of_day"].astype("category")
    _log("Creada:  time_of_day  (Morning / Afternoon / Evening / Night)", verbose)

    # ── 3. Tipo de día ────────────────────────────────────────
    # Lunes=0 … Domingo=6  →  0-4 = Weekday, 5-6 = Weekend
    # Útil para H6 y H1
    df["day_type"] = df["start_date"].dt.dayofweek.apply(
        lambda d: "Weekend" if d >= 5 else "Weekday"
    )
    df["day_type"] = df["day_type"].astype("category")
    _log("Creada:  day_type  (Weekday / Weekend)", verbose)

    # ── 4. Duración en minutos ────────────────────────────────
    # La duración original está en segundos; minutos es más legible
    # Útil para H2, H3, H4
    df["duration_min"] = (df["duration"] / 60).round(2)
    _log("Creada:  duration_min  (duration en minutos)", verbose)

    # ── 5. Métricas agregadas por bicicleta ───────────────────
    # Útil para H2 (más viajes), H3 (más tiempo), H4 (relación entre ambas)
    bike_stats = (
        df.groupby("bike_nr", observed=True)
        .agg(
            bike_total_trips=("seq_id", "count"),
            bike_total_min=("duration_min", "sum"),
            bike_avg_min=("duration_min", "mean"),
        )
        .reset_index()
    )
    df = df.merge(bike_stats, on="bike_nr", how="left")
    _log("Creadas: bike_total_trips, bike_total_min, bike_avg_min  (por bicicleta)", verbose)

    # ── Reporte final ─────────────────────────────────────────
    cols_new = set(df.columns) - cols_before
    if verbose:
        print(f"\n   Columnas nuevas ({len(cols_new)}):")
        for col in sorted(cols_new):
            print(f"     + {col:25s}  dtype: {df[col].dtype}")
        print(f"\n   Shape final: {df.shape[0]:,} filas × {df.shape[1]} columnas")

        cols = ["count", "unique", "top", "mean", "min", "max"]
        print(df.describe(include="all").T
            .reindex(columns=cols)       # si alguna columna no existe, pone NaN
            .dropna(how="all")
            .to_string())

    # ── Guardar ───────────────────────────────────────────────
    _save(df)

    return df


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _classify_time_of_day(hour: int) -> str:
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Evening"
    else:                    # 0-5
        return "Night"


def _save(df: pd.DataFrame) -> None:
    os.makedirs(CLEAN_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n  Guardado → {OUTPUT_PATH}  ({len(df):,} filas)")


def _log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"  ✔  {msg}")


# ─────────────────────────────────────────────────────────────
# Ejecución directa (testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.load_clean import load_clean

    datasets = load_clean(verbose=False)
    enriched = build_features(datasets, verbose=True)
    print("\n✅ Feature engineering completo.")
    print(enriched["trips"][["bike_nr", "time_of_day", "day_type",
                              "duration_min", "bike_total_trips"]].head())
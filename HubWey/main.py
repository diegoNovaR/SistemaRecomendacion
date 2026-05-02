"""
main.py
-------
Orquestador del pipeline de Ciencia de Datos — Hubway Bike Sharing

Pipeline:
  1a. Carga raw    → load_all()
  2.  Limpieza     → clean_all()      guarda en data/clean/
  1b. Carga clean  → load_clean()     restaura tipos correctos
  3.  EDA          → run_eda()        [próximo paso]
  4.  Visualización→ run_plots()      [próximo paso]
  5.  Insights     → run_insights()   [próximo paso]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.load_data  import load_all    # noqa: E402
from src.clean_data import clean_all   # noqa: E402
from src.load_clean import load_clean  # noqa: E402


def main():
    print("\n" + "🚲" * 30)
    print("  HUBWAY BIKE SHARING — Pipeline de Ciencia de Datos")
    print("🚲" * 30)

    # ── ETAPA 1a: Carga raw ───────────────────────────────
    print("\n\n📦 ETAPA 1a — CARGA DE DATOS RAW")
    raw = load_all(verbose=True)

    # ── ETAPA 2: Limpieza ─────────────────────────────────
    print("\n\n🧹 ETAPA 2 — LIMPIEZA DE DATOS")
    clean_all(raw, verbose=True)          # guarda CSVs en data/clean/

    # ── ETAPA 1b: Carga clean ─────────────────────────────
    print("\n\n📦 ETAPA 1b — CARGA DE DATOS LIMPIOS")
    datasets = load_clean(verbose=True)   # listo para EDA y gráficos

    # ── Etapas siguientes (próximos módulos) ──────────────
    # run_eda(datasets)
    # run_plots(datasets)
    # run_insights(datasets)

    print("\n\n✅ Pipeline completado hasta ETAPA 2")


if __name__ == "__main__":
    main()
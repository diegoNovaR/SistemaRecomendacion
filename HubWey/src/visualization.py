"""
04_visualization.py
-------------------
Módulo de VISUALIZACIONES — Ciclo de vida de los datos
Responsabilidades:
  - Recibir datasets enriquecidos (desde 02b_features)
  - Generar los 8 gráficos del plan académico
  - Guardar cada figura en outputs/figures/
  - NO modifica datos, NO imprime estadísticas (eso es EDA)

Hipótesis cubiertas:
  H2 — ¿Qué bicicletas tienen más viajes?
  H3 — ¿Qué bicicletas acumulan más tiempo?
  H4 — ¿Relación viajes vs tiempo total?
  H5 — ¿El uso está asociado al género?
  H6 — ¿Cómo influye el día / momento del día?
  H7 — ¿Diferencias a lo largo del tiempo?
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ─────────────────────────────────────────────────────────────
# Configuración global de estilo
# ─────────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures")

# Paleta académica sobria y consistente
PALETTE_MAIN   = "#2C6E9B"          # azul principal
PALETTE_ACCENT = "#E8734A"          # naranja acento
PALETTE_GENDER = {
    "Male":           "#2C6E9B",
    "Female":         "#E8734A",
    "No registrado":  "#A8A8A8",
}
PALETTE_TIME = {
    "Morning":   "#F4C430",
    "Afternoon": "#E8734A",
    "Evening":   "#2C6E9B",
    "Night":     "#4A3560",
}

def _set_style():
    sns.set_theme(style="whitegrid", font_scale=1.1)
    plt.rcParams.update({
        "font.family":        "DejaVu Sans",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.titlesize":     14,
        "axes.titleweight":   "bold",
        "axes.labelsize":     11,
        "figure.dpi":         150,
        "savefig.dpi":        150,
        "savefig.bbox":       "tight",
    })


# ─────────────────────────────────────────────────────────────
# Orquestador
# ─────────────────────────────────────────────────────────────
def run_plots(datasets: dict[str, pd.DataFrame], verbose: bool = True) -> None:
    """
    Genera y guarda los 8 gráficos del plan académico.

    Parámetros
    ----------
    datasets : dict  →  resultado de build_features()
    verbose  : bool  →  imprime ruta de cada figura guardada
    """
    os.makedirs(FIGURES_DIR, exist_ok=True)
    _set_style()

    df = datasets["trips"]

    print(f"\n{'='*60}")
    print(f"  Generando visualizaciones")
    print(f"{'='*60}")

    # Tabla resumen por bicicleta (una fila por bici)
    bike_summary = (
        df.drop_duplicates(subset=["bike_nr"])
        [["bike_nr", "bike_total_trips", "bike_total_min", "bike_avg_min"]]
        .sort_values("bike_total_trips", ascending=False)
        .reset_index(drop=True)
    )

    _plot_h2_top_trips(bike_summary, verbose)
    _plot_h3_top_time(bike_summary, verbose)
    _plot_h3h4_scatter(bike_summary, verbose)
    _plot_h5_pie(df, verbose)
    _plot_h5_bar_gender_subs(df, verbose)
    _plot_h6_heatmap(df, verbose)
    _plot_h6_boxplot(df, verbose)
    _plot_h7_line(df, verbose)

    print(f"\n✅ {8} gráficos guardados en {FIGURES_DIR}")


# ─────────────────────────────────────────────────────────────
# H2 — Top 20 bicicletas por cantidad de viajes
# ─────────────────────────────────────────────────────────────
def _plot_h2_top_trips(bike_summary: pd.DataFrame, verbose: bool) -> None:
    top20 = bike_summary.nlargest(20, "bike_total_trips")

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(
        top20["bike_nr"][::-1],
        top20["bike_total_trips"][::-1],
        color=PALETTE_MAIN, edgecolor="white", linewidth=0.5
    )
    # Etiqueta de valor al final de cada barra
    for bar in bars:
        ax.text(
            bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
            f"{int(bar.get_width()):,}", va="center", fontsize=9, color="#444"
        )
    ax.set_xlabel("Total de viajes realizados")
    ax.set_title("H2 — Top 20 bicicletas con mayor cantidad de viajes", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h2_top20_viajes.png", verbose)


# ─────────────────────────────────────────────────────────────
# H3 — Top 20 bicicletas por tiempo acumulado
# ─────────────────────────────────────────────────────────────
def _plot_h3_top_time(bike_summary: pd.DataFrame, verbose: bool) -> None:
    top20 = bike_summary.nlargest(20, "bike_total_min")

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(
        top20["bike_nr"][::-1],
        top20["bike_total_min"][::-1],
        color=PALETTE_ACCENT, edgecolor="white", linewidth=0.5
    )
    for bar in bars:
        ax.text(
            bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f} min", va="center", fontsize=9, color="#444"
        )
    ax.set_xlabel("Tiempo total acumulado (minutos)")
    ax.set_title("H3 — Top 20 bicicletas con mayor tiempo acumulado de uso", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h3_top20_tiempo.png", verbose)


# ─────────────────────────────────────────────────────────────
# H3 + H4 — Scatter: viajes vs tiempo total
# ─────────────────────────────────────────────────────────────
def _plot_h3h4_scatter(bike_summary: pd.DataFrame, verbose: bool) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(
        bike_summary["bike_total_trips"],
        bike_summary["bike_total_min"],
        alpha=0.5, s=25, color=PALETTE_MAIN, edgecolors="white", linewidths=0.4
    )
    # Línea de tendencia
    import numpy as np
    m, b = np.polyfit(bike_summary["bike_total_trips"], bike_summary["bike_total_min"], 1)
    x_range = pd.Series(sorted(bike_summary["bike_total_trips"]))
    ax.plot(x_range, m * x_range + b, color=PALETTE_ACCENT, linewidth=1.8,
            linestyle="--", label=f"Tendencia lineal")
    ax.legend(fontsize=9)
    ax.set_xlabel("Total de viajes por bicicleta")
    ax.set_ylabel("Tiempo total acumulado (min)")
    ax.set_title("H4 — Relación entre cantidad de viajes y tiempo acumulado por bicicleta", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h4_scatter_viajes_tiempo.png", verbose)


# ─────────────────────────────────────────────────────────────
# H5 — Pie chart: distribución por género
# ─────────────────────────────────────────────────────────────
def _plot_h5_pie(df: pd.DataFrame, verbose: bool) -> None:
    counts = df["gender"].value_counts()
    colors = [PALETTE_GENDER.get(g, "#ccc") for g in counts.index]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11},
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("H5 — Distribución de viajes por género", pad=20)
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.97)
    _save(fig, "h5_pie_genero.png", verbose)


# ─────────────────────────────────────────────────────────────
# H5 — Bar agrupado: género × tipo de suscripción
# ─────────────────────────────────────────────────────────────
def _plot_h5_bar_gender_subs(df: pd.DataFrame, verbose: bool) -> None:
    pivot = (
        df.groupby(["gender", "subsc_type"], observed=True)
        .size()
        .reset_index(name="viajes")
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(
        data=pivot, x="gender", y="viajes", hue="subsc_type",
        palette=[PALETTE_MAIN, PALETTE_ACCENT], edgecolor="white",
        linewidth=0.5, ax=ax
    )
    ax.set_xlabel("Género")
    ax.set_ylabel("Total de viajes")
    ax.set_title("H5 — Viajes por género y tipo de suscripción", pad=15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(title="Tipo suscripción", frameon=False)
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h5_bar_genero_suscripcion.png", verbose)


# ─────────────────────────────────────────────────────────────
# H6 — Heatmap: time_of_day × day_type
# ─────────────────────────────────────────────────────────────
def _plot_h6_heatmap(df: pd.DataFrame, verbose: bool) -> None:
    order_time = ["Morning", "Afternoon", "Evening", "Night"]
    pivot = (
        df.groupby(["day_type", "time_of_day"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=order_time)
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(
        pivot, annot=True, fmt=",d", cmap="Blues",
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Total de viajes"},
        ax=ax
    )
    ax.set_xlabel("Momento del día")
    ax.set_ylabel("Tipo de día")
    ax.set_title("H6 — Distribución de viajes por momento del día y tipo de día", pad=15)
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=1.01)
    _save(fig, "h6_heatmap_tiempo.png", verbose)


# ─────────────────────────────────────────────────────────────
# H6 — Box plot: duration_min por time_of_day
# ─────────────────────────────────────────────────────────────
def _plot_h6_boxplot(df: pd.DataFrame, verbose: bool) -> None:
    order_time = ["Morning", "Afternoon", "Evening", "Night"]
    palette    = [PALETTE_TIME[t] for t in order_time]

    # Filtrar outliers extremos para que el gráfico sea legible (percentil 99)
    p99 = df["duration_min"].quantile(0.99)
    df_plot = df[df["duration_min"] <= p99]

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.boxplot(
        data=df_plot, x="time_of_day", y="duration_min",
        order=order_time, palette=palette,
        width=0.5, linewidth=1.2,
        flierprops={"marker": "o", "markersize": 2, "alpha": 0.3},
        ax=ax
    )
    ax.set_xlabel("Momento del día")
    ax.set_ylabel("Duración del viaje (minutos)")
    ax.set_title("H6 — Distribución de duración de viajes por momento del día\n(sin outliers extremos, percentil 99)", pad=15)
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h6_boxplot_duracion.png", verbose)


# ─────────────────────────────────────────────────────────────
# H7 — Line chart: viajes por mes a lo largo del tiempo
# ─────────────────────────────────────────────────────────────
def _plot_h7_line(df: pd.DataFrame, verbose: bool) -> None:
    monthly = (
        df.groupby(["year", "month", "day_type"], observed=True)
        .size()
        .reset_index(name="viajes")
    )
    monthly["periodo"] = pd.to_datetime(
        monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    for day_type, color in [("Weekday", PALETTE_MAIN), ("Weekend", PALETTE_ACCENT)]:
        subset = monthly[monthly["day_type"] == day_type].sort_values("periodo")
        ax.plot(subset["periodo"], subset["viajes"], marker="o", markersize=3,
                linewidth=2, color=color, label=day_type)

    ax.set_xlabel("Período (mes/año)")
    ax.set_ylabel("Total de viajes")
    ax.set_title("H7 — Evolución mensual de viajes: Weekday vs Weekend", pad=15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(title="Tipo de día", frameon=False)
    fig.autofmt_xdate(rotation=45)
    fig.suptitle("Hubway Bike Sharing", fontsize=10, color="#888", y=0.98)
    _save(fig, "h7_linea_mensual.png", verbose)


# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────
def _save(fig: plt.Figure, filename: str, verbose: bool) -> None:
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path)
    plt.close(fig)
    if verbose:
        print(f"  💾 {filename}")


# ─────────────────────────────────────────────────────────────
# Ejecución directa (testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.load_clean import load_clean
    from src.features   import build_features

    datasets = load_clean(verbose=False)
    datasets = build_features(datasets, verbose=False)
    run_plots(datasets, verbose=True)
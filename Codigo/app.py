import streamlit as st 
import pandas as pd
import time
import tracemalloc

from Knn import knn
from recomendacion import recomendacion
from incluencer import items_populares, items_no_vistos, crear_influencer
from main import cargar_datos

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Sistema Recomendador", layout="wide")

# ICONOS tipo dashboard (Font Awesome)
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

st.markdown("<h1><i class='fa-solid fa-film'></i> Sistema de Recomendación MovieLens</h1>", unsafe_allow_html=True)

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["Recomendador", "Complejidad"])

# ==========================================
# CARGA DATOS (MIDiendo RAM REAL)
# ==========================================
@st.cache_data
def load_data():
    inicio = time.time()
    tracemalloc.start()

    usuarios, nombres = cargar_datos("ratings.csv", "movies.csv")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    fin = time.time()

    return usuarios, nombres, fin - inicio, peak / (1024 * 1024)

usuarios_dict, mapeo_nombres, tiempo_carga, ram_uso = load_data()

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("<h3><i class='fa-solid fa-sliders'></i> Configuración</h3>", unsafe_allow_html=True)

user_id = st.sidebar.number_input(
    "Escribe el ID de usuario objetivo",
    min_value=1,
    max_value=max([k for k in usuarios_dict.keys() if isinstance(k, int)]),
    value=1
)

metrica = st.sidebar.selectbox(
    "Escoge la métrica",
    ["pearson", "coseno", "manhattan", "euclidiana"]
)

k = st.sidebar.slider("Elige el nro de vecinos (KNN)", 5, 30, 10)
min_v = st.sidebar.slider("Mín vecinos que vieron la película", 1, 10, 3)

# CONFIG INFLUENCER
st.sidebar.markdown("<h4><i class='fa-solid fa-robot'></i> Influencer</h4>", unsafe_allow_html=True)

top_populares = st.sidebar.slider("Nro de películas populares", 10, 100, 20)
num_no_vistos = st.sidebar.slider("Nro de películas que se agregan al influencer", 1, 10, 3)

# ==========================================
# TAB 1 - RECOMENDADOR
# ==========================================
with tab1:

    if st.button("Generar recomendaciones"):

        # SIN INFLUENCER
        vecinos = knn(user_id, usuarios_dict, k, metrica=metrica)

        propuestas = recomendacion(
            user_id, usuarios_dict, vecinos,
            min_vecinos=min_v, metrica=metrica
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h3><i class='fa-solid fa-users'></i> Vecinos</h3>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(vecinos, columns=["Usuario", "Score"]))

        with col2:
            st.markdown("<h3><i class='fa-solid fa-star'></i> Recomendaciones SIN influencer</h3>", unsafe_allow_html=True)

            data = []
            for m, p in propuestas[:10]:
                data.append({
                    "Película": mapeo_nombres.get(m),
                    "Predicción": round(p, 2)
                })
            df_sin = pd.DataFrame(data)
            st.dataframe(df_sin)

        # ======================================
        # INFLUENCER
        # ======================================
        st.markdown("<h3><i class='fa-solid fa-robot'></i> Influencer</h3>", unsafe_allow_html=True)

        populares = items_populares(usuarios_dict, top_populares)
        no_vistos = items_no_vistos(user_id, usuarios_dict, populares)
        nuevas = no_vistos[:num_no_vistos]

        st.write("Películas agregadas:")
        for m in nuevas:
            st.write("➕", mapeo_nombres.get(m))

        if "influencer" in usuarios_dict:
            del usuarios_dict["influencer"]

        influencer = crear_influencer(user_id, usuarios_dict, nuevas)
        usuarios_dict["influencer"] = influencer

        # CON INFLUENCER
        vecinos_inf = knn(user_id, usuarios_dict, k, metrica=metrica)

        propuestas_inf = recomendacion(
            user_id, usuarios_dict, vecinos_inf,
            min_vecinos=min_v, metrica=metrica
        )

        st.markdown("<h3><i class='fa-solid fa-rocket'></i> Recomendaciones CON influencer</h3>", unsafe_allow_html=True)

        data_inf = []
        for m, p in propuestas_inf[:10]:
            data_inf.append({
                "Película": mapeo_nombres.get(m),
                "Predicción": round(p, 2)
            })

        df_con = pd.DataFrame(data_inf)
        st.dataframe(df_con)

        # COMPARACIÓN
        st.markdown("<h3><i class='fa-solid fa-chart-bar'></i> Comparación</h3>", unsafe_allow_html=True)

        top_sin = [x[0] for x in propuestas[:10]]
        top_con = [x[0] for x in propuestas_inf[:10]]

        nuevas_rec = set(top_con) - set(top_sin)

        if nuevas_rec:
            st.success("Nuevas recomendaciones:")
            for m in nuevas_rec:
                st.write("✨", mapeo_nombres.get(m))
        else:
            st.warning("No hubo nuevas recomendaciones.")

        # Cambios ranking
        cambios = []
        ranking_sin = {item: i for i, item in enumerate(top_sin)}
        ranking_con = {item: i for i, item in enumerate(top_con)}

        for item in top_con:
            if item in ranking_sin:
                cambio = ranking_sin[item] - ranking_con[item]
                if cambio != 0:
                    cambios.append({
                        "Película": mapeo_nombres.get(item),
                        "Cambio": cambio
                    })

        if cambios:
            st.markdown("<h4><i class='fa-solid fa-arrow-up-right-dots'></i> Cambios en ranking</h4>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(cambios))

# ==========================================
# TAB 2 - COMPLEJIDAD (SIN PSUTIL)
# ==========================================
with tab2:

    st.markdown("<h2><i class='fa-solid fa-chart-line'></i> Complejidad Computacional</h2>", unsafe_allow_html=True)

    metricas_eval = st.multiselect(
        "Selecciona métricas:",
        ["pearson", "coseno", "manhattan", "euclidiana"],
        default=["pearson", "coseno"]
    )

    if st.button("Ejecutar análisis"):

        resultados = {}
        tiempos = {}

        for metrica_eval in metricas_eval:

            tracemalloc.start()
            t0 = time.time()

            usuarios_tmp, nombres_tmp = cargar_datos("ratings.csv", "movies.csv")

            tiempo_carga = time.time() - t0
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            ram_usada = peak / (1024 * 1024)

            user_eval = list(usuarios_tmp.keys())[0]

            t0 = time.time()
            vecinos = knn(user_eval, usuarios_tmp, k, metrica=metrica_eval)
            t_knn = time.time() - t0

            t0 = time.time()
            recomendaciones = recomendacion(
                user_eval, usuarios_tmp, vecinos,
                min_vecinos=min_v, metrica=metrica_eval
            )
            t_rec = time.time() - t0

            tiempo_total = tiempo_carga + t_knn + t_rec

            resultados[metrica_eval] = {
                "Usuarios": len(usuarios_tmp),
                "Películas": len(nombres_tmp),
                "Carga dataset (s)": round(tiempo_carga, 4),
                "RAM usada (MB)": round(ram_usada, 2),
                "Similitud (s)": round(t_knn, 4),
                "Recomendación (s)": round(t_rec, 4),
                "Total (s)": round(tiempo_total, 4)
            }

            tiempos[metrica_eval] = tiempo_total

        st.subheader("Resultados")
        df = pd.DataFrame(resultados)
        st.dataframe(df)

        st.subheader("Comparación tiempos")
        st.bar_chart(tiempos)
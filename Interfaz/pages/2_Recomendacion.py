import streamlit as st
from Codigo.data_loader import cargar_all_users, cargar_movies
from Codigo.Knn import knn
from Codigo.recomendacion import recomendacion

st.title("Sistema de Recomendación")

all_users = cargar_all_users("Codigo/ratings.csv")
movies = cargar_movies("Codigo/movies.csv")

user_id = st.number_input("Usuario", min_value=1, step=1)
k = st.slider("Vecinos", 1, 20, 5)
min_vecinos = st.slider("Umbral mínimo", 1, 10, 3)
metrica = st.selectbox("Métrica", ["pearson", "coseno", "manhattan", "euclidiana"])

if st.button("Recomendar"):

    vecinos, _ = knn(user_id, all_users, k=k, metrica=metrica)

    recs = recomendacion(user_id, all_users, vecinos, min_vecinos, metrica)

    st.subheader("Recomendaciones")

    if not recs:
        st.warning("No hay recomendaciones suficientes")
    else:
        for movie_id, score in recs:
            titulo = movies.get(movie_id, movie_id)
            st.write(f"{titulo} → ⭐ {score:.2f}")
import streamlit as st
from Codigo.data_loader import cargar_all_users, cargar_movies
from Codigo.Knn import knn
from Codigo.influencer import ranking_influencer

st.title("Influencer Ranking")

all_users = cargar_all_users("Codigo/ratings.csv")
movies = cargar_movies("Codigo/movies.csv")

user_id = st.number_input("Usuario", min_value=1, step=1)
k = st.slider("Vecinos", 1, 20, 5)
metrica = st.selectbox("Métrica", ["pearson", "coseno", "manhattan", "euclidiana"])

if st.button("Calcular Influencer"):

    vecinos = knn(user_id, all_users, k=k, metrica=metrica)

    ranking = ranking_influencer(user_id, all_users, vecinos, movies)

    st.subheader("Ranking de influencia")

    for i, (movie_id, data) in enumerate(ranking[:10], start=1):
        titulo = movies.get(movie_id, movie_id)
        st.write(f"{i}. {titulo} → ⭐ {data['total']:.2f}")
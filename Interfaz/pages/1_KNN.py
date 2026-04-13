import streamlit as st
from Codigo.data_loader import cargar_all_users
from Codigo.Knn import knn

st.title("Algoritmo KNN")

all_users = cargar_all_users("Codigo/ratings.csv")

user_id = st.number_input("Usuario objetivo", min_value=1, step=1)
k = st.slider("Número de vecinos (K)", 1, 20, 5)
metrica = st.selectbox("Métrica", ["pearson", "coseno", "manhattan", "euclidiana"])

if st.button("Ejecutar KNN"):

    vecinos, distancias = knn(user_id, all_users, k=k, metrica=metrica)

    # TODOS los usuarios ordenados
    st.subheader(" Orden completo de usuarios")
    for u, score in distancias:
        st.write(f"Usuario {u} → {score:.4f}")

    # TOP K vecinos
    st.subheader(f"Top {k} vecinos más cercanos")
    for u, score in vecinos:
        st.write(f"Usuario {u} → {score:.4f}")
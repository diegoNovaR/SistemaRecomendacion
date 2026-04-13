import streamlit as st
import io
import sys

from Codigo.complejidad_computacional import main

st.title("Complejidad Computacional")

if st.button("Ejecutar análisis"):

    st.info("Ejecutando análisis completo...")

    # Capturar prints SIN modificar tu código
    buffer = io.StringIO()
    sys.stdout = buffer

    try:
        main()
    finally:
        sys.stdout = sys.__stdout__

    salida = buffer.getvalue()

    # Separar por secciones reales del texto
    partes = salida.split("════════════════════════════════════════════════════════════")

    st.subheader("Resultados organizados")

    for i, parte in enumerate(partes):
        if parte.strip():
            st.markdown(f"### Sección {i+1}")
            st.code(parte.strip())
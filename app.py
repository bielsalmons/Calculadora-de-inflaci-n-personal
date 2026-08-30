import requests
import pandas as pd
import streamlit as st

st.title("📊Inflación por subclase (IPC)")
st.write("Consulta la variación anual de los precios por categoría.")

def cargar_datos():
    URL= "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/79184?date=20260701:"
    datos=requests.get(URL).json()

    registros= []

    for serie in datos:
        if "Variación anual" in serie["Nombre"]:

            nombre_limpio=(serie["Nombre"].replace("Nacional. ", "").replace(". Variación anual. ", "").strip())
            valor = serie["Data"][0]["Valor"]

            registros.append({"Categoria": nombre_limpio,"Valor": valor})
    return pd.DataFrame(registros)
df = cargar_datos()
categoria_seleccionada = st.selectbox(
    "Selecciona una categoría de gasto:", df["Categoria"].unique()
)
dato = df[df["Categoria"] == categoria_seleccionada].iloc[0]
valor_inflacion = dato["Valor"]

# --- 3. MOSTRAR RESULTADO ---
st.divider()

# Mostrar la cifra formateada en una tarjeta limpia (Metric)
st.metric(
    label=f"Inflación anual para: {categoria_seleccionada}",
    value=f"{valor_inflacion} %",
    delta=f"{valor_inflacion} %",
    delta_color="inverse",  # Si sube la inflación, lo muestra en rojo
)


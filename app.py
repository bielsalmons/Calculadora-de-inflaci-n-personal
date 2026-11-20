import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Inflación y poder adquisitivo", page_icon="📊")
st.title("📊 Inflación por subclase (IPC)")
st.write(
    "Añade gastos por categoría para guardarlos en una tabla y ver el total acumulado y la pérdida de poder adquisitivo."
)


@st.cache_data(ttl=3600)
def cargar_datos():
    url = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/79184?date=20260701"
    respuesta = requests.get(url, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()

    registros = []
    for serie in datos:
        if "Variación anual" in serie.get("Nombre", ""):
            nombre_limpio = (
                serie["Nombre"]
                .replace("Nacional. ", "")
                .replace(". Variación anual. ", "")
                .strip()
            )
            obs = serie.get("Data", [])
            if obs and obs[0].get("Valor") is not None:
                registros.append(
                    {
                        "Categoria": nombre_limpio,
                        "Valor": float(obs[0]["Valor"]),
                    }
                )
    return pd.DataFrame(registros)


# Inicializar historial de gastos en session_state
if "gastos" not in st.session_state:
    st.session_state.gastos = []

df_ine = cargar_datos()

# --- 1. FORMULARIO PARA AÑADIR UN GASTO ---
with st.form("form_gasto", clear_on_submit=True):
    categoria_seleccionada = st.selectbox(
        "Selecciona una categoría de gasto:",
        df_ine["Categoria"].unique(),
    )
    gasto_actual = st.number_input(
        "Introduce el gasto (€):",
        min_value=0.0,
        value=50.0,
        step=1.0,
        format="%.2f",
    )
    enviado = st.form_submit_button("➕ Añadir gasto")

if enviado and gasto_actual > 0:
    inflacion = float(
        df_ine[df_ine["Categoria"] == categoria_seleccionada].iloc[0]["Valor"]
    )
    factor = 1 + (inflacion / 100)
    valor_hace_un_ano = gasto_actual / factor if factor != 0 else gasto_actual
    perdida_euros = gasto_actual - valor_hace_un_ano

    st.session_state.gastos.append(
        {
            "Categoria": categoria_seleccionada,
            "Gasto actual (€)": round(gasto_actual, 2),
            "Inflación (%)": round(inflacion, 2),
            "Equivalente hace 1 año (€)": round(valor_hace_un_ano, 2),
            "Pérdida poder adquisitivo (€)": round(perdida_euros, 2),
        }
    )

# --- 2. DATAFRAME ACUMULADO Y FILA TOTAL ABAJO ---
st.divider()
st.subheader("Registro de gastos")

if st.session_state.gastos:
    df_gastos = pd.DataFrame(st.session_state.gastos)

    total_gasto = df_gastos["Gasto actual (€)"].sum()
    total_hace_un_ano = df_gastos["Equivalente hace 1 año (€)"].sum()
    total_perdida = df_gastos["Pérdida poder adquisitivo (€)"].sum()
    inflacion_media = df_gastos["Inflación (%)"].mean()

    fila_total = pd.DataFrame(
        [
            {
                "Categoria": "TOTAL",
                "Gasto actual (€)": round(total_gasto, 2),
                "Inflación (%)": round(inflacion_media, 2),
                "Equivalente hace 1 año (€)": round(total_hace_un_ano, 2),
                "Pérdida poder adquisitivo (€)": round(total_perdida, 2),
            }
        ]
    )

    df_con_total = pd.concat([df_gastos, fila_total], ignore_index=True)
    st.dataframe(df_con_total, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gasto total actual", f"{total_gasto:.2f} €")
    with col2:
        st.metric("Equivalente total hace 1 año", f"{total_hace_un_ano:.2f} €")
    with col3:
        st.metric("Pérdida total de poder adquisitivo", f"{total_perdida:.2f} €")

    if st.button("🗑️ Borrar todos los gastos"):
        st.session_state.gastos = []
        st.rerun()
else:
    st.info("Todavía no has añadido ningún gasto. Usa el formulario de arriba para empezar.")

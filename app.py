import requests
import pandas as pd
import streamlit as st

st.title("📊 Calculadora de Inflación Personal")
st.write(
    "Selecciona un grupo y una categoría para consultar el dato de inflación más reciente."
)

NOMBRES_GRUPOS = {
    "00": "Índice general",
    "01": "01 Alimentos y bebidas no alcohólicas",
    "02": "02 Bebidas alcohólicas y tabaco",
    "03": "03 Vestido y calzado",
    "04": "04 Vivienda, agua, electricidad, gas y otros combustibles",
    "05": "05 Muebles, artículos del hogar y artículos para el mantenimiento corriente del hogar",
    "06": "06 Sanidad",
    "07": "07 Transporte",
    "08": "08 Información y comunicaciones",
    "09": "09 Actividades recreativas, deporte y cultura",
    "10": "10 Enseñanza",
    "11": "11 Restaurantes y servicios de alojamiento",
    "12": "12 Seguros y servicios financieros",
    "13": "13 Cuidado personal, protección social, y bienes y servicios diversos",
}

def cargar_datos():
    URL="https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/79184?date=20260701:"
    URL2="https://servicios.ine.es/wstempus/js/ES/VALORES_GRUPOSTABLA/79184/161050"

    datos=requests.get(URL).json()
    datosgrupos=requests.get(URL2).json()
    tablagrupos=[]
    for elemento in datosgrupos:
       Nombre=elemento["Nombre"]
       Grupo=elemento["Codigo"][:2]
       tablagrupos.append({"Nombre":Nombre,"Grupo":Grupo})

    dfgrupos=pd.DataFrame(tablagrupos)

    tabla=[]

    for serie in datos:
        if "Variación anual" in serie["Nombre"]:
            valor=serie["Data"][0]["Valor"]
            Categoria=serie["Nombre"].replace("Nacional. ", "").replace(". Variación anual.", "").strip()
            Mes= serie["Data"][0]["FK_Periodo"]
            Año= serie["Data"][0]["Anyo"]
            tabla.append({"Categoria":Categoria,"Valor":valor,"Mes":Mes,"Año":Año})


    df=pd.DataFrame(tabla)
    dfgrupos["Nombre"] = dfgrupos["Nombre"].str.strip()


    df_final= pd.merge(df,dfgrupos,left_on="Categoria", right_on="Nombre", how="left")
    df_final = df_final.drop(columns=["Nombre"])
    df_final["Nombre_Grupo"] = df_final["Grupo"].map(NOMBRES_GRUPOS)
    return df_final

df_final=cargar_datos()

# 2. Mostramos en el selectbox los nombres amigables de los grupos
lista_grupos = sorted(df_final["Nombre_Grupo"].dropna().unique())

# 1. Tu primer selector con st.segmented_control
grupo_seleccionado = st.segmented_control(
    "Selecciona el grupo de gasto:", lista_grupos
)

# Comprobamos que el usuario haya seleccionado un grupo antes de continuar
if grupo_seleccionado:

    # 2. Filtrar el DataFrame según el grupo que ha pinchado el usuario
    df_grupo = df_final[df_final["Nombre_Grupo"] == grupo_seleccionado]

    # 3. Obtener la lista de subclases de ese grupo específico
    lista_subclases = sorted(df_grupo["Categoria"].unique())

    # 4. Segundo selector (selectbox es ideal aquí porque hay muchas subclases)
    subclase_seleccionada = st.selectbox(
        "Selecciona la subclase concreta:", lista_subclases
    )

# 5. Buscamos la fila correspondiente a la subclase seleccionada
    datos_subclase = df_grupo[df_grupo["Categoria"] == subclase_seleccionada]

    # Obtenemos los valores de esa fila
    inflacion = datos_subclase["Valor"].values[0]
    mes = datos_subclase["Mes"].values[0]
    anyo = datos_subclase["Año"].values[0]

    st.divider()  # Línea separadora visual

    # 6. Mostramos el dato de inflación en destacado
    st.metric(
        label=f"Inflación anual: {subclase_seleccionada}",
        value=f"{inflacion} %",
        delta=f"{inflacion} %",
        delta_color="inverse",  # Si sube se muestra en rojo (negativo para la cartera)
    )

    st.caption(f"📅 Dato más reciente de la API: Mes {mes} del año {anyo}")

print(df_final)
                




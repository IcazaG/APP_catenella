import streamlit as st
import folium
from folium import Polygon, PolyLine, Marker, Icon
from streamlit_folium import st_folium
import shapely.geometry as geom
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración de página
st.set_page_config(
    page_title="Monitoreo Alexandrium catenella",
    page_icon="🌊",
    layout="wide"
)

# Estilo básico
st.markdown("""
<style>
    .title {
        color: #1E5162;
        font-size: 2rem;
        text-align: center;
    }
    .subtitle {
        color: #1E5162;
        background-color: #E6F2F5;
        padding: 5px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Título de la aplicación
st.markdown("<h1 class='title'>🌊 Programa de Vigilancia Alexandrium catenella</h1>", unsafe_allow_html=True)
st.markdown("Sistema de monitoreo de áreas restringidas para control de Marea Roja")

# Definir los puntos de restricción (coordenadas)
coords = [
    (-73.114044, -43.435339),
    (-73.042636, -43.568214),
    (-73.043861, -43.642142),
    (-73.058528, -43.734786),
    (-73.198778, -43.734714),
    (-73.513663, -43.664611),
    (-73.428572, -43.440469),
    (-73.114044, -43.435339)  # Cierra el polígono
]

# Crear polígono con shapely para intersecciones
polygon = geom.Polygon(coords)

# Función para convertir grados y minutos decimales a decimal
def gm_to_decimal(degrees, minutes, direction):
    decimal = abs(degrees) + abs(minutes) / 60
    if (direction in ["S", "W"]) or degrees < 0:
        decimal = -decimal
    return decimal

# Calcular línea de "cierre compuertas"
cierre_compuertas_lat = gm_to_decimal(43, 34.883, "S")

# Crear datos simulados para dashboard
def generar_datos_simulados():
    # Generar 30 días de datos
    fechas = [datetime.now() - timedelta(days=i) for i in range(30)]
    fechas = sorted(fechas)
    
    # Estaciones de monitoreo simuladas
    estaciones = ["Estación A", "Estación B", "Estación C", "Estación D"]
    
    datos = []
    for fecha in fechas:
        for estacion in estaciones:
            # Simulamos distintos niveles de concentración
            nivel = random.randint(0, 200)
            riesgo = "Alto" if nivel > 100 else "Medio" if nivel > 50 else "Bajo"
            
            datos.append({
                "fecha": fecha,
                "estacion": estacion,
                "concentracion": nivel,
                "nivel_riesgo": riesgo
            })
    
    return pd.DataFrame(datos)

# Generar datos simulados
df_monitoreo = generar_datos_simulados()

# Inicializar variables para el estado de la sesión
if 'lat' not in st.session_state:
    st.session_state.lat = -43.5
if 'lng' not in st.session_state:
    st.session_state.lng = -73.1
if 'show_marker' not in st.session_state:
    st .session_state.show_marker = False 

# Crear layout en columnas
col1, col2 = st.columns([1, 1.5])

# Columna 1: Formularios y controles
with col1:
    st.markdown("<h3 class='subtitle'>📍 Verificar Coordenadas</h3>", unsafe_allow_html=True)
    
    with st.form("check_form"):
        lat_deg = st.number_input("Grados de Latitud:", value=-43)
        lat_min = st.number_input("Minutos de Latitud:", value=30.0)
        lng_deg = st.number_input("Grados de Longitud:", value=-73)
        lng_min = st.number_input("Minutos de Longitud:", value=10.0)
        submit = st.form_submit_button("Verificar Coordenada")

    if submit:
        lat = gm_to_decimal(lat_deg, lat_min, "S")
        lng = gm_to_decimal(lng_deg, lng_min, "W")
        point = geom.Point(lng, lat)
        if polygon.contains(point):
            st.error("⚠️ ¡Alerta! La coordenada está dentro del área restringida.")
        else:
            st.success("✅ La coordenada está fuera del área restringida.")
        
        # Guardar coordenadas en el estado de sesión
        st.session_state.lat = lat
        st.session_state.lng = lng
        st.session_state.show_marker = True

# Columna 2: Mapa y gráfico
with col2:
    st.markdown("<h3 class='subtitle'>🗺️ Mapa de Monitoreo</h3>", unsafe_allow_html=True)
    
    # Crear mapa
    m = folium.Map(location=[-43.5, -73.1], zoom_start=8)
    folium.Polygon(locations=coords, color='blue', fill=True, fill_opacity=0.2).add_to(m)
    
    # Añadir marcador si hay coordenadas
    if st.session_state.show_marker:
        folium.Marker(
            location=[st.session_state.lat, st.session_state.lng],
            popup="Ubicación Ingresada",
            icon=folium.Icon(color='red')
        ).add_to(m)
    
    # Mostrar mapa en Streamlit
    st_folium(m, width=700, height=500)

    st.markdown("<h3 class='subtitle'>📊 Gráfico de Concentraciones</h3>", unsafe_allow_html=True)
    
    # Gráfico de concentraciones
    fig = px.line(df_monitoreo, x='fecha', y='concentracion', color='estacion', title='Concentración de Alexandrium catenella')
    st.plotly_chart(fig)

# Finalizar la aplicación
if __name__ == "__main__":
    st.write("Aplicación de monitoreo en funcionamiento.")

import streamlit as st
import folium
from folium import Polygon, PolyLine
from streamlit_folium import st_folium
import shapely.geometry as geom

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

# Función para convertir DMS a decimal
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal

# Calcular línea de "cierre compuertas"
cierre_compuertas_lat = dms_to_decimal(43, 34, 53, "S")

st.title("Programa de Vigilancia Alexandrium catenella")

# Formulario para ingresar lat/lng
with st.form("check_form"):
    lat = st.number_input("Latitud:", value=-43.5)
    lng = st.number_input("Longitud:", value=-73.1)
    submit = st.form_submit_button("Verificar Coordenada")

if submit:
    point = geom.Point(lng, lat)
    if polygon.contains(point):
        st.error("¡Alerta! La coordenada está dentro del área restringida.")
    else:
        st.success("La coordenada está fuera del área restringida.")

# Formulario para conversión DMS a decimal
with st.form("convert_form"):
    st.write("Conversión de DMS a Decimal:")
    dms_deg = st.number_input("Grados:", value=0)
    dms_min = st.number_input("Minutos:", value=0)
    dms_sec = st.number_input("Segundos:", value=0)
    dms_dir = st.selectbox("Dirección:", ["N", "S", "E", "W"])
    convert = st.form_submit_button("Convertir")

if convert:
    decimal_coord = dms_to_decimal(dms_deg, dms_min, dms_sec, dms_dir)
    st.info(f"Coordenada Decimal: {decimal_coord}")

# Crear el mapa Folium
m = folium.Map(location=[-43.5, -73.2], zoom_start=9)

# Agregar polígono
Polygon(locations=[(y, x) for x, y in coords], color='red', weight=2, fill_opacity=0.4).add_to(m)

# Agregar línea de cierre de compuertas
PolyLine(
    locations=[[cierre_compuertas_lat, -74], [cierre_compuertas_lat, -72]],
    color='blue',
    weight=2
).add_to(m)

st_folium(m, width=700, height=500)

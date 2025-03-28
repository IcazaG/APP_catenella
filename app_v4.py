# Importar librerías necesarias
import streamlit as st
import folium
from folium import Polygon, PolyLine, Marker, Icon
from streamlit_folium import st_folium
import shapely.geometry as geom
import pandas as pd
import plotly.express as px

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
cierre_compuertas_lat = gm_to_decimal(43, 34.88, "S")

# Intentar leer datos desde el archivo plotly_resultados.csv
try:
    # Leer el archivo CSV con punto y coma como separador
    df_resultados = pd.read_csv('plotly_resultados.csv', sep=';')
    
    # Normalizar nombres de columnas
    df_resultados.columns = [col.lower().strip() for col in df_resultados.columns]
    
    # Convertir año y mes a numérico
    df_resultados['año'] = pd.to_numeric(df_resultados['año'], errors='coerce')
    df_resultados['mes'] = pd.to_numeric(df_resultados['mes'], errors='coerce')
    
    # Mapear meses numéricos a nombres
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df_resultados['nombre_mes'] = df_resultados['mes'].map(meses_nombres)
    
    # Crear columna de resultado normalizado
    df_resultados['resultado_normalizado'] = df_resultados['resultado'].str.strip().str.upper()

    # Filtrar datos por año seleccionado
    año_seleccionado = st.selectbox("Selecciona el año:", df_resultados['año'].dropna().unique())
    df_filtrado = df_resultados[df_resultados['año'] == año_seleccionado]

    # Contar casos positivos y negativos por mes
    conteo_mensual = df_filtrado.groupby('nombre_mes')['resultado_normalizado'].value_counts().unstack(fill_value=0)
    conteo_mensual = conteo_mensual.reindex(meses_nombres.values(), fill_value=0)  # Asegurar que todos los meses estén presentes

except FileNotFoundError:
    st.error("No se encontró el archivo de datos 'plotly_resultados.csv'")
    conteo_mensual = pd.DataFrame(columns=['Positivo', 'Negativo'])
except Exception as e:
    st.error(f"Error al procesar el archivo CSV: {e}")
    conteo_mensual = pd.DataFrame(columns=['Positivo', 'Negativo'])

# Inicializar variables para el estado de la sesión
if 'lat' not in st.session_state:
    st.session_state.lat = -43.5
if 'lng' not in st.session_state:
    st.session_state.lng = -73.1
if 'show_marker' not in st.session_state:
    st.session_state.show_marker = False 

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
    
    # Añadir línea de cierre de compuertas
    folium.Marker(
        location=[cierre_compuertas_lat, -73.1],  # Longitud de ejemplo
        popup="Cierre de Compuertas",
        icon=folium.Icon(color='green')
    ).add_to(m)

    # Añadir línea punteada en la coordenada 43° 34.88' S
    folium.PolyLine(
        locations=[(cierre_compuertas_lat, -75.5), (cierre_compuertas_lat, -72.5)],
        color='red',
        weight=2,
        dash_array='5, 5'  # Estilo de línea punteada
    ).add_to(m)

    # Añadir marcador si hay coordenadas
    if st.session_state.show_marker:
        folium.Marker(
            location=[st.session_state.lat, st.session_state.lng],
            popup="Ubicación Ingresada",
            icon=folium.Icon(color='red')
        ).add_to(m)
    
    # Mostrar mapa en Streamlit
    st_folium(m, width=700, height=500)

    st.markdown("<h3 class='subtitle'>📊 Casos Positivos y Negativos por Mes</h3>", unsafe_allow_html=True)
    
    # Verificar si hay datos disponibles
    if not conteo_mensual.empty:
        # Gráfico de barras
        fig = px.bar(
            conteo_mensual.reset_index(), 
            x='nombre_mes', 
            y=conteo_mensual.columns,
            title='Casos Positivos y Negativos por Mes',
            labels={'nombre_mes': 'Mes', 'value': 'Número de Casos'},
            barmode='group'
        )
        
        # Personalizar el diseño
        fig.update_layout(
            xaxis_title='Mes',
            yaxis_title='Número de Casos',
            height=400,
            width=700
        )
        
        st.plotly_chart(fig)
        
        # Tabla de resumen
        st.markdown("### Resumen de Casos por Mes")
        st.dataframe(conteo_mensual)
    else:
        st.warning("No hay datos disponibles para mostrar.")

# Finalizar la aplicación
if __name__ == "__main__":
    st.write("Aplicación de monitoreo en funcionamiento.")
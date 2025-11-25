import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

#Configuracion y conexion
st.set_page_config(page_title="Cubo OLAP", layout="wide")

#Conexion a la base de datos (projectsupportdb)
db_connection_str = 'mysql+pymysql://root:@localhost/projectsupportdb'
db_connection = create_engine(db_connection_str)

#2. ETL (Extracción y Transformación)
@st.cache_data
def load_data():
    try:
        #Leemos la Tabla de Hechos
        fact_project = pd.read_sql("SELECT * FROM fact_project", db_connection)

        #Leemos las Dimensiones
        dim_client = pd.read_sql("SELECT * FROM dim_client", db_connection)
        dim_area = pd.read_sql("SELECT * FROM dim_area", db_connection)
        dim_time = pd.read_sql("SELECT * FROM dim_time", db_connection) 
        
        #Unimos todo (JOIN) para formar el CUBO
        #Unir Cliente
        df = fact_project.merge(dim_client, on="idClient") 
        
        #Unir Área
        df = df.merge(dim_area, on="idArea")
        
        #Unir Tiempo
        df = df.merge(dim_time, on="idTime")

        return df

    except Exception as e:
        st.error(f"Error en la carga de datos del Data Warehouse: {e}")
        return pd.DataFrame()

#Cargar datos
df = load_data()

#Si falla la carga, detenemos la app
if df.empty:
    st.stop()

#Interfaz de usuario
st.title("Cubo OLAP Dinámico")
#st.markdown(f"""
#**Base de Datos Conectada:** `projectsupportdb`  
#**Hechos:** `fact_project` | **Dimensiones:** `dim_client`, `dim_area`, `dim_time`
#""")

#Selector de Operación OLAP
operacion = st.selectbox(
    "Selecciona operacion OLAP:",
    ["Cubo Base (Vista 3D)", "Slice (Rebanar)", "Dice (Sub-cubo)", "Roll-up (Agrupar)", "Drill-down (Desglosar)"]
)

st.markdown("---")

#Validar nombres de columnas para visualización
col_cliente = 'nameClient' if 'nameClient' in df.columns else df.columns[0]
col_area = 'nameArea' if 'nameArea' in df.columns else df.columns[1]
col_costo = 'cost'
col_anio = 'Year' if 'Year' in df.columns else 'year'

#Visualizacion del cubo OLAP

#Cubo Base (3D)
if operacion == "Cubo Base (Vista 3D)":
    st.subheader("Intersección: Cliente x Área x Tiempo")
    try:
        fig = px.scatter_3d(
            df, 
            x=col_cliente, 
            y=col_area, 
            z=col_anio,
            size=col_costo, 
            color=col_area,
            opacity=0.8,
            title="Cubo OLAP: Distribución Espacial de Costos"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Faltan columnas para el 3D: {e}")

#Slice (Rebanar)
elif operacion == "Slice (Rebanar)":
    st.subheader("Slice: Corte transversal por un Año específico")
    
    years_disponibles = sorted(df[col_anio].unique())
    slice_val = st.selectbox("Selecciona el Año:", years_disponibles)
    
    #Filtro
    df_slice = df[df[col_anio] == slice_val]
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df_slice, x=col_cliente, y=col_costo, color=col_area, 
                     title=f"Costos por Cliente (Año {slice_val})")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.sunburst(df_slice, path=[col_area, col_cliente], values=col_costo,
                           title=f"Desglose por Área (Año {slice_val})")
        st.plotly_chart(fig2, use_container_width=True)

#Dice (Dados)
elif operacion == "Dice (Sub-cubo)":
    st.subheader("Dice: Filtrado multidimensional simultáneo")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        filtro_cli = st.multiselect("Clientes:", df[col_cliente].unique(), default=df[col_cliente].unique()[:2])
    with c2:
        filtro_area = st.multiselect("Áreas:", df[col_area].unique(), default=df[col_area].unique()[:2])
    with c3:
        filtro_anio = st.multiselect("Años:", df[col_anio].unique(), default=df[col_anio].unique())
        
    #Aplicar filtros
    df_dice = df[
        (df[col_cliente].isin(filtro_cli)) & 
        (df[col_area].isin(filtro_area)) & 
        (df[col_anio].isin(filtro_anio))
    ]
    
    st.metric("Total Costo Sub-Cubo", f"${df_dice[col_costo].sum():,.2f}")
    
    if not df_dice.empty:
        fig = px.scatter_3d(df_dice, x=col_cliente, y=col_area, z=col_anio, size=col_costo, color=col_area)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos en esta intersección.")

#Roll-up (Agrupar)
elif operacion == "Roll-up (Agrupar)":
    st.subheader("Roll-up: Agregación de datos (Zoom Out)")
    
    nivel = st.radio("Agrupar por:", ["Área Geográfica", "Año Fiscal"], horizontal=True)
    
    if nivel == "Área Geográfica":
        df_roll = df.groupby(col_area)[col_costo].sum().reset_index()
        eje_x = col_area
    else:
        df_roll = df.groupby(col_anio)[col_costo].sum().reset_index()
        eje_x = col_anio
        
    fig = px.bar(df_roll, x=eje_x, y=col_costo, text_auto='.2s', color=col_costo,
                 title=f"Visión Resumida por {nivel}")
    st.plotly_chart(fig, use_container_width=True)

#Drill-down (Desglosar)
elif operacion == "Drill-down (Desglosar)":
    st.subheader("Drill-down: Profundizar en la jerarquía")
    st.info("Jerarquía: Área -> Cliente -> Proyecto")
    
    col_proy = 'nameProject' if 'nameProject' in df.columns else 'idFact_Project'
    
    fig = px.treemap(df, path=[col_area, col_cliente, col_proy], values=col_costo,
                     color=col_costo, title="Mapa de Árbol de Costos")
    st.plotly_chart(fig, use_container_width=True)
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

#Configuración de la página
st.set_page_config(page_title="BSC - Visión Estratégica", layout="wide", initial_sidebar_state="expanded")

#Estilo CSS
st.markdown("""
<style>
    .vision-box {
        background-color: #262730; 
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #ff4b4b; 
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .vision-box h3 {
        color: #ff4b4b !important;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

#Conexión a la base de datos
db_connection_str = 'mysql+pymysql://root:@localhost/projectsupportdb'
db_connection = create_engine(db_connection_str)

@st.cache_data
def get_strategic_data():
    try:
        # A) Cargamos HECHOS y TIEMPO
        df_fact = pd.read_sql("SELECT * FROM fact_project", db_connection)
        df_time = pd.read_sql("SELECT * FROM dim_time", db_connection)
        
        # B) Cargamos TALENTO
        df_emp = pd.read_sql("SELECT * FROM dim_employee", db_connection)
        df_exp = pd.read_sql("SELECT * FROM dim_experience", db_connection)
        
        df_merged = df_fact.merge(df_time, on="idTime")
        df_talento = df_emp.merge(df_exp, on="idExperience")
        
        return df_merged, df_talento
        
    except Exception as e:
        st.error(f"Error de conexión o mezcla de datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

#Cargar datos iniciales (Dataframes completos)
df_full, df_talento_full = get_strategic_data()

if df_full.empty:
    st.stop()

#Filtro de año
st.sidebar.header("Filtros Estratégicos")
col_anio = 'Year' if 'Year' in df_full.columns else 'year' 
if col_anio in df_full.columns:
    years_list = sorted(df_full[col_anio].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Selecciona el Año a evaluar:", years_list)
    df_filtered = df_full[df_full[col_anio] == selected_year]
    empleados_activos_ids = df_filtered['idEmployee'].unique()
    df_talento_filtered = df_talento_full[df_talento_full['idEmployee'].isin(empleados_activos_ids)]
else:
    st.warning("No se encontró columna de Año. Mostrando histórico completo.")
    df_filtered = df_full
    df_talento_filtered = df_talento_full
    selected_year = "Histórico"

st.sidebar.markdown("---")
st.sidebar.info(f"Mostrando estrategia para: **{selected_year}**")

#Cálculo de OKRs (Con datos filtrados)
if df_filtered.empty:
    st.warning(f"No hay datos registrados para el año {selected_year}.")
    st.stop()

#F1: Financiera
total_budget = df_filtered['budget'].sum()
total_cost = df_filtered['cost'].sum()
# Evitar división por cero
margen_real = ((total_budget - total_cost) / total_budget) * 100 if total_budget > 0 else 0
target_margen = 25.0

#C1: Clientes
total_clientes_activos = df_filtered['idClient'].nunique()
target_clientes = 15 # Ajustamos meta anual (quizás 30 era histórica, 15 anual es razonable)

#P1: Procesos
proyectos_eficientes = df_filtered[df_filtered['cost'] <= df_filtered['budget']].shape[0]
total_proyectos = df_filtered.shape[0]
porcentaje_eficiencia = (proyectos_eficientes / total_proyectos) * 100 if total_proyectos > 0 else 0
target_eficiencia = 85.0

#A1: Aprendizaje (Usando talento activo en ese año)
if 'experience' in df_talento_filtered.columns:
    expertos = df_talento_filtered[df_talento_filtered['experience'].isin(['Senior', 'Semi-Senior', 'Experto'])].shape[0]
    total_empleados = df_talento_filtered.shape[0]
    ratio_talento = (expertos / total_empleados) * 100 if total_empleados > 0 else 0
else:
    ratio_talento = 0

#Visualización del Dashboard

st.title(f"Balanced Scorecard: Estrategia {selected_year}")

# Mostrar la Visión
st.markdown("""
<div class="vision-box">
    <h3>Visión Corporativa</h3>
    "Ser una empresa líder en el desarrollo de software inteligente... aspiramos a consolidarnos como un referente 
    donde la analítica de desempeño y la gestión del conocimiento orienten la estrategia hacia la excelencia."
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

#Financiera
with col1:
    st.subheader("1.Financiera (Sostenibilidad)")
    
    fig_fin = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = margen_real,
        title = {'text': "KR: Margen Rentabilidad (%)"},
        delta = {'reference': target_margen},
        gauge = {
            'axis': {'range': [None, 50]},
            'bar': {'color': "#4169E1"}, # Color corregido (RoyalBlue Hex)
            'steps' : [{'range': [0, 15], 'color': "#444"}, {'range': [15, 25], 'color': "#666"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target_margen}}))
    fig_fin.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="#262730", font={'color': "white"})
    st.plotly_chart(fig_fin, use_container_width=True)
    
    st.metric("Presupuesto Ejercido", f"${total_cost:,.0f}", delta_color="inverse")

#Clientes
with col2:
    st.subheader("2.Clientes (Confianza)")
    
    fig_cli = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = total_clientes_activos,
        title = {'text': "KR: Clientes Activos (Anual)"},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [None, 40]},
            'threshold': {'line': {'color': "#00CC96", 'width': 2}, 'thickness': 0.75, 'value': target_clientes},
            'bar': {'color': "#4169E1"}
        }
    ))
    fig_cli.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="#262730", font={'color': "white"})
    st.plotly_chart(fig_cli, use_container_width=True)
    
    st.info(f"En {selected_year} atendimos a {total_clientes_activos} clientes únicos.")

st.markdown("---")
col3, col4 = st.columns(2)

#Procesos
with col3:
    st.subheader("3.Procesos (Eficiencia)")
    
    labels = ['Eficientes', 'Excedidos']
    values = [proyectos_eficientes, total_proyectos - proyectos_eficientes]
    
    fig_proc = px.pie(values=values, names=labels, hole=0.6, 
                      title=f"Eficiencia: {porcentaje_eficiencia:.1f}%",
                      color_discrete_sequence=['#00CC96', '#EF553B'])
    fig_proc.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="#262730", font={'color': "white"})
    st.plotly_chart(fig_proc, use_container_width=True)

#Aprendizaje
with col4:
    st.subheader("4.Aprendizaje (Talento Activo)")
    
    if total_empleados > 0:
        df_agrupado = df_talento_filtered['experience'].value_counts().reset_index()
        df_agrupado.columns = ['Nivel', 'Cantidad']
        
        fig_apr = px.bar(df_agrupado, x='Cantidad', y='Nivel', orientation='h',
                         title="Seniority del Equipo Activo",
                         color='Nivel', text='Cantidad')
        fig_apr.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), showlegend=False, paper_bgcolor="#262730", font={'color': "white"})
        st.plotly_chart(fig_apr, use_container_width=True)
    else:
        st.warning("No se encontraron empleados activos en proyectos este año.")
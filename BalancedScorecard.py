import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

st.set_page_config(page_title="Balanced Scorecard", layout="wide")

#Estilo CSS para que parezca un Balanced Scorecard
st.markdown("""
<style>
    .vision-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

db_connection_str = 'mysql+pymysql://root:@localhost/projectsupportdb'
db_connection = create_engine(db_connection_str)

@st.cache_data
def get_strategic_data():
    try:
        df_fact = pd.read_sql("SELECT * FROM fact_project", db_connection)
        df_emp = pd.read_sql("SELECT * FROM dim_employee", db_connection)
        df_exp = pd.read_sql("SELECT * FROM dim_experience", db_connection)
        df_talento = df_emp.merge(df_exp, on="idExperience")
        
        return df_fact, df_talento
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_fact, df_talento = get_strategic_data()

if df_fact.empty:
    st.stop()

#Calculo de OKRs (Resultados Clave)

#Financiera (Margen de Rentabilidad)
#Visión: "Innovación Sostenible"
total_budget = df_fact['budget'].sum()
total_cost = df_fact['cost'].sum()
margen_real = ((total_budget - total_cost) / total_budget) * 100
target_margen = 25.0 # Meta del 25%

#Clientes (Penetración de Mercado)
#Visión: "Referente en creación de plataformas"
total_clientes_activos = df_fact['idClient'].nunique()
target_clientes = 30 # Meta de tener 30 clientes activos

#Procesos (Eficiencia Operativa)
#Visión: "Excelencia y automatización" -> Medido como desviación del presupuesto
#Si cost < budget = Eficiente. Calculamos qué % de proyectos fueron eficientes.
proyectos_eficientes = df_fact[df_fact['cost'] <= df_fact['budget']].shape[0]
total_proyectos = df_fact.shape[0]
porcentaje_eficiencia = (proyectos_eficientes / total_proyectos) * 100
target_eficiencia = 85.0 # Meta del 85%

#Aprendizaje (Gestión del Conocimiento)
#Visión: "Desarrollo de software inteligente" -> Necesitamos Seniors
#Contamos cuántos son Senior o Semi-Senior vs Juniors
if 'experience' in df_talento.columns:
    expertos = df_talento[df_talento['experience'].isin(['Senior', 'Semi-Senior', 'Experto'])].shape[0]
    total_empleados = df_talento.shape[0]
    ratio_talento = (expertos / total_empleados) * 100
else:
    ratio_talento = 50 # Valor default si no encuentra la columna


st.title("Balanced Scorecard: Visión Estratégica")

#Mostrar la Visión claramente
st.markdown("""
<div class="vision-box">
    <h3>Visión</h3>
    "Ser una empresa líder en el desarrollo de software inteligente... aspiramos a consolidarnos como un referente 
    donde la analítica de desempeño y la gestión del conocimiento orienten la estrategia hacia la excelencia."
</div>
""", unsafe_allow_html=True)

#Layout de 4 cuadrantes
col1, col2 = st.columns(2)

#Grafico 1: Financiera
with col1:
    st.subheader("1. Perspectiva Financiera")
    st.markdown("**Objetivo:** Sostenibilidad para la innovación.")
    
    fig_fin = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = margen_real,
        title = {'text': "KR: Margen de Rentabilidad (%)"},
        delta = {'reference': target_margen},
        gauge = {
            'axis': {'range': [None, 50]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [0, 15], 'color': "lightgray"},
                {'range': [15, 25], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target_margen}}))
    fig_fin.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_fin, use_container_width=True)
    st.caption(f"Presupuesto: ${total_budget:,.0f} | Costo Real: ${total_cost:,.0f}")

#Grafico 2: Clientes
with col2:
    st.subheader("2. Perspectiva del Cliente")
    st.markdown("**Objetivo:** Ser referente en soluciones confiables.")
    
    #Gráfico de progreso hacia la meta de clientes
    fig_cli = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = total_clientes_activos,
        title = {'text': "KR: Clientes Activos"},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [None, target_clientes]},
            'threshold': {
                'line': {'color': "green", 'width': 2},
                'thickness': 0.75,
                'value': target_clientes},
            'bar': {'color': "royalblue"}
        }
    ))
    fig_cli.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_cli, use_container_width=True)
    st.caption("La diversificación de clientes valida nuestra posición de liderazgo.")

st.markdown("---")

col3, col4 = st.columns(2)

#Grafico 3: Procesos Internos
with col3:
    st.subheader("3. Perspectiva Procesos")
    st.markdown("**Objetivo:** Excelencia y automatización operativa.")
    
    #Donut chart de eficiencia
    labels = ['Eficientes', 'Excedidos']
    values = [proyectos_eficientes, total_proyectos - proyectos_eficientes]
    
    fig_proc = px.pie(values=values, names=labels, hole=0.6, 
                      title=f"KR: Eficiencia en Proyectos ({porcentaje_eficiencia:.1f}%)",
                      color_discrete_sequence=['#00CC96', '#EF553B'])
    fig_proc.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_proc, use_container_width=True)
    st.caption("Porcentaje de proyectos entregados dentro o bajo presupuesto.")

#Grafico 4: Aprendizaje y crecimiento
with col4:
    st.subheader("4. Aprendizaje (Talento)")
    st.markdown("**Objetivo:** Gestión del conocimiento experto.")
    
    #Barra de composición de talento
    df_agrupado = df_talento['experience'].value_counts().reset_index()
    df_agrupado.columns = ['Nivel', 'Cantidad']
    
    fig_apr = px.bar(df_agrupado, x='Cantidad', y='Nivel', orientation='h',
                     title="KR: Distribución de Seniority",
                     color='Nivel', text='Cantidad')
    fig_apr.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
    st.plotly_chart(fig_apr, use_container_width=True)
    st.caption("Base de talento para soportar desarrollo de software inteligente.")
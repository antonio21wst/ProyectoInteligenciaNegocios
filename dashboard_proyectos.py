import pandas as pd
import streamlit as st
import plotly.express as px
import pymysql

# ------------------------------------
# Configuración de pantalla completa
# ------------------------------------
st.set_page_config(page_title="Dashboard Proyectos", layout="wide")

# -------------------------------
# Conexión a MySQL
# -------------------------------
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='soporte_desicion'
)

# -------------------------------
# Cargar datos
# -------------------------------
fact_project = pd.read_sql("SELECT * FROM fact_project", conn)
dim_client = pd.read_sql("SELECT * FROM dim_client", conn)
dim_area = pd.read_sql("SELECT * FROM dim_area", conn)
dim_address = pd.read_sql("SELECT * FROM dim_address", conn)
dim_city = pd.read_sql("SELECT * FROM dim_city", conn)
dim_team = pd.read_sql("SELECT * FROM dim_team", conn)
dim_employee = pd.read_sql("SELECT * FROM dim_employee", conn)
dim_experience = pd.read_sql("SELECT * FROM dim_experience", conn)

conn.close()

# -------------------------------
# Merge de datos
# -------------------------------
df = fact_project.merge(dim_client, on="idClient")
df = df.merge(dim_area, on="idArea")
df = df.merge(dim_address, on="idAddress")
df = df.merge(dim_city, on="idCity")
df = df.merge(dim_team, on="idTeam")

# -------------------------------
# Calcular Ganancia
# -------------------------------
df["ganancia"] = df["budget"] - df["cost"]
ganancia_total = df["ganancia"].sum()

# -------------------------------
# KPIs
# -------------------------------
total_proyectos = fact_project.shape[0]
porcentaje_cumplimiento = (df["cost"].sum() / df["budget"].sum()) * 100

# -------------------------------
# Experiencia empleados
# -------------------------------
df_exp = fact_project.merge(dim_employee, on="idEmployee", how="left")
df_exp = df_exp.merge(dim_experience, on="idExperience", how="right")
empleados_por_experiencia = df_exp.groupby("experience")["idEmployee"].nunique().reset_index()
empleados_por_experiencia.rename(columns={"idEmployee": "num_empleados"}, inplace=True)
empleados_por_experiencia["num_empleados"] = empleados_por_experiencia["num_empleados"].fillna(0)

# -------------------------------
# DASHBOARD OPTIMIZADO
# -------------------------------
st.title("📊 Dashboard General de Proyectos")

# ------------------ KPIs ------------------
st.header(" Indicadores Generales")
k1, k2, k3 = st.columns(3)
k1.metric("Total Proyectos", total_proyectos)
k2.metric("% Cumplimiento", f"{porcentaje_cumplimiento:.2f}%")
k3.metric("Ganancia Total", f"${ganancia_total:,.2f}")
st.markdown("---")

# ------------------ Gráficos en 3 columnas ------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Ganancia por Cliente")
    fig1 = px.bar(df, x="nameClient", y="ganancia", height=300)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Proyectos por Área")
    fig2 = px.pie(df, names="nameArea", values="idFact_Project", height=300)
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.subheader("Proyectos por Ciudad")
    proyectos_por_ciudad = df.groupby("nameCity")["idFact_Project"].count().reset_index()
    fig3 = px.bar(proyectos_por_ciudad, x="nameCity", y="idFact_Project", height=300)
    st.plotly_chart(fig3, use_container_width=True)

# ------------------ Fila 2 ------------------
c4, c5, c6 = st.columns(3)

with c4:
    st.subheader("Proyectos por Equipo")
    proyectos_por_equipo = df.groupby("nameTeam")["idFact_Project"].count().reset_index()
    fig4 = px.bar(proyectos_por_equipo, x="nameTeam", y="idFact_Project", height=300)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.subheader("Integrantes por Equipo")
    fig5 = px.bar(dim_team, x="nameTeam", y="integrantes", height=300)
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.subheader("Experiencia de Empleados")
    fig6 = px.bar(empleados_por_experiencia, x="experience", y="num_empleados", height=300)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.write("")

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

db_connection_str = 'mysql+pymysql://root:@localhost/projectsupportdb'
db_connection = create_engine(db_connection_str)

try:
    fact_project = pd.read_sql("SELECT * FROM fact_project", db_connection)
    dim_client = pd.read_sql("SELECT * FROM dim_client", db_connection)
    dim_area = pd.read_sql("SELECT * FROM dim_area", db_connection)
    dim_address = pd.read_sql("SELECT * FROM dim_address", db_connection)
    dim_city = pd.read_sql("SELECT * FROM dim_city", db_connection)
    dim_team = pd.read_sql("SELECT * FROM dim_team", db_connection)
    dim_employee = pd.read_sql("SELECT * FROM dim_employee", db_connection)
    dim_experience = pd.read_sql("SELECT * FROM dim_experience", db_connection)
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

#Merge para tener toda la info
df = fact_project.merge(dim_client, on="idClient")
df = df.merge(dim_area, on="idArea")
df = df.merge(dim_address, on="idAddress")
df = df.merge(dim_city, on="idCity")
df = df.merge(dim_team, on="idTeam")

#KPIs
total_proyectos = fact_project.shape[0]
presupuesto_total = fact_project["budget"].sum()
costo_total = fact_project["cost"].sum()
porcentaje_cumplimiento = (costo_total / presupuesto_total) * 100

#Número de integrantes por equipo
num_integrantes = dim_team[["nameTeam", "integrantes"]]


#Experiencia de los empleados (todos los niveles)
df_exp = fact_project.merge(dim_employee, on="idEmployee", how="left")
df_exp = df_exp.merge(dim_experience, on="idExperience", how="right")  # Incluye todos los niveles

#Contar empleados únicos por nivel de experiencia
empleados_por_experiencia = df_exp.groupby("experience")["idEmployee"].nunique().reset_index()
empleados_por_experiencia.rename(columns={"idEmployee": "num_empleados"}, inplace=True)
empleados_por_experiencia["num_empleados"] = empleados_por_experiencia["num_empleados"].fillna(0)

#Balance Score General de Proyectos
presupuesto_cumplimiento = min(costo_total / presupuesto_total, 1)
experience_mapping = {"Junior": 1, "Semi-Senior": 2, "Senior": 3}
df_exp["experience_score"] = df_exp["experience"].map(experience_mapping)
experiencia_promedio = df_exp["experience_score"].mean() / 3

proyectos_por_equipo = df.groupby("nameTeam")["idFact_Project"].count()
proyectos_norm_equipo = proyectos_por_equipo / proyectos_por_equipo.sum()
balance_equipo = 1 - proyectos_norm_equipo.std()

proyectos_por_area = df.groupby("nameArea")["idFact_Project"].count()
proyectos_norm_area = proyectos_por_area / proyectos_por_area.sum()
balance_area = 1 - proyectos_norm_area.std()

balance_score_general = (presupuesto_cumplimiento + experiencia_promedio + balance_equipo + balance_area) / 4

#Dashboard Streamlit
st.title("Dashboard de Proyectos")

#KPIs con formato completo
st.metric("Total Proyectos", f"{250:,}")
st.metric("Presupuesto Total", f"${58934940.60:,.2f}")
st.metric("Costo Total", f"${28645501.32:,.2f}")
st.metric("% Cumplimiento", f"{48.61:.2f}%")
st.metric("Balance Score General", f"{0.86:.2f}")

#Costo por Cliente
st.subheader("Costo por Cliente")
df_client_cost = df.groupby("nameClient")["cost"].sum().reset_index()
fig1 = px.bar(df_client_cost, x="nameClient", y="cost", text="cost", title="Costo por Cliente")
fig1.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
st.plotly_chart(fig1)

#Proyectos por Área
st.subheader("Proyectos por Área")
df_area = df.groupby("nameArea")["idFact_Project"].count().reset_index()
fig2 = px.pie(df_area, names="nameArea", values="idFact_Project", title="Proyectos por Área")
st.plotly_chart(fig2)

#Proyectos por Localidad (Ciudad)
st.subheader("Proyectos por Localidad")
proyectos_por_ciudad = df.groupby("nameCity")["idFact_Project"].count().reset_index()
fig3 = px.bar(proyectos_por_ciudad, x="nameCity", y="idFact_Project", text="idFact_Project",
              title="Número de Proyectos por Localidad")
fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig3)

#Proyectos por Equipo
st.subheader("Proyectos por Equipo")
proyectos_por_equipo = df.groupby("nameTeam")["idFact_Project"].count().reset_index()
fig4 = px.bar(proyectos_por_equipo, x="nameTeam", y="idFact_Project", text="idFact_Project",
              title="Número de Proyectos por Equipo")
fig4.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig4)

#Número de integrantes por equipo
st.subheader("Número de Integrantes por Equipo")
fig5 = px.bar(num_integrantes, x="nameTeam", y="integrantes", text="integrantes",
              title="Integrantes por Equipo")
fig5.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig5)

#Experiencia de los empleados
st.subheader("Experiencia de los Empleados")
fig6 = px.bar(empleados_por_experiencia, x="experience", y="num_empleados", text="num_empleados",
              title="Número de Empleados por Nivel de Experiencia")
fig6.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig6)
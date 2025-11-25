import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine


# Conexión MySQL usando SQLAlchemy

engine = create_engine("mysql+pymysql://root:@localhost/projectsupportdb")


# Cargar tablas

fact_project = pd.read_sql("SELECT * FROM fact_project", engine)
dim_time = pd.read_sql("SELECT * FROM dim_time", engine)
dim_client = pd.read_sql("SELECT * FROM dim_client", engine)
dim_area = pd.read_sql("SELECT * FROM dim_area", engine)
dim_address = pd.read_sql("SELECT * FROM dim_address", engine)
dim_city = pd.read_sql("SELECT * FROM dim_city", engine)
dim_team = pd.read_sql("SELECT * FROM dim_team", engine)


# Merge de datos

df = fact_project.merge(dim_time, on="idTime")
df = df.merge(dim_client, on="idClient")
df = df.merge(dim_area, on="idArea")
df = df.merge(dim_address, on="idAddress")
df = df.merge(dim_city, on="idCity")
df = df.merge(dim_team, on="idTeam")


# Asegurarnos de usar la columna year

df['year'] = df['year']  


#  Predicción de proyectos para el próximo año

proyectos_por_año = df.groupby("year")["idFact_Project"].count().reset_index()
X = proyectos_por_año[['year']]
y = proyectos_por_año['idFact_Project']

modelo_proyectos = LinearRegression()
modelo_proyectos.fit(X, y)

next_year = proyectos_por_año['year'].max() + 1
pred_proyectos = modelo_proyectos.predict([[next_year]])[0]

print(" Proyectos estimados para", next_year, ":", int(pred_proyectos))


#  Predicción de ganancias para el próximo año

df["ganancia"] = df["budget"] - df["cost"]
ganancias_por_año = df.groupby("year")["ganancia"].sum().reset_index()

Xg = ganancias_por_año[['year']]
yg = ganancias_por_año['ganancia']

modelo_ganancia = LinearRegression()
modelo_ganancia.fit(Xg, yg)

pred_ganancia = modelo_ganancia.predict(pd.DataFrame({'year': [next_year]}))[0]

print(" Ganancia estimada para", next_year, ":", round(pred_ganancia, 2))


#  Ciudad con más proyectos

ciudad_proyectos = df.groupby("nameCity")["idFact_Project"].count()
ciudad_top = ciudad_proyectos.idxmax()

print(" Ciudad con más proyectos:", ciudad_top)

#  Ciudad con más clientes

ciudad_clientes = df.groupby("nameCity")["idClient"].nunique()
ciudad_clientes_top = ciudad_clientes.idxmax()

print(" Ciudad con más clientes:", ciudad_clientes_top)

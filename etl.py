import mysql.connector
from mysql.connector import errorcode, cursor
from datetime import datetime, timedelta
from decimal import Decimal

SOURCE_DB_CONFIG = {
    'user': 'projectmanagement',
    'password': '1234', 
    'host': '172.26.160.30',
    'port': '3307',
    'database': 'projectmanagementdb'
}

DEST_DB_CONFIG = {
    'user': 'projectmanagement',
    'password': '1234', 
    'host': '172.26.160.30',
    'port': '3307',
    'database': 'projectsupportdb'
}

BATCH_SIZE = 5000  

def connect_db(config, attempts=3, delay=5):
    for attempt in range(1, attempts + 1):
        try:
            print(f"Conectando a {config['database']} en {config['host']}... (Intento {attempt})")
            cnx = mysql.connector.connect(**config)
            print(f"Conexión exitosa a {config['database']}.")
            return cnx
        except mysql.connector.Error as err:
            print(f"Error al conectar: {err}")
            if attempt < attempts:
                print(f"Reintentando en {delay} segundos...")
                time.sleep(delay)
            else:
                print("No se pudo conectar a la base de datos después de varios intentos.")
                raise
    return None

def clear_dw_tables(dest_cursor):
    print("Limpiando Data Warehouse (projectsupportdb)...")
    tables = [
        'fact_project',
        'dim_client',
        'dim_address',
        'dim_city',
        'dim_state',
        'dim_country',
        'dim_team',
        'dim_employee',
        'dim_rol',
        'dim_experience',
        'dim_area',
        'dim_time'
    ]
    try:
        dest_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table in tables:
            print(f"  Limpiando {table}...")
            dest_cursor.execute(f"TRUNCATE TABLE {table}")
            dest_cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
        dest_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Data Warehouse limpiado.")
    except mysql.connector.Error as err:
        print(f"Error al limpiar tablas: {err}")
        raise

def etl_load_simple_dims(source_cursor, dest_cursor):
    print("Iniciando carga de dimensiones Copo de Nieve...")
    try:
        print("  Cargando dim_country...")
        source_cursor.execute("SELECT idCountry, nameCountry FROM country")
        data_tuples = [(row['idCountry'], row['nameCountry']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_country (idCountry, nameCountry) VALUES (%s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando dim_state...")
        source_cursor.execute("SELECT idState, nameState, idCountry FROM state")
        data_tuples = [(row['idState'], row['nameState'], row['idCountry']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_state (idState, nameState, idCountry) VALUES (%s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando dim_city...")
        source_cursor.execute("SELECT idCity, nameCity, idState FROM city")
        data_tuples = [(row['idCity'], row['nameCity'], row['idState']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_city (idCity, nameCity, idState) VALUES (%s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando dim_address...")
        source_cursor.execute("SELECT idAddress, street, postalCode, idCity FROM address")
        data_tuples = [(row['idAddress'], row['street'], row['postalCode'], row['idCity']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_address (idAddress, street, postalCode, idCity) VALUES (%s, %s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando dim_rol...")
        source_cursor.execute("SELECT idRol, nameRol FROM rol")
        data_tuples = [(row['idRol'], row['nameRol']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_rol (idRol, rol) VALUES (%s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando y transformando dim_experience...")
        source_cursor.execute("""
            SELECT idExperience, 
                   CASE experience 
                       WHEN 'SemiSenior' THEN 'Mid' 
                       ELSE experience 
                   END as experience
            FROM experience
            WHERE experience IN ('Junior', 'SemiSenior', 'Senior')
        """)
        data_tuples = [(row['idExperience'], row['experience']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_experience (idExperience, experience) VALUES (%s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas transformadas insertadas.")

        print("  Cargando dim_area...")
        source_cursor.execute("SELECT idArea, nameArea FROM area")
        data_tuples = [(row['idArea'], row['nameArea']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_area (idArea, nameArea) VALUES (%s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")
        
        print("Dimensiones simples cargadas.")
        
    except mysql.connector.Error as err:
        print(f"Error en etl_load_simple_dims: {err}")
        raise

def etl_load_dependent_dims(source_cursor, dest_cursor):
    try:
        print("  Cargando dim_employee...")
        source_cursor.execute("SELECT idEmployee, nameEmployee, idRol, idExperience FROM employee")
        data_tuples = [(row['idEmployee'], row['nameEmployee'], row['idRol'], row['idExperience']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_employee (idEmployee, nameEmployee, idRol, idExperience) VALUES (%s, %s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("  Cargando dim_client...")
        source_cursor.execute("SELECT idClient, nameClient, idAddress FROM client")
        data_tuples = [(row['idClient'], row['nameClient'], row['idAddress']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_client (idClient, nameClient, idAddress) VALUES (%s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas insertadas.")

        print("Dimensiones dependientes cargadas.")

    except mysql.connector.Error as err:
        print(f"Error en etl_load_dependent_dims: {err}")
        raise

def etl_load_transformed_dims(source_cursor, dest_cursor):
    print("Iniciando carga de dimensiones transformadas...")
    time_lookup = {}

    try:
        print("  Cargando y transformando dim_team...")
        source_cursor.execute("""
            SELECT 
                t.idTeam, 
                t.nameTeam, 
                COUNT(tm.idEmployee) as integrantes,
                MIN(tm.idEmployee) as leadEmployee
            FROM team t
            LEFT JOIN team_member tm ON t.idTeam = tm.idTeam
            GROUP BY t.idTeam, t.nameTeam
        """)
        data_tuples = [(row['idTeam'], row['nameTeam'], row['integrantes'], row['leadEmployee']) for row in source_cursor.fetchall()]
        dest_cursor.executemany(
            "INSERT INTO dim_team (idTeam, nameTeam, integrantes, idEmployee) VALUES (%s, %s, %s, %s)", data_tuples
        )
        print(f"    -> {dest_cursor.rowcount} filas transformadas insertadas.")

        print("  Generando dim_time...")
        
        source_cursor.execute("""
            SELECT MIN(min_date) as min_date, MAX(max_date) as max_date
            FROM (
                SELECT MIN(plannedStart) as min_date, MAX(plannedEnd) as max_date FROM project
                UNION ALL
                SELECT MIN(workDate), MAX(workDate) FROM timesheet
            ) as dates
        """)
        result = source_cursor.fetchone()
        min_date, max_date = result['min_date'], result['max_date']
        
        if not min_date or not max_date:
            print("No hay fechas en la base de datos de origen. Abortando dim_time.")
            return {}

        print(f"    -> Generando fechas desde {min_date} hasta {max_date}")
        
        time_data = []
        current_date = min_date
        while current_date <= max_date:
            quarter = (current_date.month - 1) // 3 + 1
            time_data.append((
                current_date,
                current_date.year,
                current_date.month,
                current_date.day,
                quarter
            ))
            current_date += timedelta(days=1)
        
        print(f"    -> {len(time_data)} días generados.")

        sql = "INSERT INTO dim_time (`date`, `year`, `month`, `day`, `quarter`) VALUES (%s, %s, %s, %s, %s)"
        for i in range(0, len(time_data), BATCH_SIZE):
            batch = time_data[i:i + BATCH_SIZE]
            dest_cursor.executemany(sql, batch)
            print(f"      -> Lote de {len(batch)} fechas insertado.")

        dest_cursor.execute("SELECT idTime, `date` FROM dim_time")
        # El cursor de destino (dest_cursor) no es de diccionario, así que usamos índices
        time_lookup = {row[1].isoformat(): row[0] for row in dest_cursor.fetchall()}
        print(f"    -> Lookup de dim_time creado con {len(time_lookup)} entradas.")

        print("Dimensiones transformadas cargadas.")
        return time_lookup

    except mysql.connector.Error as err:
        print(f"Error en etl_load_transformed_dims: {err}")
        raise

def etl_load_fact_project(source_cursor, dest_cursor, time_lookup):
    print("Iniciando carga de fact_project...")

    try:
        print("  1. Extrayendo datos de origen (Proyectos)...")
        source_cursor.execute("""
            SELECT 
                p.idClient,
                p.idArea,
                p.idTeam,
                COALESCE(p.actualStart, p.plannedStart) as startDate,
                COALESCE(p.actualEnd, p.plannedEnd) as endDate,
                p.budget,
                p.cost
            FROM project p
            WHERE COALESCE(p.actualStart, p.plannedStart) IS NOT NULL 
        """)
        project_data = source_cursor.fetchall()
        print(f"    -> {len(project_data)} registros de hechos extraídos.")

        # T: Crear lookup para Project Managers
        print("  2. Transformando: Creando lookup de Project Managers...")
        source_cursor.execute("""
            SELECT 
                tm.idTeam,
                tm.idEmployee 
            FROM team_member tm
            JOIN employee e ON tm.idEmployee = e.idEmployee
            JOIN rol r ON e.idRol = r.idRol
            WHERE r.nameRol = 'Project Manager'
        """)
        
        pm_lookup = {row['idTeam']: row['idEmployee'] for row in source_cursor.fetchall()}
        print(f"    -> Lookup de PMs creado para {len(pm_lookup)} equipos.")

        print("  3. Transformando: Buscando claves foráneas (Surrogate Keys)...")
        fact_data = []
        for row in project_data:
            idClient = row['idClient']
            idArea = row['idArea']
            idTeam = row['idTeam']
            startDate = row['startDate']
            endDate = row['endDate']
            budget = row['budget']
            cost = row['cost']
            
            idEmployee_pm = pm_lookup.get(idTeam, None) 
            
            start_key = time_lookup.get(startDate.isoformat()) if startDate else None
            end_key = time_lookup.get(endDate.isoformat()) if endDate else None
            
            if start_key: 
                fact_data.append((
                    idClient, idArea, idTeam, idEmployee_pm,
                    start_key, end_key, start_key, 
                    budget, cost
                ))
        
        print(f"    -> {len(fact_data)} hechos listos para cargar.")

        print("  4. Cargando hechos en lotes...")
        sql = """
            INSERT INTO fact_project (
                idClient, idArea, idTeam, idEmployee, 
                idFechaInicio, idFechaFin, idTime, 
                budget, cost
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        total_inserted = 0
        for i in range(0, len(fact_data), BATCH_SIZE):
            batch = fact_data[i:i + BATCH_SIZE]
            dest_cursor.executemany(sql, batch)
            total_inserted += len(batch)
            print(f"    -> Lote de {len(batch)} hechos insertado (total: {total_inserted}).")
        
        print("Carga de fact_project completada.")

    except mysql.connector.Error as err:
        print(f"Error en etl_load_fact_project: {err}")
        raise

def main():
    source_cnx = None
    dest_cnx = None
    
    try:
        source_cnx = connect_db(SOURCE_DB_CONFIG)
        dest_cnx = connect_db(DEST_DB_CONFIG)
        
        if not source_cnx or not dest_cnx:
            raise Exception("No se pudieron establecer las conexiones de base de datos.")

        source_cursor = source_cnx.cursor(dictionary=True)
        dest_cursor = dest_cnx.cursor()
        
        dest_cnx.start_transaction()

        clear_dw_tables(dest_cursor)
        
        etl_load_simple_dims(source_cursor, dest_cursor)
        etl_load_dependent_dims(source_cursor, dest_cursor)
        
        time_lookup = etl_load_transformed_dims(source_cursor, dest_cursor)
        
        etl_load_fact_project(source_cursor, dest_cursor, time_lookup)

        print("Proceso ETL completado exitosamente. Haciendo commit de los cambios...")
        dest_cnx.commit()

    except mysql.connector.Error as err:
        print(f"\n¡ERROR! Proceso ETL fallido: {err}")
        print("Revirtiendo cambios (Rollback)...")
        if dest_cnx:
            dest_cnx.rollback()
    except Exception as e:
        print(f"\n¡ERROR INESPERADO! {e}")
        if dest_cnx:
            dest_cnx.rollback()
    
    finally:
        if 'source_cursor' in locals() and source_cursor:
            source_cursor.close()
        if 'dest_cursor' in locals() and dest_cursor:
            dest_cursor.close()
        if source_cnx and source_cnx.is_connected():
            source_cnx.close()
            print("Conexión a OLTP (fuente) cerrada.")
        if dest_cnx and dest_cnx.is_connected():
            dest_cnx.close()
            print("Conexión a OLAP (destino) cerrada.")

if __name__ == "__main__":
    import time
    main()
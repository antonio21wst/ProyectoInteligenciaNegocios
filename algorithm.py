import mysql.connector
from mysql.connector import errorcode
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal

DB_CONFIG = {
    'user': 'projectmanagement',
    'password': '1234',  
    'host': '172.31.14.104',
    'port': '3307',      
    'database': 'projectmanagementdbp'
}

NUM_EMPLOYEES = 50
NUM_TEAMS = 10
NUM_CLIENTS = 25
NUM_PROJECTS = 250
MAX_TASKS_PER_PROJECT = 80
MAX_EXPENSES_PER_PROJECT = 10
MAX_TIMESHEETS_PER_TASK = 20
COST_PER_HOUR = 75.0 

# Inicializar Faker para generar nombres.
fake = Faker(['es_ES', 'es_MX', 'en_US'])

# --- DICCIONARIOS PARA DATOS REALISTAS---
locations = {
    'México': {
        'Ciudad de México': ['Ciudad de México'],
        'Jalisco': ['Guadalajara', 'Zapopan', 'Tlaquepaque'],
        'Nuevo León': ['Monterrey', 'San Pedro Garza García']
    },
    'Estados Unidos': {
        'California': ['San Francisco', 'Los Angeles', 'San Jose'],
        'New York': ['New York City', 'Buffalo'],
        'Texas': ['Austin', 'Houston', 'Dallas']
    },
    'España': {
        'Comunidad de Madrid': ['Madrid'],
        'Cataluña': ['Barcelona', 'L\'Hospitalet de Llobregat'],
        'Andalucía': ['Sevilla', 'Málaga']
    }
}

AREAS_NEGOCIO = [
    'Desarrollo de Software', 'Aseguramiento de Calidad (QA)', 
    'Diseño de Experiencia e Interfaz (UX/UI)', 'Operaciones y Automatización (DevOps)', 
    'Gestión de Proyectos', 'Análisis de Negocio', 'Soporte Técnico', 
    'Infraestructura y Redes', 'Seguridad Informática', 
    'Investigación y Desarrollo (I+D)', 'Marketing y Ventas'
]

# Plantillas para generar nombres de proyecto realistas
project_name_templates = {
    'Desarrollo de Software': [
        'Plataforma de {Noun} para {Client}', 'Migración de {System} a Microservicios', 
        'Desarrollo de API REST para {Module}', 'Módulo de {Noun} (v2.0)'],
    'Aseguramiento de Calidad (QA)': [
        'Plan de Pruebas Automatizadas para {Project}', 'Auditoría de Calidad de {System}', 
        'Testing de Performance (E-commerce)'],
    'Diseño de Experiencia e Interfaz (UX/UI)': [
        'Rediseño de {App} Móvil', 'Investigación de Usuario para {Module}', 
        'Diseño de Sistema de {Noun}'],
    'Operaciones y Automatización (DevOps)': [
        'Implementación de Pipeline CI/CD ({Project})', 'Migración a Kubernetes', 
        'Optimización de Infraestructura AWS/Azure'],
    'Gestión de Proyectos': ['Implementación de Metodología Ágil', 'Oficina de Proyectos (PMO)'],
    'Análisis de Negocio': ['Análisis de Requerimientos para {Project}', 'Definición de {System} v3'],
    'Soporte Técnico': ['Plataforma de Onboarding de Soporte', 'Sistema de Gestión de Tickets'],
    'Infraestructura y Redes': ['Actualización de Red Corporativa', 'Migración de Servidores On-Premise a Cloud'],
    'Seguridad Informática': ['Auditoría de Seguridad (Pentesting)', 'Implementación de {Standard} Compliance'],
    'Investigación y Desarrollo (I+D)': ['Prototipo de {Feature} con IA', 'Investigación de {Technology}'],
    'Marketing y Ventas': ['Desarrollo de CRM Interno', 'Plataforma de Análisis de Campañas']
}
# Nombres genéricos para rellenar plantillas
project_fillers = {
    'Noun': ['Pagos', 'Inventario', 'Usuarios', 'Reportes', 'Logística', 'Analítica', 'Seguridad'],
    'System': ['Legacy', 'ERP', 'CRM', 'Monolito', 'Facturación'],
    'Module': ['Autenticación', 'Perfiles', 'Marketplace', 'Checkout'],
    'App': ['Banca', 'Retail', 'Salud', 'Lealtad'],
    'Project': ['Plataforma X', 'Proyecto Alfa', 'Sistema B2B'],
    'Standard': ['ISO 27001', 'PCI', 'GDPR'],
    'Feature': ['Recomendación', 'Búsqueda'],
    'Technology': ['Blockchain', 'Quantum Computing']
}

expense_templates = {
    'Software': ('Licencia de {Software}', (500, 3000)),
    'Cloud': ('Costos de {Cloud_Provider} (Servidores)', (1000, 8000)),
    'Hardware': ('Compra de {Hardware} para equipo', (800, 5000)),
    'Consultoría': ('Servicios de Consultoría Externa ({Topic})', (2000, 10000)),
    'Operativos': ('Viáticos (Viaje a Cliente)', (300, 1500)),
    'Capacitación': ('Curso de {Technology} para equipo', (500, 2500))
}
expense_fillers = {
    'Software': ['Jira', 'Figma', 'Sketch', 'IntelliJ IDEA', 'Salesforce'],
    'Cloud_Provider': ['AWS', 'Azure', 'Google Cloud', 'DigitalOcean'],
    'Hardware': ['Laptops (Desarrollo)', 'Servidor de Pruebas', 'Equipo de Red'],
    'Topic': ['Seguridad', 'UX', 'Arquitectura', 'Legal'],
    'Technology': ['Kubernetes', 'React Avanzado', 'Gestión Ágil']
}


def clear_tables(cursor):
    """ Vacía todas las tablas en el orden inverso de dependencias. """
    print("Limpiando tablas existentes...")
    tables = [
        'timesheet', 'expense', 'task', 'team_member', 
        'project', 'client', 'address', 'city', 'state', 
        'country', 'employee', 'team', 'area', 'rol', 'experience'
    ]
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
            # Resetear auto_increment
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Tablas limpiadas.")
    except mysql.connector.Error as err:
        print(f"Error al limpiar tablas: {err}")
        raise

def populate_locations(cursor):
    """ Puebla las tablas country, state, city y address. Devuelve IDs de ciudades. """
    print("Poblando Ubicaciones (País, Estado, Ciudad)...")
    city_ids = []
    address_ids = []
    
    try:
        for country_name, states in locations.items():
            cursor.execute("INSERT INTO country (nameCountry) VALUES (%s)", (country_name,))
            country_id = cursor.lastrowid
            
            for state_name, cities in states.items():
                cursor.execute("INSERT INTO state (nameState, idCountry) VALUES (%s, %s)", (state_name, country_id))
                state_id = cursor.lastrowid
                
                for city_name in cities:
                    cursor.execute("INSERT INTO city (nameCity, idState) VALUES (%s, %s)", (city_name, state_id))
                    city_ids.append(cursor.lastrowid)

        print(f"Insertados {len(city_ids)} ciudades.")
        address_data = []
        for _ in range(NUM_CLIENTS * 2): 
            address_data.append((
                fake.street_address(),
                fake.postcode(),
                random.choice(city_ids)
            ))
        
        sql = "INSERT INTO address (street, postalCode, idCity) VALUES (%s, %s, %s)"
        cursor.executemany(sql, address_data)
        
        # Obtener todos los IDs de direcciones generados
        cursor.execute("SELECT idAddress FROM address")
        address_ids = [item[0] for item in cursor.fetchall()]
        print(f"Insertadas {len(address_ids)} direcciones.")
        
        return city_ids, address_ids

    except mysql.connector.Error as err:
        print(f"Error en populate_locations: {err}")
        raise

def populate_hr_catalogs(cursor):
    """ Puebla Rol y Experience. Devuelve mapeos de ID. """
    print("Poblando Catálogos de RRHH (Rol, Experiencia)...")
    try:
        # Roles
        roles = ['Project Manager', 'Software Architect', 'Senior Developer', 
                 'SemiSenior Developer', 'Junior Developer', 'QA Engineer', 
                 'UI/UX Designer', 'DevOps Engineer', 'Business Analyst', 'Support Engineer']
        cursor.executemany("INSERT INTO rol (nameRol) VALUES (%s)", [(r,) for r in roles])
        rol_ids = {name: i+1 for i, name in enumerate(roles)}
        
        # Experiencia
        experiences = ['Junior', 'SemiSenior', 'Senior']
        cursor.executemany("INSERT INTO experience (experience) VALUES (%s)", [(e,) for e in experiences])
        exp_ids = {name: i+1 for i, name in enumerate(experiences)}
        
        print("Catálogos de RRHH poblados.")
        return rol_ids, exp_ids
    
    except mysql.connector.Error as err:
        print(f"Error en populate_hr_catalogs: {err}")
        raise

def populate_areas_and_teams(cursor):
    """ Puebla Areas (con tu lista) y Teams. Devuelve mapeos de ID. """
    print("Poblando Áreas de Negocio y Equipos...")
    try:
        cursor.executemany("INSERT INTO area (nameArea) VALUES (%s)", [(a,) for a in AREAS_NEGOCIO])
        area_id_map = {name: i+1 for i, name in enumerate(AREAS_NEGOCIO)}
        print(f"Insertadas {len(area_id_map)} áreas.")

        realistic_team_names = [
            'Equipo Alfa (Fintech)', 'Equipo Beta (Móvil)', 'Equipo Gamma (E-commerce)', 
            'Equipo Delta (Analytics)', 'Squad Titanes (DevOps)', 'Célula Fénix (Seguridad)',
            'Equipo Core (Plataforma)', 'Squad Innovación (I+D)', 'Célula de Soporte',
            'Equipo Omega (QA)', 'Equipo Zeus (Infra)', 'Squad Atenea (UX/UI)'
        ]
        
        # Asegurarnos de tener suficientes nombres o repetir si es necesario
        if NUM_TEAMS > len(realistic_team_names):
            # Si pides más equipos que los de la lista, rellena con genéricos
            team_data = [(name,) for name in realistic_team_names] + \
                        [(f"Equipo Genérico {i+1}",) for i in range(NUM_TEAMS - len(realistic_team_names))]
        else:
            # Selecciona una muestra aleatoria de la lista
            team_names_sample = random.sample(realistic_team_names, NUM_TEAMS)
            team_data = [(name,) for name in team_names_sample]
        
        cursor.executemany("INSERT INTO team (nameTeam) VALUES (%s)", team_data)
        cursor.execute("SELECT idTeam FROM team")
        team_ids = [item[0] for item in cursor.fetchall()]
        print(f"Insertados {len(team_ids)} equipos con nombres realistas.")
        
        return area_id_map, team_ids

    except mysql.connector.Error as err:
        print(f"Error en populate_areas_and_teams: {err}")
        raise
def populate_employees(cursor, rol_ids, exp_ids, team_ids):
    """ Puebla Employees y Team_Members. Devuelve IDs de empleados. """
    print(f"Poblando {NUM_EMPLOYEES} Empleados y asignando equipos...")
    try:
        employee_data = []
        for _ in range(NUM_EMPLOYEES):
            exp_name = random.choice(list(exp_ids.keys()))
            if exp_name == 'Junior':
                rol_name = random.choice(['Junior Developer', 'Support Engineer', 'QA Engineer'])
            elif exp_name == 'SemiSenior':
                rol_name = random.choice(['SemiSenior Developer', 'QA Engineer', 'UI/UX Designer', 'DevOps Engineer'])
            else: # Senior
                rol_name = random.choice(['Senior Developer', 'Software Architect', 'Project Manager', 'Business Analyst'])
            
            employee_data.append((
                fake.name(),
                rol_ids[rol_name],
                exp_ids[exp_name],
                fake.email()
            ))
        
        sql = "INSERT INTO employee (nameEmployee, idRol, idExperience, email) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, employee_data)
        
        cursor.execute("SELECT idEmployee FROM employee")
        employee_ids = [item[0] for item in cursor.fetchall()]
        print(f"Insertados {len(employee_ids)} empleados.")

        team_member_data = []
        assigned_pairs = set() 
        
        CHANCE_TO_LEAVE_TEAM = 0.2 # 20% de probabilidad de que un miembro haya dejado el equipo

        for team_id in team_ids:
            emp_id = random.choice(employee_ids)
            if (team_id, emp_id) not in assigned_pairs:

                assigned_from = fake.date_between(start_date='-2y', end_date='today')
                assigned_to = None
                
                if random.random() < CHANCE_TO_LEAVE_TEAM:
                    # Si han dejado el equipo, la fecha fin debe ser DESPUÉS de la de inicio
                    end_date_start = assigned_from + timedelta(days=90) # Mínimo 3 meses en el equipo
                    end_date_end = datetime.now().date() # Hasta hoy
                    
                    if end_date_start < end_date_end:
                        assigned_to = fake.date_between_dates(date_start=end_date_start, date_end=end_date_end)

                team_member_data.append((team_id, emp_id, assigned_from, assigned_to))
                assigned_pairs.add((team_id, emp_id))
        
        for _ in range(NUM_EMPLOYEES):
            team_id = random.choice(team_ids)
            emp_id = random.choice(employee_ids)
            if (team_id, emp_id) not in assigned_pairs:
                
                assigned_from = fake.date_between(start_date='-2y', end_date='today')
                assigned_to = None
                
                if random.random() < CHANCE_TO_LEAVE_TEAM:
                    end_date_start = assigned_from + timedelta(days=90)
                    end_date_end = datetime.now().date()
                    if end_date_start < end_date_end:
                        assigned_to = fake.date_between_dates(date_start=end_date_start, date_end=end_date_end)

                team_member_data.append((team_id, emp_id, assigned_from, assigned_to))
                assigned_pairs.add((team_id, emp_id))

        sql = "INSERT INTO team_member (idTeam, idEmployee, assignedFrom, assignedTo) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, team_member_data)
        print(f"Insertadas {len(team_member_data)} asignaciones de equipo (con algunas finalizadas).")
        
        return employee_ids

    except mysql.connector.Error as err:
        print(f"Error en populate_employees: {err}")
        raise

def populate_clients(cursor, address_ids):
    """ Puebla Clientes. Devuelve IDs de clientes. """
    print(f"Poblando {NUM_CLIENTS} Clientes...")
    try:
        client_data = []
        # Asegurar que las direcciones no se repitan en clientes
        available_addresses = random.sample(address_ids, NUM_CLIENTS)
        
        for i in range(NUM_CLIENTS):
            client_data.append((
                fake.company(),
                fake.email(),
                fake.phone_number(),
                available_addresses[i]
            ))
        
        sql = "INSERT INTO client (nameClient, contactEmail, contactPhone, idAddress) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, client_data)
        
        cursor.execute("SELECT idClient FROM client")
        client_ids = [item[0] for item in cursor.fetchall()]
        print(f"Insertados {len(client_ids)} clientes.")
        
        return client_ids

    except mysql.connector.Error as err:
        print(f"Error en populate_clients: {err}")
        raise

def generate_realistic_project_name(area_name, client_name):
    """ Genera un nombre de proyecto realista usando las plantillas. """
    if area_name not in project_name_templates:
        return f"Proyecto de {area_name} para {client_name}"

    template = random.choice(project_name_templates[area_name])
    
    # Rellenar placeholders en la plantilla
    replacements = {
        'Noun': random.choice(project_fillers['Noun']),
        'System': random.choice(project_fillers['System']),
        'Module': random.choice(project_fillers['Module']),
        'App': random.choice(project_fillers['App']),
        'Project': random.choice(project_fillers['Project']),
        'Standard': random.choice(project_fillers['Standard']),
        'Feature': random.choice(project_fillers['Feature']),
        'Technology': random.choice(project_fillers['Technology']),
        'Client': client_name.split(' ')[0] 
    }
    
    # Usamos .get() para evitar errores si un placeholder no está en replacements
    for key, value in replacements.items():
        template = template.replace(f"{{{key}}}", value)
        
    return template

def populate_projects(cursor, client_ids, area_id_map, team_ids):
    """ Puebla Proyectos. Devuelve una lista de tuplas de proyecto para referencia. """
    print(f"Poblando {NUM_PROJECTS} Proyectos...")
    project_data = []
    project_reference_list = [] # Guardará (id, start, end, status)
    
    # Necesitamos los nombres de cliente y área para los nombres de proyecto
    cursor.execute("SELECT idClient, nameClient FROM client")
    client_map = dict(cursor.fetchall())
    area_name_map = {v: k for k, v in area_id_map.items()} # Invertir el mapa

    try:
        for _ in range(NUM_PROJECTS):
            # Lógica de Fechas
            plannedStart = fake.date_between(start_date='-2y', end_date='+6m')
            duration_days = random.randint(60, 365)
            plannedEnd = plannedStart + timedelta(days=duration_days)
            
            status = random.choice(['Planificado', 'En Progreso', 'Finalizado', 'Cancelado'])
            actualStart, actualEnd = None, None
            
            if status != 'Planificado':
                actualStart = plannedStart + timedelta(days=random.randint(0, 15)) # Retraso al inicio
            
            if status == 'Finalizado':
                # Retraso o adelanto al final
                end_variation = duration_days + random.randint(-15, 30) 
                actualEnd = actualStart + timedelta(days=end_variation)
                if actualEnd < actualStart: actualEnd = actualStart + timedelta(days=1)
            
            elif status == 'Cancelado':
                # Se cancela a mitad de camino
                cancel_date = actualStart + timedelta(days=random.randint(10, duration_days - 10))
                actualEnd = cancel_date

            idClient = random.choice(client_ids)
            idArea = random.choice(list(area_id_map.values()))
            
            # Generar nombre realista
            client_name = client_map[idClient]
            area_name = area_name_map[idArea]
            project_name = generate_realistic_project_name(area_name, client_name)

            project_data.append((
                project_name,
                idClient,
                idArea,
                random.choice(team_ids),
                plannedStart,
                plannedEnd,
                actualStart,
                actualEnd,
                status,
                random.uniform(20000, 500000) # Budget
                # Costo se deja en 0.00 y se calcula al final
            ))

        sql = """INSERT INTO project (nameProject, idClient, idArea, idTeam, 
                 plannedStart, plannedEnd, actualStart, actualEnd, status, budget) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql, project_data)
        
        # Recuperar IDs y fechas para las tareas
        cursor.execute("SELECT idProject, actualStart, actualEnd, status, plannedStart, plannedEnd FROM project")
        project_reference_list = cursor.fetchall()
        
        print(f"Insertados {len(project_data)} proyectos.")
        return project_reference_list

    except mysql.connector.Error as err:
        print(f"Error en populate_projects: {err}")
        raise

def populate_tasks(cursor, project_list, employee_ids):
    """ Puebla Tareas. Devuelve lista de tuplas de tareas para referencia. """
    print("Poblando Tareas...")
    task_data = []
    task_reference_list = [] # Guardará (id, start, end, employee_id)
    
    try:
        for (proj_id, proj_start, proj_end, proj_status, proj_plan_start, proj_plan_end) in project_list:
            
            # No crear tareas para proyectos 'Planificados' que no han iniciado
            if proj_status == 'Planificado':
                continue
            
            # Definir el rango de fechas real del proyecto
            start_date = proj_start if proj_start else proj_plan_start
            
            if proj_status == 'Finalizado' or proj_status == 'Cancelado':
                end_date = proj_end
            elif proj_status == 'En Progreso':
                end_date = datetime.now().date() # Tareas hasta hoy
            
            if not end_date or end_date < start_date:
                continue # Evitar rangos de fecha inválidos

            num_tasks = random.randint(1, MAX_TASKS_PER_PROJECT)
            
            for _ in range(num_tasks):
                # Lógica de fechas de Tarea (debe estar DENTRO del proyecto)
                task_start = fake.date_between_dates(date_start=start_date, date_end=end_date)
                task_duration = random.randint(5, 45)
                task_end = task_start + timedelta(days=task_duration)
                
                # Asegurar que la tarea no termine después que el proyecto
                if task_end > end_date:
                    task_end = end_date
                
                estimated_hours = random.randint(10, 80)
                
                # Simular horas reales (factor de desviación)
                actual_hours = round(estimated_hours * random.uniform(0.8, 1.3), 2)
                
                task_data.append((
                    proj_id,
                    fake.bs().capitalize(), # Título de tarea
                    random.choice(employee_ids),
                    task_start,
                    task_end,
                    task_start + timedelta(days=random.randint(0,2)), # actualStart
                    task_end + timedelta(days=random.randint(-1,3)), # actualEnd
                    'Completada' if proj_status == 'Finalizado' else 'En Progreso',
                    estimated_hours,
                    actual_hours
                ))

        sql = """INSERT INTO task (idProject, title, assignedTo, plannedStart, plannedEnd, 
                 actualStart, actualEnd, status, estimatedHours, actualHours)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql, task_data)
        
        # Recuperar IDs para Timesheet
        cursor.execute("SELECT idTask, actualStart, actualEnd, assignedTo, actualHours FROM task")
        task_reference_list = cursor.fetchall()
        
        print(f"Insertadas {len(task_data)} tareas.")
        return task_reference_list

    except mysql.connector.Error as err:
        print(f"Error en populate_tasks: {err}")
        raise

def generate_realistic_expense_desc(project_area_name):
    """ Genera una descripción y monto de gasto realista. """
    
    # Elegir un tipo de gasto
    # Si el proyecto es de Infra, es más probable que haya gastos de Hardware/Cloud
    if project_area_name in ['Infraestructura y Redes', 'Operaciones y Automatización (DevOps)']:
        category = random.choice(['Cloud', 'Hardware', 'Software'])
    else:
        category = random.choice(list(expense_templates.keys()))
    
    template, amount_range = expense_templates[category]
    amount = round(random.uniform(amount_range[0], amount_range[1]), 2)
    
    # Rellenar placeholders
    replacements = {
        'Software': random.choice(expense_fillers['Software']),
        'Cloud_Provider': random.choice(expense_fillers['Cloud_Provider']),
        'Hardware': random.choice(expense_fillers['Hardware']),
        'Topic': random.choice(expense_fillers['Topic']),
        'Technology': random.choice(expense_fillers['Technology']),
    }
    
    for key, value in replacements.items():
        template = template.replace(f"{{{key}}}", value)
        
    return template, amount

def populate_expenses(cursor, project_list, area_id_map):
    """ Puebla Gastos (Expense) con descripciones realistas. """
    print("Poblando Gastos...")
    expense_data = []
    area_name_map = {v: k for k, v in area_id_map.items()}
    
    # Necesitamos el area_id de cada proyecto
    cursor.execute("SELECT idProject, idArea FROM project")
    project_area_map = dict(cursor.fetchall())

    try:
        for (proj_id, proj_start, proj_end, proj_status, _, _) in project_list:
            
            if proj_status == 'Planificado':
                continue
                
            start_date = proj_start if proj_start else datetime.now().date() - timedelta(days=365)
            end_date = proj_end if proj_end else datetime.now().date()
            
            if not end_date or end_date < start_date:
                continue

            num_expenses = random.randint(0, MAX_EXPENSES_PER_PROJECT)
            
            for _ in range(num_expenses):
                proj_area_id = project_area_map.get(proj_id)
                proj_area_name = area_name_map.get(proj_area_id, 'Desarrollo de Software') # Default
                
                description, amount = generate_realistic_expense_desc(proj_area_name)
                
                expense_data.append((
                    proj_id,
                    description,
                    amount,
                    fake.date_between_dates(date_start=start_date, date_end=end_date)
                ))

        sql = "INSERT INTO expense (idProject, description, amount, expenseDate) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, expense_data)
        print(f"Insertados {len(expense_data)} gastos.")

    except mysql.connector.Error as err:
        print(f"Error en populate_expenses: {err}")
        raise

def populate_timesheets(cursor, task_list):
    """ Puebla Timesheet basado en las horas reales de la tarea. """
    print("Poblando Hojas de Tiempo (Timesheet)...")
    timesheet_data = []
    
    # --- LÓGICA DE BATCH AÑADIDA ---
    BATCH_SIZE = 5000  # Enviaremos los datos en lotes de 5000
    total_inserted = 0
    
    try:
        # Definimos el SQL aquí, fuera del bucle
        sql = "INSERT INTO timesheet (idTask, idEmployee, workDate, `hours`) VALUES (%s, %s, %s, %s)"

        for (task_id, task_start, task_end, employee_id, actual_hours) in task_list:
            
            if not task_start or not task_end or not actual_hours or actual_hours <= 0:
                continue
            
            if task_end < task_start:
                task_end = task_start + timedelta(days=1) 

            hours_logged = Decimal('0.00')
            
            for _ in range(random.randint(2, MAX_TIMESHEETS_PER_TASK)): 
                if hours_logged >= actual_hours:
                    break
                
                random_float_str = str(round(random.uniform(4, 9), 2))
                hours_to_log = Decimal(random_float_str)
                
                if hours_logged + hours_to_log > actual_hours:
                    hours_to_log = actual_hours - hours_logged
                
                if hours_to_log <= Decimal('0.0'):
                    break

                work_date = fake.date_between_dates(date_start=task_start, date_end=task_end)
                
                timesheet_data.append((
                    task_id,
                    employee_id,
                    work_date,
                    hours_to_log 
                ))
                
                # --- LÓGICA DE BATCH AÑADIDA ---
                # Si el lote alcanza el tamaño, lo insertamos y lo vaciamos
                if len(timesheet_data) >= BATCH_SIZE:
                    cursor.executemany(sql, timesheet_data)
                    total_inserted += len(timesheet_data)
                    print(f"  ... insertado lote de {len(timesheet_data)} (total: {total_inserted})")
                    timesheet_data = [] # Limpiamos la lista para el siguiente lote

        # --- LÓGICA DE BATCH AÑADIDA ---
        # Insertar el último lote restante (el que no llegó a 5000)
        if timesheet_data:
            cursor.executemany(sql, timesheet_data)
            total_inserted += len(timesheet_data)
            print(f"  ... insertado lote final de {len(timesheet_data)} (total: {total_inserted})")

        print(f"Insertadas {total_inserted} entradas de tiempo en total.")

    except mysql.connector.Error as err:
        print(f"Error en populate_timesheets: {err}")
        raise
    except Exception as e:
        print(f"Error inesperado en populate_timesheets: {e}")
        raise

def update_project_costs(cursor):
    """ Actualiza el costo real del proyecto sumando gastos y horas. """
    print("Calculando y actualizando costos de proyectos...")
    try:
        # Primero, asegurar que actualHours en Task sea la suma de Timesheet
        # (Aunque en este script simulamos al revés, en un caso real haríamos esto)
        # Para este script, nos basamos en el actualHours ya calculado en Task.
        
        sql = f"""
        UPDATE project p
        SET p.cost = (
            SELECT IFNULL(SUM(e.amount), 0)
            FROM expense e
            WHERE e.idProject = p.idProject
        ) + (
            SELECT IFNULL(SUM(t.actualHours), 0) * {COST_PER_HOUR}
            FROM task t
            WHERE t.idProject = p.idProject
        )
        WHERE p.idProject > 0;
        """
        cursor.execute(sql)
        print(f"Costos actualizados usando una tarifa de {COST_PER_HOUR}/hora.")
        
    except mysql.connector.Error as err:
        print(f"Error en update_project_costs: {err}")
        raise

# --- FUNCIÓN PRINCIPAL ---
def main():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Limpiar todo
        clear_tables(cursor)

        # FASE 1: Catálogos de Ubicación
        city_ids, address_ids = populate_locations(cursor)
        
        # FASE 2: Catálogos de RRHH y Proyectos
        rol_ids, exp_ids = populate_hr_catalogs(cursor)
        area_id_map, team_ids = populate_areas_and_teams(cursor)
        
        # FASE 3: Entidades (Empleados, Clientes)
        employee_ids = populate_employees(cursor, rol_ids, exp_ids, team_ids)
        client_ids = populate_clients(cursor, address_ids)
        
        # FASE 4: Proyectos (El corazón)
        project_list = populate_projects(cursor, client_ids, area_id_map, team_ids)

        # FASE 5: Tareas y Gastos
        task_list = populate_tasks(cursor, project_list, employee_ids)
        populate_expenses(cursor, project_list, area_id_map) # Depende de la lógica de negocio

        # FASE 6: Grano Fino (Timesheet)
        populate_timesheets(cursor, task_list)
        
        # FASE 7: Cálculos finales
        update_project_costs(cursor)

        # Guardar cambios
        connection.commit()
        print("\n¡Éxito! La base de datos ha sido poblada con datos sintéticos realistas.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Credenciales de MySQL incorrectas (usuario/contraseña).")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Error: La base de datos '{DB_CONFIG['database']}' no existe.")
        elif err.errno == 1049: # Unknown database
             print(f"Error: La base de datos '{DB_CONFIG['database']}' no existe.")
        elif err.errno == 2003: # Can't connect
             print(f"Error: No se pudo conectar a MySQL en {DB_CONFIG['host']}:{DB_CONFIG['port']}.")
        else:
            print(f"Error de MySQL: {err}")
        if connection:
            connection.rollback() # Revertir cambios en caso de error
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada.")

if __name__ == "__main__":
    main()
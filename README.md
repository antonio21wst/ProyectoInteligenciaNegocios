# Sistema de Soporte de Decisiones (DSS) para Empresa de Desarrollo de Software

![BUAP Logo](https://www.buap.mx/sites/default/files/logo_buap_0.png)

> **Curso:** Inteligencia de Negocios  
> [cite_start]**Institución:** Benemérita Universidad Autónoma de Puebla (BUAP) - Facultad de Ciencias de la Computación [cite: 7, 8, 9]

## Descripción del Proyecto

[cite_start]Este proyecto consiste en el diseño e implementación de un **Sistema de Soporte de Decisiones (DSS)** orientado a una empresa de desarrollo de software[cite: 25, 40]. [cite_start]El objetivo principal es transformar los datos operativos en información estratégica mediante un proceso ETL, un Data Warehouse y herramientas analíticas[cite: 27, 40].

[cite_start]El sistema permite automatizar y centralizar la información para mejorar la eficiencia operativa y fomentar una cultura basada en evidencia[cite: 30, 31].

## Objetivos

* [cite_start]**Automatización:** Implementación de un proceso ETL (Extracción, Transformación y Carga)[cite: 42].
* [cite_start]**Análisis Multidimensional:** Creación de un cubo OLAP para análisis flexibles[cite: 43].
* [cite_start]**Estrategia:** Integración de un *Balanced Scorecard* con OKRs definidos[cite: 44].
* [cite_start]**Predicción:** Implementación de un modelo predictivo basado en la distribución de Rayleigh para estimación de defectos[cite: 45].

## Arquitectura del Sistema

[cite_start]La solución sigue un flujo de datos estructurado en capas[cite: 48, 50]:

1.  [cite_start]**Fuentes de Datos (Sistema de Gestión):** Base de datos operativa con información de proyectos, tareas, recursos y costos[cite: 51, 67].
2.  [cite_start]**Proceso ETL:** Extracción, limpieza y transformación de datos para corregir inconsistencias y estandarizar formatos[cite: 53, 71].
3.  [cite_start]**Data Warehouse (DW):** Repositorio centralizado optimizado para consultas complejas[cite: 56].
4.  [cite_start]**Cubo OLAP:** Modelo multidimensional para operaciones de *slice, dice, roll-up* y *drill-down*[cite: 58, 74].
5.  **Visualización:**
    * [cite_start]**Dashboard Estratégico:** Paneles interactivos[cite: 60].
    * [cite_start]**Balanced Scorecard:** Tablero de control organizado en 4 perspectivas[cite: 62].

## Métricas Clave (KPIs y OKRs)

[cite_start]El sistema monitorea indicadores críticos para la "Visión 2030" de la empresa[cite: 107]:

### KPIs Principales
* [cite_start]**Financieros:** Presupuesto Total, Costo Real y % de Cumplimiento (Ejecución)[cite: 86, 88].
* [cite_start]**Talento:** Calidad del Talento (Seniority ponderado) y Equilibrio de Equipos[cite: 92, 93].
* [cite_start]**Operativos:** Eficiencia de Costos por Cliente y Distribución de Proyectos por Área/Localidad[cite: 97, 98].

### OKRs (Objetivos y Resultados Clave)
1.  [cite_start]**Financiera:** Alcanzar un 25% de Margen de Rentabilidad[cite: 111].
2.  [cite_start]**Clientes:** Lograr una cartera de 30 Clientes Activos[cite: 114].
3.  [cite_start]**Procesos Internos:** Asegurar que el 85% de los proyectos se entreguen dentro del presupuesto[cite: 117].
4.  [cite_start]**Aprendizaje:** Mantener una distribución de talento dominada por perfiles Senior/Expertos[cite: 119].

## Modelado de Datos

El proyecto evoluciona desde un esquema relacional transaccional hacia un esquema de estrella/opo de nieve para el análisis:

* [cite_start]**Base de Datos de Gestión:** Enfocada en transacciones diarias (Proyectos, Empleados, Tareas)[cite: 121].
* [cite_start]**Base de Datos de Decisiones (DW):** Esquema dimensional con tablas de hechos (`Fact_Project`) y dimensiones (`dim_time`, `dim_client`, `dim_team`, `dim_employee`, etc.)[cite: 133, 166].

## Equipo de Desarrollo

* [cite_start]**Francisco Soriano Rojas** [cite: 17]
* [cite_start]**Jose Antonio Coyotzi Juarez** [cite: 18]
* [cite_start]**Jose Eduardo Flores Parra** [cite: 19]
* [cite_start]**Edaid Ramirez Valencia** [cite: 20]

[cite_start]**Docente:** Gustavo Emilio Mendoza Olguin [cite: 21]

---
© 2025 - Ingeniería en Tecnologías de la Información

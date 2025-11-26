# Arquitectura del Sistema

## Visión General

El sistema está construido con una arquitectura de microservicios, donde cada servicio tiene una responsabilidad específica y se comunica a través de HTTP/REST.

## Componentes Principales

### 1. Frontend (Streamlit)
- **Tecnología:** Streamlit
- **Puerto:** 8501
- **Responsabilidad:** Interfaz de usuario web
- **Páginas:**
  - Dashboard principal
  - Gestión de Equipos
  - Gestión de Proveedores
  - Gestión de Mantenimientos
  - Reportes y Análisis

### 2. API Gateway
- **Tecnología:** FastAPI
- **Puerto:** 8000
- **Responsabilidad:** 
  - Punto de entrada único
  - Enrutamiento de peticiones
  - CORS y seguridad básica

### 3. Microservicios Backend

#### Equipos Service
- **Puerto:** 8001
- **Responsabilidad:** CRUD de equipos, categorías, ubicaciones, movimientos

#### Proveedores Service
- **Puerto:** 8002
- **Responsabilidad:** CRUD de proveedores y contratos

#### Mantenimiento Service
- **Puerto:** 8003
- **Responsabilidad:** CRUD de mantenimientos, calendario, estadísticas

#### Reportes Service
- **Puerto:** 8004
- **Responsabilidad:** Generación de reportes, dashboard, exportación PDF/Excel

#### Agent Service
- **Puerto:** 8005
- **Responsabilidad:** Agentes inteligentes, notificaciones, alertas

### 4. Base de Datos
- **Tecnología:** PostgreSQL 15
- **Puerto:** 5432
- **Responsabilidad:** Almacenamiento persistente

## Flujo de Datos

1. Usuario accede al Frontend (Streamlit)
2. Frontend hace peticiones al API Gateway
3. API Gateway enruta a los microservicios correspondientes
4. Microservicios consultan/actualizan la base de datos PostgreSQL
5. Respuestas se devuelven al Frontend

## Comunicación entre Servicios

- **Frontend ↔ API Gateway:** HTTP REST
- **API Gateway ↔ Microservicios:** HTTP REST (httpx)
- **Microservicios ↔ PostgreSQL:** asyncpg (async PostgreSQL driver)

## Despliegue

El sistema se despliega usando Docker Compose, donde cada servicio corre en su propio contenedor.

## Escalabilidad

Cada microservicio puede escalarse independientemente según la carga.

## Seguridad

- Health checks en todos los servicios
- Variables de entorno para configuración sensible
- Red Docker aislada para comunicación entre servicios


# Documentación de API

## Endpoints Principales

### API Gateway
**Base URL:** `http://localhost:8000`

### Equipos

#### GET /api/equipos
Obtiene lista de equipos con filtros opcionales.

**Parámetros de consulta:**
- `categoria` (opcional): Filtrar por categoría
- `estado` (opcional): Filtrar por estado operativo
- `ubicacion` (opcional): Filtrar por ubicación

**Ejemplo:**
```bash
GET /api/equipos?estado=operativo&categoria=Laptop
```

#### GET /api/equipos/{equipo_id}
Obtiene detalles de un equipo específico.

#### POST /api/equipos
Crea un nuevo equipo.

**Body:**
```json
{
  "codigo_inventario": "EQ-2024-001",
  "categoria_id": 1,
  "nombre": "Laptop Dell Inspiron",
  "marca": "Dell",
  "modelo": "Inspiron 15 3000",
  "estado_operativo": "operativo"
}
```

#### PUT /api/equipos/{equipo_id}
Actualiza un equipo existente.

#### DELETE /api/equipos/{equipo_id}
Elimina un equipo.

### Proveedores

#### GET /api/proveedores
Obtiene lista de proveedores.

**Parámetros:**
- `activo` (opcional): Filtrar por estado activo/inactivo

#### GET /api/proveedores/{proveedor_id}
Obtiene detalles de un proveedor.

#### POST /api/proveedores
Crea un nuevo proveedor.

#### PUT /api/proveedores/{proveedor_id}
Actualiza un proveedor.

### Mantenimientos

#### GET /api/mantenimientos
Obtiene lista de mantenimientos.

**Parámetros:**
- `equipo_id` (opcional)
- `estado` (opcional)
- `tipo` (opcional): 'preventivo' o 'correctivo'

#### POST /api/mantenimientos
Crea un nuevo mantenimiento.

#### GET /api/mantenimientos/calendario
Obtiene calendario de mantenimientos programados.

### Reportes

#### GET /api/reportes/dashboard
Obtiene métricas del dashboard.

#### GET /api/reportes/equipos-por-ubicacion
Distribución de equipos por ubicación.

#### GET /api/reportes/equipos-por-estado
Distribución de equipos por estado.

#### POST /api/reportes/export/pdf
Exporta reporte a PDF.

#### POST /api/reportes/export/excel
Exporta reporte a Excel.

### Agentes

#### POST /api/agents/run-all-agents
Ejecuta todos los agentes inteligentes.

#### GET /api/agents/notificaciones
Obtiene notificaciones del sistema.

## Códigos de Estado HTTP

- `200`: Éxito
- `201`: Creado
- `400`: Solicitud incorrecta
- `404`: No encontrado
- `500`: Error del servidor
- `503`: Servicio no disponible

## Autenticación

Actualmente el sistema no requiere autenticación. En producción se implementará JWT.


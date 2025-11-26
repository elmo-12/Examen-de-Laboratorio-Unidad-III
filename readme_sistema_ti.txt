# Sistema de Gestión de Equipos de TI - Universidad

## 📋 Descripción
Sistema integral para la gestión de equipos de tecnología en universidades públicas, implementado con arquitectura de microservicios.

## 🏗️ Arquitectura

### Microservicios
- **API Gateway** (Puerto 8000): Punto de entrada único
- **Equipos Service** (Puerto 8001): Gestión de inventario
- **Proveedores Service** (Puerto 8002): Gestión de proveedores
- **Mantenimiento Service** (Puerto 8003): Gestión de mantenimientos
- **Reportes Service** (Puerto 8004): Generación de reportes y análisis
- **Frontend Streamlit** (Puerto 8501): Interfaz de usuario
- **PostgreSQL** (Puerto 5432): Base de datos
- **Agent Service** (Puerto 8005): Agentes inteligentes para automatización

## 🚀 Instalación

### Prerrequisitos
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espacio en disco

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd sistema-gestion-ti
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Construir y levantar servicios**
```bash
docker-compose build
docker-compose up -d
```

4. **Inicializar base de datos**
```bash
docker-compose exec api-gateway python init_db.py
```

5. **Acceder a la aplicación**
- Frontend: http://localhost:8501
- API Gateway: http://localhost:8000/docs

## 📊 Estructura del Proyecto

```
sistema-gestion-ti/
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_📦_Equipos.py
│   │   ├── 2_🏢_Proveedores.py
│   │   ├── 3_🔧_Mantenimiento.py
│   │   └── 4_📊_Reportes.py
│   ├── requirements.txt
│   └── Dockerfile
├── services/
│   ├── api_gateway/
│   ├── equipos_service/
│   ├── proveedores_service/
│   ├── mantenimiento_service/
│   ├── reportes_service/
│   └── agent_service/
├── database/
│   └── schema.sql
├── docker-compose.yml
└── README.md
```

## 🗄️ Modelo de Datos

### Tablas Principales
- **proveedores**: Información de proveedores
- **equipos**: Inventario de equipos
- **ubicaciones**: Ubicaciones físicas
- **movimientos_equipos**: Historial de movimientos
- **mantenimientos**: Registro de mantenimientos
- **contratos**: Contratos con proveedores

## 🔧 Funcionalidades

### 1. Gestión de Proveedores
- ✅ Registro y actualización
- ✅ Historial de compras
- ✅ Gestión de contratos
- ✅ Búsqueda y filtrado

### 2. Gestión de Equipos
- ✅ Inventario completo
- ✅ Historial de asignaciones
- ✅ Rastreo de ubicación
- ✅ Estados operativos
- ✅ Códigos QR/Barras

### 3. Gestión de Mantenimiento
- ✅ Mantenimientos preventivos/correctivos
- ✅ Calendario de programación
- ✅ Historial de costos
- ✅ Alertas automáticas

### 4. Reportes y Análisis
- ✅ Dashboard interactivo
- ✅ Gráficos estadísticos
- ✅ Exportación PDF/Excel
- ✅ Métricas clave

### 5. Agentes Inteligentes
- ✅ Recordatorios de mantenimiento
- ✅ Alertas de equipos obsoletos
- ✅ Notificaciones de garantías
- ✅ Análisis predictivo

## 🔐 Seguridad
- Autenticación JWT
- Encriptación de datos sensibles
- Logs de auditoría
- Roles y permisos

## 📈 Monitoreo
- Health checks automáticos
- Logs centralizados
- Métricas de rendimiento

## 🛠️ Mantenimiento

### Backup de Base de Datos
```bash
docker-compose exec postgres pg_dump -U postgres ti_management > backup.sql
```

### Restaurar Base de Datos
```bash
docker-compose exec -T postgres psql -U postgres ti_management < backup.sql
```

### Ver logs
```bash
docker-compose logs -f <service-name>
```

### Reiniciar servicios
```bash
docker-compose restart <service-name>
```

## 🧪 Testing
```bash
# Ejecutar tests
docker-compose exec <service-name> pytest

# Coverage
docker-compose exec <service-name> pytest --cov
```

## 📝 API Documentation
Una vez levantado el sistema, acceder a:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contribución
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia
MIT License

## 👥 Contacto
Universidad - Departamento de TI
Email: ti@universidad.edu

## 🙏 Agradecimientos
- Comunidad Streamlit
- FastAPI Framework
- PostgreSQL Team
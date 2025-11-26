# Guía de Despliegue

## Requisitos Previos

- Docker 20.10 o superior
- Docker Compose 2.0 o superior
- Mínimo 4GB de RAM
- 10GB de espacio en disco

## Despliegue Local

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd sistema-gestion-ti
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Construir las Imágenes
```bash
docker-compose build
```

### 4. Iniciar los Servicios
```bash
docker-compose up -d
```

### 5. Verificar el Estado
```bash
docker-compose ps
```

### 6. Ver Logs
```bash
docker-compose logs -f
```

## Despliegue en Producción

### Consideraciones de Seguridad

1. **Cambiar contraseñas por defecto**
   - Editar `.env` con contraseñas seguras
   - Cambiar `POSTGRES_PASSWORD`
   - Cambiar `SECRET_KEY` para JWT

2. **Configurar HTTPS**
   - Usar un proxy reverso (nginx/traefik)
   - Configurar certificados SSL

3. **Backups regulares**
   - Configurar cron job para backups automáticos
   - Almacenar backups en ubicación segura

### Variables de Entorno en Producción

```env
ENVIRONMENT=production
DEBUG=false
POSTGRES_PASSWORD=<password-segura>
SECRET_KEY=<clave-secreta-aleatoria>
```

## Monitoreo

### Health Checks
Todos los servicios tienen health checks configurados:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
# etc.
```

### Logs
```bash
# Ver logs de un servicio específico
docker-compose logs -f api-gateway

# Ver logs de todos los servicios
docker-compose logs -f
```

## Mantenimiento

### Backup de Base de Datos
```bash
./scripts/backup_db.sh
```

### Restaurar Base de Datos
```bash
./scripts/restore_db.sh backups/backup_ti_management_20240101_120000.sql.gz
```

### Actualizar Servicios
```bash
docker-compose pull
docker-compose up -d --build
```

### Reiniciar un Servicio
```bash
docker-compose restart <service-name>
```

## Troubleshooting

### Servicio no inicia
1. Verificar logs: `docker-compose logs <service-name>`
2. Verificar variables de entorno
3. Verificar conectividad entre servicios

### Base de datos no conecta
1. Verificar que PostgreSQL esté corriendo
2. Verificar credenciales en `.env`
3. Verificar que el esquema se haya ejecutado

### Puerto ya en uso
1. Cambiar puerto en `.env`
2. O detener el proceso que usa el puerto

## Escalado

Para escalar un servicio específico:
```bash
docker-compose up -d --scale equipos-service=3
```


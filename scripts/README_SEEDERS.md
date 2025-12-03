# 🌱 Seeders de Base de Datos

Este directorio contiene scripts para poblar la base de datos con datos de ejemplo.

## 📋 Archivos

- **`seed_db.py`**: Script principal de seeders (Python con asyncpg)
- **`run_seeders.sh`**: Script bash para ejecutar desde Linux/Mac
- **`run_seeders.ps1`**: Script PowerShell para ejecutar desde Windows

## 🚀 Formas de Ejecutar

### Opción 1: Desde el Host (Recomendado)

**Requisitos:**
- Python 3.8+
- `asyncpg` instalado: `pip install asyncpg`

**Ejecutar:**
```bash
# Linux/Mac
python scripts/seed_db.py

# Windows
python scripts\seed_db.py
```

### Opción 2: Desde Docker (si el servicio tiene Python)

```bash
# Copiar el script al contenedor
docker cp scripts/seed_db.py reportes-service:/app/scripts/seed_db.py

# Ejecutar
docker-compose exec reportes-service python /app/scripts/seed_db.py
```

### Opción 3: Usando los Scripts Auxiliares

```bash
# Linux/Mac
bash scripts/run_seeders.sh

# Windows PowerShell
.\scripts\run_seeders.ps1
```

## 📊 Datos que se Insertan

El script inserta los siguientes datos de ejemplo:

| Tabla | Cantidad | Descripción |
|-------|----------|-------------|
| **Usuarios** | 5 | Admin, técnicos y usuarios regulares |
| **Ubicaciones** | 12 | Aulas, oficinas, laboratorios |
| **Proveedores** | 4 | Proveedores con información completa |
| **Contratos** | 8-12 | 2-3 contratos por proveedor |
| **Equipos** | 50-90 | 5-10 equipos por categoría |
| **Mantenimientos** | 25-50 | Preventivos y correctivos |
| **Movimientos** | 15-30 | Historial de movimientos de equipos |
| **Notificaciones** | 20 | Notificaciones de ejemplo |

## ⚙️ Configuración

El script usa la variable de entorno `DATABASE_URL` o un valor por defecto:

```bash
# Ejemplo de configuración
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/ti_management"
```

O desde `.env`:
```
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/ti_management
```

## 🔍 Verificación

Después de ejecutar los seeders, puedes verificar los datos:

```sql
-- Conectarse a la base de datos
docker-compose exec postgres psql -U postgres -d ti_management

-- Ver conteos
SELECT 
    'usuarios' as tabla, COUNT(*) as total FROM usuarios
UNION ALL
SELECT 'equipos', COUNT(*) FROM equipos
UNION ALL
SELECT 'proveedores', COUNT(*) FROM proveedores
UNION ALL
SELECT 'mantenimientos', COUNT(*) FROM mantenimientos;
```

## ⚠️ Notas Importantes

1. **Datos Existentes**: El script pregunta antes de continuar si ya hay datos en la base de datos.

2. **Orden de Inserción**: Los datos se insertan en el orden correcto respetando las foreign keys:
   - Usuarios → Ubicaciones → Proveedores → Contratos → Equipos → Mantenimientos → Movimientos → Notificaciones

3. **Datos Aleatorios**: Algunos datos son generados aleatoriamente (fechas, costos, etc.) para simular un entorno real.

4. **Contraseñas**: Todas las contraseñas de ejemplo son `admin123` (hash: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ`)

## 🐛 Solución de Problemas

### Error: "No module named 'asyncpg'"
```bash
pip install asyncpg
```

### Error: "Connection refused"
- Verifica que PostgreSQL esté corriendo: `docker-compose ps`
- Verifica la URL de conexión en `DATABASE_URL`

### Error: "relation does not exist"
- Ejecuta primero `init_db.py` para crear las tablas:
```bash
python scripts/init_db.py
```

## 📝 Personalización

Puedes modificar los datos en `seed_db.py`:
- Agregar más usuarios en `USUARIOS`
- Agregar más proveedores en `PROVEEDORES`
- Modificar ubicaciones en `UBICACIONES`
- Ajustar cantidades de equipos por categoría


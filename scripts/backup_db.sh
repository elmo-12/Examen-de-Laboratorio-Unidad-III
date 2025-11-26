#!/bin/bash
# Script para hacer backup de la base de datos PostgreSQL

# Configuración
DB_NAME=${POSTGRES_DB:-ti_management}
DB_USER=${POSTGRES_USER:-postgres}
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

echo "🔄 Iniciando backup de la base de datos..."
echo "📁 Base de datos: $DB_NAME"
echo "👤 Usuario: $DB_USER"
echo "📍 Host: $DB_HOST:$DB_PORT"

# Ejecutar pg_dump
if docker-compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"; then
    # Comprimir el backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    echo "✅ Backup completado exitosamente"
    echo "📦 Archivo: $BACKUP_FILE"
    echo "📊 Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    echo "❌ Error al realizar el backup"
    exit 1
fi


#!/bin/bash
# Script para restaurar la base de datos PostgreSQL desde un backup

# Configuración
DB_NAME=${POSTGRES_DB:-ti_management}
DB_USER=${POSTGRES_USER:-postgres}
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}

# Verificar que se proporcionó el archivo de backup
if [ -z "$1" ]; then
    echo "❌ Error: Debe especificar el archivo de backup"
    echo "Uso: ./restore_db.sh <archivo_backup.sql[.gz]>"
    exit 1
fi

BACKUP_FILE="$1"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: El archivo de backup no existe: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ADVERTENCIA: Esta operación eliminará todos los datos actuales"
echo "📁 Archivo de backup: $BACKUP_FILE"
read -p "¿Desea continuar? (s/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo "🔄 Restaurando base de datos..."

# Si el archivo está comprimido, descomprimirlo temporalmente
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "📦 Descomprimiendo archivo..."
    TEMP_FILE=$(mktemp)
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    BACKUP_FILE="$TEMP_FILE"
fi

# Restaurar la base de datos
if docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"; then
    echo "✅ Base de datos restaurada exitosamente"
    
    # Limpiar archivo temporal si se creó
    if [ -n "$TEMP_FILE" ]; then
        rm "$TEMP_FILE"
    fi
else
    echo "❌ Error al restaurar la base de datos"
    exit 1
fi


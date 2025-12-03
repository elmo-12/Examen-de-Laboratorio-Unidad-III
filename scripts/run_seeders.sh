#!/bin/bash
# Script para ejecutar seeders desde Docker

echo "🌱 Ejecutando seeders de la base de datos..."

# Verificar que Docker Compose esté corriendo
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Los servicios de Docker Compose no están corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

# Ejecutar seeders usando el servicio de reportes (tiene todas las dependencias)
echo "📦 Ejecutando seeders desde el contenedor..."
docker-compose exec -T reportes-service python /app/scripts/seed_db.py

if [ $? -eq 0 ]; then
    echo "✅ Seeders ejecutados exitosamente"
else
    echo "❌ Error al ejecutar seeders"
    exit 1
fi


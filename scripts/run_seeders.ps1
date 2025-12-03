# Script PowerShell para ejecutar seeders desde Docker (Windows)

Write-Host "🌱 Ejecutando seeders de la base de datos..." -ForegroundColor Cyan

# Verificar que Docker Compose esté corriendo
$services = docker-compose ps 2>$null
if (-not $services -or $services -notmatch "Up") {
    Write-Host "❌ Error: Los servicios de Docker Compose no están corriendo" -ForegroundColor Red
    Write-Host "   Ejecuta: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Ejecutar seeders usando el servicio de reportes (tiene todas las dependencias)
Write-Host "📦 Ejecutando seeders desde el contenedor..." -ForegroundColor Cyan
docker-compose exec -T reportes-service python /app/scripts/seed_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Seeders ejecutados exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error al ejecutar seeders" -ForegroundColor Red
    exit 1
}




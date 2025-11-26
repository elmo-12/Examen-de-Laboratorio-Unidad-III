# Script para limpiar archivos duplicados
# Estos archivos ya están organizados en sus respectivas carpetas

Write-Host "🗑️ Limpiando archivos duplicados..." -ForegroundColor Yellow

$archivos_duplicados = @(
    "agent_service.py",
    "equipos_service_code.py",
    "frontend_app.py",
    "frontend_equipos.py",
    "frontend_reportes.py",
    "proveedores_service.py",
    "reportes_service.py",
    "requirements_frontend.txt",
    "env_example.sh"
)

foreach ($archivo in $archivos_duplicados) {
    if (Test-Path $archivo) {
        Write-Host "  Eliminando: $archivo" -ForegroundColor Gray
        Remove-Item $archivo -Force
    }
}

Write-Host "✅ Limpieza completada" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Estructura actual del proyecto:"
Write-Host "  - services/       (microservicios organizados)"
Write-Host "  - frontend/       (aplicación Streamlit)"
Write-Host "  - database/       (esquemas SQL)"
Write-Host "  - scripts/        (utilidades)"
Write-Host "  - docs/           (documentación)"


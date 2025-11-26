from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import asyncpg
import os
from datetime import datetime, date
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

app = FastAPI(title="Reportes Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL")

# Pool de conexiones global
_pool = None

async def get_db_pool():
    """Obtiene o crea el pool de conexiones a la base de datos"""
    global _pool
    
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
            timeout=30
        )
    
    return _pool

@app.on_event("startup")
async def startup():
    """Inicializar el pool de conexiones al iniciar la aplicación"""
    global _pool
    _pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
        timeout=30
    )

@app.on_event("shutdown")
async def shutdown():
    """Cerrar el pool de conexiones al apagar la aplicación"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "reportes"}

@app.get("/dashboard")
async def get_dashboard():
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            total_equipos = await conn.fetchval("SELECT COUNT(*) FROM equipos")
            
            equipos_operativos = await conn.fetchval(
                "SELECT COUNT(*) FROM equipos WHERE estado_operativo = 'operativo'"
            )
            
            equipos_reparacion = await conn.fetchval(
                "SELECT COUNT(*) FROM equipos WHERE estado_operativo = 'en_reparacion'"
            )
            
            valor_inventario = await conn.fetchval(
                "SELECT COALESCE(SUM(costo_compra), 0) FROM equipos"
            )
            
            mantenimientos_mes = await conn.fetchval("""
                SELECT COUNT(*) FROM mantenimientos
                WHERE EXTRACT(MONTH FROM fecha_programada) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_programada) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            
            costo_mantenimiento_mes = await conn.fetchval("""
                SELECT COALESCE(SUM(costo), 0) FROM mantenimientos
                WHERE EXTRACT(MONTH FROM fecha_realizada) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_realizada) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            
            return {
                "total_equipos": total_equipos,
                "equipos_operativos": equipos_operativos,
                "equipos_reparacion": equipos_reparacion,
                "tasa_disponibilidad": round((equipos_operativos / total_equipos * 100) if total_equipos > 0 else 0, 2),
                "valor_inventario": float(valor_inventario),
                "mantenimientos_mes": mantenimientos_mes,
                "costo_mantenimiento_mes": float(costo_mantenimiento_mes)
            }
    except Exception as e:
        import traceback
        print(f"Error en dashboard: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al obtener dashboard: {str(e)}")

@app.get("/equipos-por-ubicacion")
async def get_equipos_por_ubicacion():
    pool = await get_db_pool()
    
    query = """
        SELECT u.edificio || ' - ' || u.aula_oficina as ubicacion,
               COUNT(*) as cantidad
        FROM equipos e
        JOIN ubicaciones u ON e.ubicacion_actual_id = u.id
        GROUP BY u.id, u.edificio, u.aula_oficina
        ORDER BY cantidad DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.get("/equipos-por-estado")
async def get_equipos_por_estado():
    pool = await get_db_pool()
    
    query = """
        SELECT estado_operativo as estado, COUNT(*) as cantidad
        FROM equipos
        GROUP BY estado_operativo
        ORDER BY cantidad DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.get("/equipos-por-categoria")
async def get_equipos_por_categoria():
    pool = await get_db_pool()
    
    query = """
        SELECT c.nombre as categoria, COUNT(*) as cantidad,
               COALESCE(SUM(e.costo_compra), 0) as valor_total
        FROM equipos e
        JOIN categorias_equipos c ON e.categoria_id = c.id
        GROUP BY c.nombre
        ORDER BY cantidad DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.get("/equipos-antiguedad")
async def get_equipos_antiguedad():
    pool = await get_db_pool()
    
    query = """
        SELECT 
            CASE 
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, fecha_compra)) < 1 THEN 'Menos de 1 año'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, fecha_compra)) BETWEEN 1 AND 2 THEN '1-2 años'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, fecha_compra)) BETWEEN 3 AND 4 THEN '3-4 años'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, fecha_compra)) BETWEEN 5 AND 6 THEN '5-6 años'
                ELSE 'Más de 6 años'
            END as rango_antiguedad,
            COUNT(*) as cantidad
        FROM equipos
        WHERE fecha_compra IS NOT NULL
        GROUP BY rango_antiguedad
        ORDER BY 
            CASE rango_antiguedad
                WHEN 'Menos de 1 año' THEN 1
                WHEN '1-2 años' THEN 2
                WHEN '3-4 años' THEN 3
                WHEN '5-6 años' THEN 4
                ELSE 5
            END
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.get("/costos-mantenimiento")
async def get_costos_mantenimiento(year: Optional[int] = None):
    pool = await get_db_pool()
    
    if not year:
        year = datetime.now().year
    
    query = """
        SELECT 
            TO_CHAR(fecha_realizada, 'Month') as mes,
            EXTRACT(MONTH FROM fecha_realizada) as mes_num,
            tipo,
            SUM(costo) as total_costo,
            COUNT(*) as cantidad
        FROM mantenimientos
        WHERE EXTRACT(YEAR FROM fecha_realizada) = $1
        AND fecha_realizada IS NOT NULL
        GROUP BY mes, mes_num, tipo
        ORDER BY mes_num, tipo
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, year)
        return [dict(row) for row in rows]

@app.get("/mantenimientos-por-prioridad")
async def get_mantenimientos_por_prioridad():
    pool = await get_db_pool()
    
    query = """
        SELECT prioridad, COUNT(*) as cantidad
        FROM mantenimientos
        WHERE estado IN ('programado', 'en_proceso')
        GROUP BY prioridad
        ORDER BY 
            CASE prioridad
                WHEN 'urgente' THEN 1
                WHEN 'alta' THEN 2
                WHEN 'media' THEN 3
                WHEN 'baja' THEN 4
            END
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.get("/equipos-garantia")
async def get_equipos_garantia():
    pool = await get_db_pool()
    
    query = """
        SELECT 
            CASE 
                WHEN fecha_garantia_fin >= CURRENT_DATE THEN 'En garantía'
                WHEN fecha_garantia_fin < CURRENT_DATE THEN 'Fuera de garantía'
                ELSE 'Sin información'
            END as estado_garantia,
            COUNT(*) as cantidad
        FROM equipos
        GROUP BY estado_garantia
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@app.post("/export/excel")
async def export_excel(report_data: dict):
    report_type = report_data.get("type", "equipos")
    pool = await get_db_pool()
    
    try:
        if report_type == "equipos":
            query = """
                SELECT e.codigo_inventario, e.nombre, e.marca, e.modelo,
                       c.nombre as categoria, e.estado_operativo,
                       u.edificio || ' - ' || u.aula_oficina as ubicacion,
                       e.fecha_compra, e.costo_compra
                FROM equipos e
                LEFT JOIN categorias_equipos c ON e.categoria_id = c.id
                LEFT JOIN ubicaciones u ON e.ubicacion_actual_id = u.id
                ORDER BY e.codigo_inventario
            """
        elif report_type == "mantenimientos":
            query = """
                SELECT m.id, m.tipo, m.fecha_programada, m.fecha_realizada,
                       e.codigo_inventario, e.nombre as equipo,
                       m.estado, m.costo, m.descripcion
                FROM mantenimientos m
                JOIN equipos e ON m.equipo_id = e.id
                ORDER BY m.fecha_programada DESC
            """
        else:
            raise HTTPException(status_code=400, detail="Tipo de reporte no válido")
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            df = pd.DataFrame([dict(row) for row in rows])
            
            filename = f"/app/reportes/{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            os.makedirs("/app/reportes", exist_ok=True)
            df.to_excel(filename, index=False)
            
            return {"filename": filename, "message": "Excel exportado exitosamente"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.post("/export/pdf")
async def export_pdf(report_data: dict):
    report_type = report_data.get("type", "equipos")
    pool = await get_db_pool()
    
    try:
        filename = f"/app/reportes/{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("/app/reportes", exist_ok=True)
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"<b>Reporte de {report_type.capitalize()}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        date_str = Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(date_str)
        elements.append(Spacer(1, 20))
        
        if report_type == "equipos":
            query = """
                SELECT e.codigo_inventario, e.nombre, c.nombre as categoria, 
                       e.estado_operativo, u.edificio || ' - ' || u.aula_oficina as ubicacion
                FROM equipos e
                LEFT JOIN categorias_equipos c ON e.categoria_id = c.id
                LEFT JOIN ubicaciones u ON e.ubicacion_actual_id = u.id
                ORDER BY e.codigo_inventario
                LIMIT 50
            """
            headers = ['Código', 'Nombre', 'Categoría', 'Estado', 'Ubicación']
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            data = [headers]
            for row in rows:
                data.append([str(val)[:30] if val else '' for val in row])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        doc.build(elements)
        
        return {"filename": filename, "message": "PDF exportado exitosamente"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)


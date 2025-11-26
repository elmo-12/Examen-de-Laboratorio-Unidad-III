from fastapi import FastAPI, BackgroundTasks
from typing import List
import asyncpg
import os
from datetime import datetime, date, timedelta
import asyncio

app = FastAPI(title="Agent Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agents"}

async def crear_notificacion(pool, tipo: str, titulo: str, mensaje: str, 
                             equipo_id: int = None, mantenimiento_id: int = None):
    """Crea una notificación en la base de datos"""
    query = """
        INSERT INTO notificaciones (tipo, titulo, mensaje, equipo_id, mantenimiento_id)
        VALUES ($1, $2, $3, $4, $5)
    """
    async with pool.acquire() as conn:
        await conn.execute(query, tipo, titulo, mensaje, equipo_id, mantenimiento_id)

@app.post("/check-maintenance")
async def check_maintenance_reminders():
    """
    Agente: Revisa mantenimientos programados y genera alertas
    Se ejecuta diariamente
    """
    pool = await get_db_pool()
    notificaciones_generadas = 0
    
    try:
        hoy = date.today()
        fecha_limite_7dias = hoy + timedelta(days=7)
        fecha_limite_3dias = hoy + timedelta(days=3)
        
        async with pool.acquire() as conn:
            # Mantenimientos próximos (7 días)
            mantenimientos_proximos = await conn.fetch("""
                SELECT m.id, m.fecha_programada, m.descripcion,
                       e.id as equipo_id, e.nombre as equipo_nombre, e.codigo_inventario
                FROM mantenimientos m
                JOIN equipos e ON m.equipo_id = e.id
                WHERE m.fecha_programada BETWEEN $1 AND $2
                AND m.estado = 'programado'
                AND NOT EXISTS (
                    SELECT 1 FROM notificaciones n
                    WHERE n.mantenimiento_id = m.id
                    AND n.tipo = 'mantenimiento_proximo'
                    AND n.fecha_creacion >= CURRENT_DATE
                )
            """, hoy, fecha_limite_7dias)
            
            for mant in mantenimientos_proximos:
                dias_restantes = (mant['fecha_programada'] - hoy).days
                mensaje = f"El equipo {mant['equipo_nombre']} ({mant['codigo_inventario']}) tiene un mantenimiento programado en {dias_restantes} días."
                
                await crear_notificacion(
                    pool,
                    "mantenimiento_proximo",
                    f"Mantenimiento programado en {dias_restantes} días",
                    mensaje,
                    mant['equipo_id'],
                    mant['id']
                )
                notificaciones_generadas += 1
            
            # Mantenimientos urgentes (3 días o menos)
            mantenimientos_urgentes = await conn.fetch("""
                SELECT m.id, m.fecha_programada, m.descripcion,
                       e.id as equipo_id, e.nombre as equipo_nombre, e.codigo_inventario
                FROM mantenimientos m
                JOIN equipos e ON m.equipo_id = e.id
                WHERE m.fecha_programada BETWEEN $1 AND $2
                AND m.estado = 'programado'
            """, hoy, fecha_limite_3dias)
            
            for mant in mantenimientos_urgentes:
                dias_restantes = (mant['fecha_programada'] - hoy).days
                mensaje = f"⚠️ URGENTE: El equipo {mant['equipo_nombre']} ({mant['codigo_inventario']}) tiene un mantenimiento programado en {dias_restantes} días. Por favor, asegurar disponibilidad de técnicos y recursos."
                
                await crear_notificacion(
                    pool,
                    "mantenimiento_urgente",
                    f"⚠️ Mantenimiento URGENTE en {dias_restantes} días",
                    mensaje,
                    mant['equipo_id'],
                    mant['id']
                )
                notificaciones_generadas += 1
            
            # Mantenimientos vencidos
            mantenimientos_vencidos = await conn.fetch("""
                SELECT m.id, m.fecha_programada,
                       e.id as equipo_id, e.nombre as equipo_nombre, e.codigo_inventario
                FROM mantenimientos m
                JOIN equipos e ON m.equipo_id = e.id
                WHERE m.fecha_programada < $1
                AND m.estado = 'programado'
            """, hoy)
            
            for mant in mantenimientos_vencidos:
                dias_vencidos = (hoy - mant['fecha_programada']).days
                mensaje = f"🚨 El mantenimiento del equipo {mant['equipo_nombre']} ({mant['codigo_inventario']}) está vencido por {dias_vencidos} días."
                
                await crear_notificacion(
                    pool,
                    "mantenimiento_vencido",
                    f"🚨 Mantenimiento VENCIDO",
                    mensaje,
                    mant['equipo_id'],
                    mant['id']
                )
                notificaciones_generadas += 1
        
        return {
            "status": "success",
            "notificaciones_generadas": notificaciones_generadas,
            "fecha_ejecucion": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fecha_ejecucion": datetime.now().isoformat()
        }

@app.post("/check-obsolescence")
async def check_equipment_obsolescence():
    """
    Agente: Identifica equipos obsoletos o próximos a serlo
    """
    pool = await get_db_pool()
    notificaciones_generadas = 0
    
    try:
        async with pool.acquire() as conn:
            # Equipos que superan la vida útil
            equipos_obsoletos = await conn.fetch("""
                SELECT e.id, e.nombre, e.codigo_inventario, e.fecha_compra,
                       c.nombre as categoria, c.vida_util_anos,
                       EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.fecha_compra)) as anos_uso
                FROM equipos e
                JOIN categorias_equipos c ON e.categoria_id = c.id
                WHERE e.fecha_compra IS NOT NULL
                AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.fecha_compra)) >= c.vida_util_anos
                AND e.estado_operativo NOT IN ('obsoleto', 'dado_baja')
                AND NOT EXISTS (
                    SELECT 1 FROM notificaciones n
                    WHERE n.equipo_id = e.id
                    AND n.tipo = 'equipo_obsoleto'
                    AND n.fecha_creacion >= CURRENT_DATE - INTERVAL '30 days'
                )
            """)
            
            for equipo in equipos_obsoletos:
                mensaje = f"El equipo {equipo['nombre']} ({equipo['codigo_inventario']}) tiene {int(equipo['anos_uso'])} años de uso, superando la vida útil de {equipo['vida_util_anos']} años. Se recomienda evaluar su reemplazo."
                
                await crear_notificacion(
                    pool,
                    "equipo_obsoleto",
                    "Equipo ha superado su vida útil",
                    mensaje,
                    equipo['id']
                )
                notificaciones_generadas += 1
            
            # Equipos próximos a fin de vida útil (falta 1 año)
            equipos_proximos_obsolescencia = await conn.fetch("""
                SELECT e.id, e.nombre, e.codigo_inventario, e.fecha_compra,
                       c.nombre as categoria, c.vida_util_anos,
                       EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.fecha_compra)) as anos_uso
                FROM equipos e
                JOIN categorias_equipos c ON e.categoria_id = c.id
                WHERE e.fecha_compra IS NOT NULL
                AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.fecha_compra)) >= (c.vida_util_anos - 1)
                AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.fecha_compra)) < c.vida_util_anos
                AND e.estado_operativo NOT IN ('obsoleto', 'dado_baja')
            """)
            
            for equipo in equipos_proximos_obsolescencia:
                anos_restantes = equipo['vida_util_anos'] - int(equipo['anos_uso'])
                mensaje = f"El equipo {equipo['nombre']} ({equipo['codigo_inventario']}) se acerca al fin de su vida útil. Quedan aproximadamente {anos_restantes} años. Considere incluirlo en el próximo plan de renovación."
                
                await crear_notificacion(
                    pool,
                    "equipo_proximo_obsolescencia",
                    "Equipo próximo a fin de vida útil",
                    mensaje,
                    equipo['id']
                )
                notificaciones_generadas += 1
        
        return {
            "status": "success",
            "notificaciones_generadas": notificaciones_generadas,
            "fecha_ejecucion": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fecha_ejecucion": datetime.now().isoformat()
        }

@app.post("/check-warranties")
async def check_warranty_expiration():
    """
    Agente: Alerta sobre garantías próximas a vencer
    """
    pool = await get_db_pool()
    notificaciones_generadas = 0
    
    try:
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=60)
        
        async with pool.acquire() as conn:
            equipos_garantia_proxima = await conn.fetch("""
                SELECT e.id, e.nombre, e.codigo_inventario, e.fecha_garantia_fin,
                       p.razon_social as proveedor
                FROM equipos e
                LEFT JOIN proveedores p ON e.proveedor_id = p.id
                WHERE e.fecha_garantia_fin BETWEEN $1 AND $2
                AND NOT EXISTS (
                    SELECT 1 FROM notificaciones n
                    WHERE n.equipo_id = e.id
                    AND n.tipo = 'garantia_proxima_vencer'
                    AND n.fecha_creacion >= CURRENT_DATE - INTERVAL '30 days'
                )
            """, hoy, fecha_limite)
            
            for equipo in equipos_garantia_proxima:
                dias_restantes = (equipo['fecha_garantia_fin'] - hoy).days
                mensaje = f"La garantía del equipo {equipo['nombre']} ({equipo['codigo_inventario']}) vence en {dias_restantes} días ({equipo['fecha_garantia_fin'].strftime('%d/%m/%Y')}). Proveedor: {equipo['proveedor'] or 'N/A'}"
                
                await crear_notificacion(
                    pool,
                    "garantia_proxima_vencer",
                    f"Garantía vence en {dias_restantes} días",
                    mensaje,
                    equipo['id']
                )
                notificaciones_generadas += 1
        
        return {
            "status": "success",
            "notificaciones_generadas": notificaciones_generadas,
            "fecha_ejecucion": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fecha_ejecucion": datetime.now().isoformat()
        }

@app.post("/analyze-maintenance-costs")
async def analyze_maintenance_costs():
    """
    Agente: Analiza costos de mantenimiento y genera alertas
    """
    pool = await get_db_pool()
    alertas = []
    
    try:
        async with pool.acquire() as conn:
            # Equipos con alto costo de mantenimiento
            equipos_alto_costo = await conn.fetch("""
                SELECT e.id, e.nombre, e.codigo_inventario, e.costo_compra,
                       COUNT(m.id) as num_mantenimientos,
                       SUM(m.costo) as costo_total_mantenimiento
                FROM equipos e
                JOIN mantenimientos m ON e.id = m.equipo_id
                WHERE m.fecha_realizada >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY e.id
                HAVING SUM(m.costo) > e.costo_compra * 0.5
                ORDER BY costo_total_mantenimiento DESC
            """)
            
            for equipo in equipos_alto_costo:
                porcentaje = (equipo['costo_total_mantenimiento'] / equipo['costo_compra'] * 100) if equipo['costo_compra'] else 0
                
                mensaje = f"El equipo {equipo['nombre']} ({equipo['codigo_inventario']}) ha generado costos de mantenimiento por ${equipo['costo_total_mantenimiento']:.2f} en el último año ({int(porcentaje)}% de su valor de compra). Se recomienda evaluar su reemplazo."
                
                await crear_notificacion(
                    pool,
                    "alto_costo_mantenimiento",
                    "Equipo con altos costos de mantenimiento",
                    mensaje,
                    equipo['id']
                )
                
                alertas.append({
                    "equipo_id": equipo['id'],
                    "codigo": equipo['codigo_inventario'],
                    "costo_mantenimiento": float(equipo['costo_total_mantenimiento']),
                    "num_mantenimientos": equipo['num_mantenimientos']
                })
        
        return {
            "status": "success",
            "equipos_identificados": len(alertas),
            "detalle": alertas,
            "fecha_ejecucion": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fecha_ejecucion": datetime.now().isoformat()
        }

@app.get("/notificaciones")
async def get_notificaciones(leida: bool = False, limit: int = 50):
    """Obtiene las notificaciones del sistema"""
    pool = await get_db_pool()
    
    query = """
        SELECT n.*, e.codigo_inventario, e.nombre as equipo_nombre
        FROM notificaciones n
        LEFT JOIN equipos e ON n.equipo_id = e.id
        WHERE n.leida = $1
        ORDER BY n.fecha_creacion DESC
        LIMIT $2
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, leida, limit)
        return [dict(row) for row in rows]

@app.put("/notificaciones/{notif_id}/marcar-leida")
async def marcar_notificacion_leida(notif_id: int):
    """Marca una notificación como leída"""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE notificaciones SET leida = TRUE, fecha_lectura = CURRENT_TIMESTAMP WHERE id = $1",
            notif_id
        )
    
    return {"message": "Notificación marcada como leída"}

@app.post("/run-all-agents")
async def run_all_agents(background_tasks: BackgroundTasks):
    """Ejecuta todos los agentes en segundo plano"""
    
    async def ejecutar_todos():
        await check_maintenance_reminders()
        await check_equipment_obsolescence()
        await check_warranty_expiration()
        await analyze_maintenance_costs()
    
    background_tasks.add_task(ejecutar_todos)
    
    return {
        "message": "Todos los agentes han sido programados para ejecución",
        "fecha": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


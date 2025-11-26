from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncpg
import os
from datetime import datetime, date
import json

app = FastAPI(title="Mantenimiento Service", version="1.0.0")

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

class MantenimientoCreate(BaseModel):
    equipo_id: int
    tipo: str  # 'preventivo' o 'correctivo'
    fecha_programada: date
    tecnico_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    descripcion: str
    problema_reportado: Optional[str] = None
    prioridad: str = "media"  # 'urgente', 'alta', 'media', 'baja'
    observaciones: Optional[str] = None

class MantenimientoUpdate(BaseModel):
    fecha_programada: Optional[date] = None
    fecha_realizada: Optional[date] = None
    tecnico_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    descripcion: Optional[str] = None
    problema_reportado: Optional[str] = None
    solucion_aplicada: Optional[str] = None
    costo: Optional[float] = None
    tiempo_fuera_servicio_horas: Optional[float] = None
    estado: Optional[str] = None  # 'programado', 'en_proceso', 'completado', 'cancelado'
    prioridad: Optional[str] = None
    partes_reemplazadas: Optional[dict] = None
    observaciones: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mantenimientos"}

@app.get("/mantenimientos")
async def get_mantenimientos(
    equipo_id: Optional[int] = None,
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None
):
    """Obtiene lista de mantenimientos con filtros opcionales"""
    pool = await get_db_pool()
    
    query = """
        SELECT m.*, 
               e.codigo_inventario, e.nombre as equipo_nombre,
               u.nombre_completo as tecnico_nombre,
               p.razon_social as proveedor_nombre
        FROM mantenimientos m
        JOIN equipos e ON m.equipo_id = e.id
        LEFT JOIN usuarios u ON m.tecnico_id = u.id
        LEFT JOIN proveedores p ON m.proveedor_id = p.id
        WHERE 1=1
    """
    params = []
    param_count = 1
    
    if equipo_id:
        query += f" AND m.equipo_id = ${param_count}"
        params.append(equipo_id)
        param_count += 1
    
    if estado:
        query += f" AND m.estado = ${param_count}"
        params.append(estado)
        param_count += 1
    
    if tipo:
        query += f" AND m.tipo = ${param_count}"
        params.append(tipo)
        param_count += 1
    
    if fecha_desde:
        query += f" AND m.fecha_programada >= ${param_count}"
        params.append(fecha_desde)
        param_count += 1
    
    if fecha_hasta:
        query += f" AND m.fecha_programada <= ${param_count}"
        params.append(fecha_hasta)
        param_count += 1
    
    query += " ORDER BY m.fecha_programada DESC"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        mantenimientos = []
        for row in rows:
            mant = dict(row)
            if mant.get('partes_reemplazadas'):
                mant['partes_reemplazadas'] = json.loads(mant['partes_reemplazadas'])
            mantenimientos.append(mant)
        return mantenimientos

@app.get("/mantenimientos/{mantenimiento_id}")
async def get_mantenimiento(mantenimiento_id: int):
    """Obtiene un mantenimiento específico"""
    pool = await get_db_pool()
    
    query = """
        SELECT m.*, 
               e.codigo_inventario, e.nombre as equipo_nombre,
               u.nombre_completo as tecnico_nombre,
               p.razon_social as proveedor_nombre
        FROM mantenimientos m
        JOIN equipos e ON m.equipo_id = e.id
        LEFT JOIN usuarios u ON m.tecnico_id = u.id
        LEFT JOIN proveedores p ON m.proveedor_id = p.id
        WHERE m.id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, mantenimiento_id)
        if not row:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
        
        mantenimiento = dict(row)
        if mantenimiento.get('partes_reemplazadas'):
            mantenimiento['partes_reemplazadas'] = json.loads(mantenimiento['partes_reemplazadas'])
        
        return mantenimiento

@app.post("/mantenimientos")
async def create_mantenimiento(mantenimiento: MantenimientoCreate):
    """Crea un nuevo mantenimiento"""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO mantenimientos (
            equipo_id, tipo, fecha_programada, tecnico_id, proveedor_id,
            descripcion, problema_reportado, estado, prioridad, observaciones
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
    """
    
    estado = "programado"
    
    # Si es correctivo, cambiar estado del equipo a en_reparacion
    if mantenimiento.tipo == "correctivo":
        estado_equipo = "en_reparacion"
    else:
        estado_equipo = None
    
    async with pool.acquire() as conn:
        try:
            # Validar que el equipo existe
            equipo = await conn.fetchval("SELECT id FROM equipos WHERE id = $1", mantenimiento.equipo_id)
            if not equipo:
                raise HTTPException(status_code=400, detail=f"El equipo con ID {mantenimiento.equipo_id} no existe")
            
            # Validar técnico si se proporciona
            if mantenimiento.tecnico_id:
                tecnico = await conn.fetchval("SELECT id FROM usuarios WHERE id = $1 AND rol = 'tecnico'", mantenimiento.tecnico_id)
                if not tecnico:
                    raise HTTPException(status_code=400, detail=f"El técnico con ID {mantenimiento.tecnico_id} no existe")
            
            # Validar proveedor si se proporciona
            if mantenimiento.proveedor_id:
                proveedor = await conn.fetchval("SELECT id FROM proveedores WHERE id = $1", mantenimiento.proveedor_id)
                if not proveedor:
                    raise HTTPException(status_code=400, detail=f"El proveedor con ID {mantenimiento.proveedor_id} no existe")
            
            mantenimiento_id = await conn.fetchval(
                query,
                mantenimiento.equipo_id,
                mantenimiento.tipo,
                mantenimiento.fecha_programada,
                mantenimiento.tecnico_id,
                mantenimiento.proveedor_id,
                mantenimiento.descripcion,
                mantenimiento.problema_reportado,
                estado,
                mantenimiento.prioridad,
                mantenimiento.observaciones
            )
            
            # Actualizar estado del equipo si es mantenimiento correctivo
            if estado_equipo:
                await conn.execute(
                    "UPDATE equipos SET estado_operativo = $1 WHERE id = $2",
                    estado_equipo,
                    mantenimiento.equipo_id
                )
            
            return {"id": mantenimiento_id, "message": "Mantenimiento creado exitosamente"}
        except HTTPException:
            raise
        except asyncpg.ForeignKeyViolationError as e:
            error_msg = str(e)
            if "equipo_id" in error_msg.lower():
                raise HTTPException(status_code=400, detail=f"El equipo no existe")
            elif "tecnico_id" in error_msg.lower():
                raise HTTPException(status_code=400, detail=f"El técnico no existe")
            elif "proveedor_id" in error_msg.lower():
                raise HTTPException(status_code=400, detail=f"El proveedor no existe")
            else:
                raise HTTPException(status_code=400, detail=f"Error de referencia: {error_msg}")
        except Exception as e:
            import traceback
            error_detail = str(e)
            print(f"Error al crear mantenimiento: {error_detail}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error al crear mantenimiento: {error_detail}")

@app.put("/mantenimientos/{mantenimiento_id}")
async def update_mantenimiento(mantenimiento_id: int, mantenimiento: MantenimientoUpdate):
    """Actualiza un mantenimiento existente"""
    pool = await get_db_pool()
    
    updates = []
    params = []
    param_count = 1
    
    if mantenimiento.fecha_programada is not None:
        updates.append(f"fecha_programada = ${param_count}")
        params.append(mantenimiento.fecha_programada)
        param_count += 1
    
    if mantenimiento.fecha_realizada is not None:
        updates.append(f"fecha_realizada = ${param_count}")
        params.append(mantenimiento.fecha_realizada)
        param_count += 1
    
    if mantenimiento.tecnico_id is not None:
        updates.append(f"tecnico_id = ${param_count}")
        params.append(mantenimiento.tecnico_id)
        param_count += 1
    
    if mantenimiento.proveedor_id is not None:
        updates.append(f"proveedor_id = ${param_count}")
        params.append(mantenimiento.proveedor_id)
        param_count += 1
    
    if mantenimiento.descripcion is not None:
        updates.append(f"descripcion = ${param_count}")
        params.append(mantenimiento.descripcion)
        param_count += 1
    
    if mantenimiento.problema_reportado is not None:
        updates.append(f"problema_reportado = ${param_count}")
        params.append(mantenimiento.problema_reportado)
        param_count += 1
    
    if mantenimiento.solucion_aplicada is not None:
        updates.append(f"solucion_aplicada = ${param_count}")
        params.append(mantenimiento.solucion_aplicada)
        param_count += 1
    
    if mantenimiento.costo is not None:
        updates.append(f"costo = ${param_count}")
        params.append(mantenimiento.costo)
        param_count += 1
    
    if mantenimiento.tiempo_fuera_servicio_horas is not None:
        updates.append(f"tiempo_fuera_servicio_horas = ${param_count}")
        params.append(mantenimiento.tiempo_fuera_servicio_horas)
        param_count += 1
    
    if mantenimiento.estado is not None:
        updates.append(f"estado = ${param_count}")
        params.append(mantenimiento.estado)
        param_count += 1
    
    if mantenimiento.prioridad is not None:
        updates.append(f"prioridad = ${param_count}")
        params.append(mantenimiento.prioridad)
        param_count += 1
    
    if mantenimiento.partes_reemplazadas is not None:
        updates.append(f"partes_reemplazadas = ${param_count}")
        params.append(json.dumps(mantenimiento.partes_reemplazadas))
        param_count += 1
    
    if mantenimiento.observaciones is not None:
        updates.append(f"observaciones = ${param_count}")
        params.append(mantenimiento.observaciones)
        param_count += 1
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    params.append(mantenimiento_id)
    query = f"UPDATE mantenimientos SET {', '.join(updates)} WHERE id = ${param_count}"
    
    async with pool.acquire() as conn:
        # Obtener información del mantenimiento antes de actualizar
        mant_actual = await conn.fetchrow("SELECT equipo_id, estado, tipo FROM mantenimientos WHERE id = $1", mantenimiento_id)
        if not mant_actual:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
        
        result = await conn.execute(query, *params)
        
        # Si el mantenimiento se completó, restaurar estado del equipo
        if mantenimiento.estado == "completado" and mant_actual['tipo'] == "correctivo":
            await conn.execute(
                "UPDATE equipos SET estado_operativo = 'operativo' WHERE id = $1",
                mant_actual['equipo_id']
            )
        
        return {"message": "Mantenimiento actualizado exitosamente"}

@app.delete("/mantenimientos/{mantenimiento_id}")
async def delete_mantenimiento(mantenimiento_id: int):
    """Elimina un mantenimiento"""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM mantenimientos WHERE id = $1", mantenimiento_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
        
        return {"message": "Mantenimiento eliminado exitosamente"}

@app.get("/mantenimientos/calendario")
async def get_calendario_mantenimientos(
    mes: Optional[int] = None,
    año: Optional[int] = None
):
    """Obtiene mantenimientos programados para un mes específico"""
    pool = await get_db_pool()
    
    if not mes:
        mes = datetime.now().month
    if not año:
        año = datetime.now().year
    
    query = """
        SELECT m.id, m.fecha_programada, m.tipo, m.estado, m.prioridad,
               e.codigo_inventario, e.nombre as equipo_nombre,
               u.nombre_completo as tecnico_nombre
        FROM mantenimientos m
        JOIN equipos e ON m.equipo_id = e.id
        LEFT JOIN usuarios u ON m.tecnico_id = u.id
        WHERE EXTRACT(MONTH FROM m.fecha_programada) = $1
        AND EXTRACT(YEAR FROM m.fecha_programada) = $2
        ORDER BY m.fecha_programada, m.prioridad DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, mes, año)
        return [dict(row) for row in rows]

@app.get("/mantenimientos/estadisticas")
async def get_estadisticas_mantenimientos():
    """Obtiene estadísticas de mantenimientos"""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        stats = {}
        
        # Total de mantenimientos
        stats['total'] = await conn.fetchval("SELECT COUNT(*) FROM mantenimientos")
        
        # Por tipo
        stats['por_tipo'] = await conn.fetch("""
            SELECT tipo, COUNT(*) as cantidad
            FROM mantenimientos
            GROUP BY tipo
        """)
        
        # Por estado
        stats['por_estado'] = await conn.fetch("""
            SELECT estado, COUNT(*) as cantidad
            FROM mantenimientos
            GROUP BY estado
        """)
        
        # Costo total
        stats['costo_total'] = await conn.fetchval("SELECT COALESCE(SUM(costo), 0) FROM mantenimientos WHERE costo IS NOT NULL")
        
        # Costo por mes (últimos 6 meses)
        stats['costo_por_mes'] = await conn.fetch("""
            SELECT 
                TO_CHAR(fecha_realizada, 'YYYY-MM') as mes,
                SUM(costo) as total_costo,
                COUNT(*) as cantidad
            FROM mantenimientos
            WHERE fecha_realizada >= CURRENT_DATE - INTERVAL '6 months'
            AND costo IS NOT NULL
            GROUP BY mes
            ORDER BY mes DESC
        """)
        
        return {
            "total": stats['total'],
            "por_tipo": [dict(row) for row in stats['por_tipo']],
            "por_estado": [dict(row) for row in stats['por_estado']],
            "costo_total": float(stats['costo_total']),
            "costo_por_mes": [dict(row) for row in stats['costo_por_mes']]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)


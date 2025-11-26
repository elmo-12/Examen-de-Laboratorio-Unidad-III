from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import os
from datetime import datetime, date
import json

app = FastAPI(title="Equipos Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

class EquipoCreate(BaseModel):
    codigo_inventario: str
    categoria_id: int
    nombre: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    especificaciones: Optional[dict] = None
    proveedor_id: Optional[int] = None
    fecha_compra: Optional[date] = None
    costo_compra: Optional[float] = None
    fecha_garantia_fin: Optional[date] = None
    ubicacion_actual_id: Optional[int] = None
    estado_operativo: str = "operativo"
    estado_fisico: str = "bueno"
    asignado_a_id: Optional[int] = None
    notas: Optional[str] = None
    imagen_url: Optional[str] = None

class EquipoUpdate(BaseModel):
    nombre: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    especificaciones: Optional[dict] = None
    ubicacion_actual_id: Optional[int] = None
    estado_operativo: Optional[str] = None
    estado_fisico: Optional[str] = None
    asignado_a_id: Optional[int] = None
    notas: Optional[str] = None

class MovimientoCreate(BaseModel):
    equipo_id: int
    ubicacion_destino_id: int
    usuario_responsable_id: int
    motivo: str
    observaciones: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "equipos"}

@app.get("/equipos")
async def get_equipos(
    categoria: Optional[str] = None,
    estado: Optional[str] = None,
    ubicacion: Optional[int] = None
):
    pool = await get_db_pool()
    
    query = """
        SELECT e.*, c.nombre as categoria_nombre, 
               u.edificio || ' - ' || u.aula_oficina as ubicacion_nombre,
               p.razon_social as proveedor_nombre
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.categoria_id = c.id
        LEFT JOIN ubicaciones u ON e.ubicacion_actual_id = u.id
        LEFT JOIN proveedores p ON e.proveedor_id = p.id
        WHERE 1=1
    """
    params = []
    param_count = 1
    
    if categoria:
        query += f" AND c.nombre = ${param_count}"
        params.append(categoria)
        param_count += 1
    
    if estado:
        query += f" AND e.estado_operativo = ${param_count}"
        params.append(estado)
        param_count += 1
    
    if ubicacion:
        query += f" AND e.ubicacion_actual_id = ${param_count}"
        params.append(ubicacion)
        param_count += 1
    
    query += " ORDER BY e.fecha_registro DESC"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        equipos = []
        for row in rows:
            equipo = dict(row)
            if equipo.get('especificaciones'):
                equipo['especificaciones'] = json.loads(equipo['especificaciones'])
            equipos.append(equipo)
        return equipos

@app.get("/equipos/{equipo_id}")
async def get_equipo(equipo_id: int):
    pool = await get_db_pool()
    
    query = """
        SELECT e.*, c.nombre as categoria_nombre,
               u.edificio || ' - ' || u.aula_oficina as ubicacion_nombre,
               p.razon_social as proveedor_nombre,
               usr.nombre_completo as asignado_a_nombre
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.categoria_id = c.id
        LEFT JOIN ubicaciones u ON e.ubicacion_actual_id = u.id
        LEFT JOIN proveedores p ON e.proveedor_id = p.id
        LEFT JOIN usuarios usr ON e.asignado_a_id = usr.id
        WHERE e.id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, equipo_id)
        if not row:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        equipo = dict(row)
        if equipo.get('especificaciones'):
            equipo['especificaciones'] = json.loads(equipo['especificaciones'])
        
        movimientos_query = """
            SELECT m.*, 
                   uo.edificio || ' - ' || uo.aula_oficina as origen,
                   ud.edificio || ' - ' || ud.aula_oficina as destino,
                   u.nombre_completo as responsable
            FROM movimientos_equipos m
            LEFT JOIN ubicaciones uo ON m.ubicacion_origen_id = uo.id
            LEFT JOIN ubicaciones ud ON m.ubicacion_destino_id = ud.id
            LEFT JOIN usuarios u ON m.usuario_responsable_id = u.id
            WHERE m.equipo_id = $1
            ORDER BY m.fecha_movimiento DESC
        """
        movimientos = await conn.fetch(movimientos_query, equipo_id)
        equipo['historial_movimientos'] = [dict(m) for m in movimientos]
        
        return equipo

@app.post("/equipos")
async def create_equipo(equipo: EquipoCreate):
    pool = await get_db_pool()
    
    query = """
        INSERT INTO equipos (
            codigo_inventario, categoria_id, nombre, marca, modelo, numero_serie,
            especificaciones, proveedor_id, fecha_compra, costo_compra,
            fecha_garantia_fin, ubicacion_actual_id, estado_operativo, estado_fisico,
            asignado_a_id, notas, imagen_url
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
        RETURNING id
    """
    
    especificaciones_json = json.dumps(equipo.especificaciones) if equipo.especificaciones else None
    
    async with pool.acquire() as conn:
        equipo_id = await conn.fetchval(
            query,
            equipo.codigo_inventario,
            equipo.categoria_id,
            equipo.nombre,
            equipo.marca,
            equipo.modelo,
            equipo.numero_serie,
            especificaciones_json,
            equipo.proveedor_id,
            equipo.fecha_compra,
            equipo.costo_compra,
            equipo.fecha_garantia_fin,
            equipo.ubicacion_actual_id,
            equipo.estado_operativo,
            equipo.estado_fisico,
            equipo.asignado_a_id,
            equipo.notas,
            equipo.imagen_url
        )
        
        return {"id": equipo_id, "message": "Equipo creado exitosamente"}

@app.put("/equipos/{equipo_id}")
async def update_equipo(equipo_id: int, equipo: EquipoUpdate):
    pool = await get_db_pool()
    
    updates = []
    params = []
    param_count = 1
    
    if equipo.nombre is not None:
        updates.append(f"nombre = ${param_count}")
        params.append(equipo.nombre)
        param_count += 1
    
    if equipo.marca is not None:
        updates.append(f"marca = ${param_count}")
        params.append(equipo.marca)
        param_count += 1
    
    if equipo.modelo is not None:
        updates.append(f"modelo = ${param_count}")
        params.append(equipo.modelo)
        param_count += 1
    
    if equipo.especificaciones is not None:
        updates.append(f"especificaciones = ${param_count}")
        params.append(json.dumps(equipo.especificaciones))
        param_count += 1
    
    if equipo.ubicacion_actual_id is not None:
        updates.append(f"ubicacion_actual_id = ${param_count}")
        params.append(equipo.ubicacion_actual_id)
        param_count += 1
    
    if equipo.estado_operativo is not None:
        updates.append(f"estado_operativo = ${param_count}")
        params.append(equipo.estado_operativo)
        param_count += 1
    
    if equipo.estado_fisico is not None:
        updates.append(f"estado_fisico = ${param_count}")
        params.append(equipo.estado_fisico)
        param_count += 1
    
    if equipo.asignado_a_id is not None:
        updates.append(f"asignado_a_id = ${param_count}")
        params.append(equipo.asignado_a_id)
        param_count += 1
    
    if equipo.notas is not None:
        updates.append(f"notas = ${param_count}")
        params.append(equipo.notas)
        param_count += 1
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    params.append(equipo_id)
    query = f"UPDATE equipos SET {', '.join(updates)} WHERE id = ${param_count}"
    
    async with pool.acquire() as conn:
        result = await conn.execute(query, *params)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        return {"message": "Equipo actualizado exitosamente"}

@app.delete("/equipos/{equipo_id}")
async def delete_equipo(equipo_id: int):
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM equipos WHERE id = $1", equipo_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        return {"message": "Equipo eliminado exitosamente"}

@app.post("/movimientos")
async def create_movimiento(movimiento: MovimientoCreate):
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        ubicacion_origen = await conn.fetchval(
            "SELECT ubicacion_actual_id FROM equipos WHERE id = $1",
            movimiento.equipo_id
        )
        
        await conn.execute(
            """
            INSERT INTO movimientos_equipos 
            (equipo_id, ubicacion_origen_id, ubicacion_destino_id, usuario_responsable_id, motivo, observaciones)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            movimiento.equipo_id,
            ubicacion_origen,
            movimiento.ubicacion_destino_id,
            movimiento.usuario_responsable_id,
            movimiento.motivo,
            movimiento.observaciones
        )
        
        await conn.execute(
            "UPDATE equipos SET ubicacion_actual_id = $1 WHERE id = $2",
            movimiento.ubicacion_destino_id,
            movimiento.equipo_id
        )
        
        return {"message": "Movimiento registrado exitosamente"}

@app.get("/categorias")
async def get_categorias():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM categorias_equipos ORDER BY nombre")
        return [dict(row) for row in rows]

@app.get("/ubicaciones")
async def get_ubicaciones():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT *, edificio || ' - ' || aula_oficina as nombre_completo 
            FROM ubicaciones 
            WHERE activo = TRUE 
            ORDER BY edificio, aula_oficina
            """
        )
        return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
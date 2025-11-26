"""
Configuración centralizada de base de datos para todos los microservicios
"""
import asyncpg
import os
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@postgres:5432/ti_management")

# Pool de conexiones global
_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """
    Obtiene o crea el pool de conexiones a la base de datos
    """
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

async def close_db_pool():
    """
    Cierra el pool de conexiones
    """
    global _pool
    
    if _pool is not None:
        await _pool.close()
        _pool = None


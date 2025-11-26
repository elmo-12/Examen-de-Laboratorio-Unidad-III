#!/usr/bin/env python3
"""
Script para inicializar la base de datos
Ejecuta el esquema SQL y carga datos iniciales
"""

import asyncpg
import os
import sys
from pathlib import Path

# Obtener DATABASE_URL de las variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/ti_management"
)

async def init_database():
    """Inicializa la base de datos ejecutando el esquema SQL"""
    
    # Leer el archivo schema.sql
    schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Error: No se encontró el archivo schema.sql en {schema_path}")
        sys.exit(1)
    
    print(f"📖 Leyendo esquema desde: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    try:
        # Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Ejecutar el esquema SQL
        print("⚙️  Ejecutando esquema SQL...")
        await conn.execute(schema_sql)
        
        print("✅ Base de datos inicializada correctamente")
        
        # Verificar tablas creadas
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_database())


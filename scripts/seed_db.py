#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo (seeders)
Ejecuta después de init_db.py
"""

import asyncpg
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random
import json

# Obtener DATABASE_URL de las variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/ti_management"
)

# Datos de ejemplo
USUARIOS = [
    {
        "username": "admin",
        "email": "admin@universidad.edu",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ",
        "rol": "admin",
        "nombre_completo": "Administrador del Sistema"
    },
    {
        "username": "jperez",
        "email": "jperez@universidad.edu",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ",
        "rol": "tecnico",
        "nombre_completo": "Juan Pérez - Técnico de TI"
    },
    {
        "username": "mgarcia",
        "email": "mgarcia@universidad.edu",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ",
        "rol": "tecnico",
        "nombre_completo": "María García - Técnico de Mantenimiento"
    },
    {
        "username": "crodriguez",
        "email": "crodriguez@universidad.edu",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ",
        "rol": "usuario",
        "nombre_completo": "Carlos Rodríguez - Docente"
    },
    {
        "username": "alopez",
        "email": "alopez@universidad.edu",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ",
        "rol": "usuario",
        "nombre_completo": "Ana López - Secretaria"
    }
]

PROVEEDORES = [
    {
        "razon_social": "Tecnología Avanzada S.A.",
        "ruc": "20123456789",
        "direccion": "Av. Principal 123, Lima",
        "telefono": "+51 1 234-5678",
        "email": "ventas@tecavanzada.com",
        "contacto_nombre": "Roberto Silva",
        "contacto_telefono": "+51 999 888 777",
        "sitio_web": "https://www.tecavanzada.com",
        "calificacion": 4.5,
        "notas": "Proveedor confiable con buen servicio post-venta"
    },
    {
        "razon_social": "Equipos Informáticos del Perú S.A.C.",
        "ruc": "20234567890",
        "direccion": "Jr. Comercio 456, Lima",
        "telefono": "+51 1 345-6789",
        "email": "contacto@equiposinfo.pe",
        "contacto_nombre": "Patricia Mendoza",
        "contacto_telefono": "+51 999 777 666",
        "sitio_web": "https://www.equiposinfo.pe",
        "calificacion": 4.2,
        "notas": "Buenos precios, entrega rápida"
    },
    {
        "razon_social": "Servicios de Mantenimiento TI S.A.",
        "ruc": "20345678901",
        "direccion": "Av. Industrial 789, Lima",
        "telefono": "+51 1 456-7890",
        "email": "servicios@mantenimientoti.com",
        "contacto_nombre": "Luis Fernández",
        "contacto_telefono": "+51 999 666 555",
        "sitio_web": "https://www.mantenimientoti.com",
        "calificacion": 4.8,
        "notas": "Especialistas en mantenimiento preventivo y correctivo"
    },
    {
        "razon_social": "Distribuidora de Hardware S.A.",
        "ruc": "20456789012",
        "direccion": "Calle Los Olivos 321, Lima",
        "telefono": "+51 1 567-8901",
        "email": "info@hardwareperu.com",
        "contacto_nombre": "Carmen Torres",
        "contacto_telefono": "+51 999 555 444",
        "sitio_web": "https://www.hardwareperu.com",
        "calificacion": 3.9,
        "notas": "Amplio catálogo de productos"
    }
]

UBICACIONES = [
    {"edificio": "Edificio Principal", "piso": "1", "aula_oficina": "Aula 101", "descripcion": "Aula de informática - Laboratorio 1"},
    {"edificio": "Edificio Principal", "piso": "1", "aula_oficina": "Aula 102", "descripcion": "Aula de informática - Laboratorio 2"},
    {"edificio": "Edificio Principal", "piso": "1", "aula_oficina": "Aula 103", "descripcion": "Aula de informática - Laboratorio 3"},
    {"edificio": "Edificio Principal", "piso": "2", "aula_oficina": "Oficina 201", "descripcion": "Oficina administrativa - Dirección"},
    {"edificio": "Edificio Principal", "piso": "2", "aula_oficina": "Oficina 202", "descripcion": "Oficina administrativa - Secretaría"},
    {"edificio": "Edificio Principal", "piso": "2", "aula_oficina": "Oficina 203", "descripcion": "Oficina administrativa - Contabilidad"},
    {"edificio": "Edificio Principal", "piso": "3", "aula_oficina": "Aula 301", "descripcion": "Aula de clases - Ingeniería"},
    {"edificio": "Edificio Principal", "piso": "3", "aula_oficina": "Aula 302", "descripcion": "Aula de clases - Ciencias"},
    {"edificio": "Edificio Anexo", "piso": "1", "aula_oficina": "Laboratorio 1", "descripcion": "Laboratorio de computación - Redes"},
    {"edificio": "Edificio Anexo", "piso": "1", "aula_oficina": "Laboratorio 2", "descripcion": "Laboratorio de computación - Programación"},
    {"edificio": "Edificio Anexo", "piso": "2", "aula_oficina": "Sala de Servidores", "descripcion": "Centro de datos y servidores"},
    {"edificio": "Edificio Anexo", "piso": "2", "aula_oficina": "Almacén TI", "descripcion": "Almacén de equipos y repuestos"}
]

MARCAS_EQUIPOS = {
    "Laptop": ["Dell", "HP", "Lenovo", "ASUS", "Acer"],
    "Desktop": ["Dell", "HP", "Lenovo", "ASUS"],
    "Monitor": ["Dell", "HP", "LG", "Samsung", "Acer"],
    "Impresora": ["HP", "Canon", "Epson", "Brother"],
    "Servidor": ["Dell", "HP", "IBM", "Cisco"],
    "Tablet": ["Apple", "Samsung", "Lenovo"],
    "Proyector": ["Epson", "BenQ", "Optoma", "ViewSonic"],
    "Router": ["Cisco", "TP-Link", "D-Link", "Netgear"],
    "Switch": ["Cisco", "TP-Link", "D-Link", "Netgear"]
}

MODELOS_EQUIPOS = {
    "Laptop": ["Latitude 5520", "EliteBook 840", "ThinkPad X1", "VivoBook 15", "Aspire 5"],
    "Desktop": ["OptiPlex 7090", "EliteDesk 800", "ThinkCentre M90", "VivoMini"],
    "Monitor": ["UltraSharp U2720", "EliteDisplay E243", "UltraWide 34", "Curved 27", "ProArt PA248"],
    "Impresora": ["LaserJet Pro", "PIXMA G", "WorkForce Pro", "MFC-L3750"],
    "Servidor": ["PowerEdge R740", "ProLiant DL380", "System x3650", "UCS C220"],
    "Tablet": ["iPad Pro", "Galaxy Tab S7", "Tab P11"],
    "Proyector": ["PowerLite X41+", "MW560", "HD146X", "PJD7820HD"],
    "Router": ["ISR 4331", "Archer AX50", "DIR-842", "Nighthawk AX8"],
    "Switch": ["Catalyst 2960", "TL-SG108", "DGS-1008G", "GS308"]
]

async def seed_database():
    """Pobla la base de datos con datos de ejemplo"""
    
    try:
        print("🔌 Conectando a la base de datos...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Verificar si ya hay datos
        count_equipos = await conn.fetchval("SELECT COUNT(*) FROM equipos")
        if count_equipos > 0:
            print(f"⚠️  Ya existen {count_equipos} equipos en la base de datos.")
            respuesta = input("¿Desea continuar y agregar más datos? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                await conn.close()
                return
        
        print("\n🌱 Iniciando seeders...\n")
        
        # 1. USUARIOS
        print("👥 Insertando usuarios...")
        usuario_ids = {}
        for usuario in USUARIOS:
            try:
                user_id = await conn.fetchval("""
                    INSERT INTO usuarios (username, email, password_hash, rol, nombre_completo, activo)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (username) DO UPDATE SET nombre_completo = EXCLUDED.nombre_completo
                    RETURNING id
                """, usuario["username"], usuario["email"], usuario["password_hash"], 
                    usuario["rol"], usuario["nombre_completo"], True)
                usuario_ids[usuario["username"]] = user_id
                print(f"   ✅ {usuario['nombre_completo']}")
            except Exception as e:
                print(f"   ⚠️  Error al insertar {usuario['username']}: {e}")
        
        # 2. UBICACIONES
        print("\n📍 Insertando ubicaciones...")
        ubicacion_ids = []
        responsable_ids = list(usuario_ids.values())
        for i, ubicacion in enumerate(UBICACIONES):
            try:
                responsable_id = responsable_ids[i % len(responsable_ids)] if responsable_ids else None
                ubic_id = await conn.fetchval("""
                    INSERT INTO ubicaciones (edificio, piso, aula_oficina, descripcion, responsable_id, activo)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, ubicacion["edificio"], ubicacion["piso"], ubicacion["aula_oficina"],
                    ubicacion["descripcion"], responsable_id, True)
                ubicacion_ids.append(ubic_id)
                print(f"   ✅ {ubicacion['edificio']} - {ubicacion['aula_oficina']}")
            except Exception as e:
                print(f"   ⚠️  Error al insertar ubicación: {e}")
        
        # 3. PROVEEDORES
        print("\n🏢 Insertando proveedores...")
        proveedor_ids = []
        for proveedor in PROVEEDORES:
            try:
                prov_id = await conn.fetchval("""
                    INSERT INTO proveedores (razon_social, ruc, direccion, telefono, email, 
                                           contacto_nombre, contacto_telefono, sitio_web, calificacion, activo, notas)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (ruc) DO UPDATE SET razon_social = EXCLUDED.razon_social
                    RETURNING id
                """, proveedor["razon_social"], proveedor["ruc"], proveedor["direccion"],
                    proveedor["telefono"], proveedor["email"], proveedor["contacto_nombre"],
                    proveedor["contacto_telefono"], proveedor["sitio_web"], 
                    Decimal(str(proveedor["calificacion"])), True, proveedor["notas"])
                proveedor_ids.append(prov_id)
                print(f"   ✅ {proveedor['razon_social']}")
            except Exception as e:
                print(f"   ⚠️  Error al insertar proveedor: {e}")
        
        # 4. CONTRATOS
        print("\n📄 Insertando contratos...")
        contrato_ids = []
        tipos_contrato = ["compra_equipos", "mantenimiento", "servicio_tecnico", "suministro"]
        estados_contrato = ["vigente", "vigente", "vigente", "vencido", "finalizado"]
        
        for i, proveedor_id in enumerate(proveedor_ids):
            # 2-3 contratos por proveedor
            num_contratos = random.randint(2, 3)
            for j in range(num_contratos):
                fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 365))
                fecha_fin = fecha_inicio + timedelta(days=random.randint(180, 730))
                tipo = random.choice(tipos_contrato)
                estado = random.choice(estados_contrato)
                
                # Si el contrato está vencido, ajustar fecha_fin
                if estado == "vencido":
                    fecha_fin = datetime.now() - timedelta(days=random.randint(1, 90))
                elif estado == "finalizado":
                    fecha_fin = datetime.now() - timedelta(days=random.randint(1, 180))
                
                monto = Decimal(str(random.uniform(5000, 50000)))
                
                try:
                    contrato_id = await conn.fetchval("""
                        INSERT INTO contratos (proveedor_id, numero_contrato, tipo, fecha_inicio, 
                                              fecha_fin, monto_total, estado, descripcion)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        RETURNING id
                    """, proveedor_id, f"CONT-{proveedor_id}-{j+1:03d}", tipo, 
                        fecha_inicio.date(), fecha_fin.date(), monto, estado,
                        f"Contrato de {tipo} con proveedor {proveedor_id}")
                    contrato_ids.append(contrato_id)
                    print(f"   ✅ Contrato CONT-{proveedor_id}-{j+1:03d} ({tipo})")
                except Exception as e:
                    print(f"   ⚠️  Error al insertar contrato: {e}")
        
        # 5. Obtener categorías existentes
        categorias = await conn.fetch("SELECT id, nombre FROM categorias_equipos")
        categoria_map = {cat["nombre"]: cat["id"] for cat in categorias}
        
        # 6. EQUIPOS
        print("\n💻 Insertando equipos...")
        equipo_ids = []
        estados_operativos = ["operativo", "operativo", "operativo", "en_reparacion", "obsoleto", "baja"]
        estados_fisicos = ["bueno", "bueno", "bueno", "regular", "malo"]
        
        codigo_counter = 1
        for categoria_nombre, categoria_id in categoria_map.items():
            if categoria_nombre == "Otro":
                continue
            
            # 5-10 equipos por categoría
            num_equipos = random.randint(5, 10)
            marcas = MARCAS_EQUIPOS.get(categoria_nombre, ["Genérico"])
            modelos = MODELOS_EQUIPOS.get(categoria_nombre, ["Modelo 1"])
            
            for i in range(num_equipos):
                marca = random.choice(marcas)
                modelo = random.choice(modelos)
                nombre = f"{marca} {modelo}"
                numero_serie = f"SN{random.randint(100000, 999999)}"
                codigo_inventario = f"INV-{categoria_nombre[:3].upper()}-{codigo_counter:04d}"
                codigo_counter += 1
                
                proveedor_id = random.choice(proveedor_ids) if proveedor_ids else None
                ubicacion_id = random.choice(ubicacion_ids) if ubicacion_ids else None
                asignado_id = random.choice(list(usuario_ids.values())) if random.random() > 0.3 else None
                
                fecha_compra = datetime.now() - timedelta(days=random.randint(30, 1095))
                costo_compra = Decimal(str(random.uniform(200, 5000)))
                fecha_garantia_fin = fecha_compra + timedelta(days=random.randint(365, 1095))
                
                estado_operativo = random.choice(estados_operativos)
                estado_fisico = random.choice(estados_fisicos)
                
                especificaciones = json.dumps({
                    "procesador": f"Intel Core i{random.randint(3, 9)}",
                    "ram": f"{random.choice([4, 8, 16, 32])}GB",
                    "almacenamiento": f"{random.choice([256, 512, 1024])}GB SSD",
                    "pantalla": f"{random.choice([13, 14, 15, 17, 24, 27])}\""
                } if categoria_nombre in ["Laptop", "Desktop", "Monitor"] else {})
                
                try:
                    equipo_id = await conn.fetchval("""
                        INSERT INTO equipos (codigo_inventario, categoria_id, nombre, marca, modelo,
                                           numero_serie, especificaciones, proveedor_id, fecha_compra,
                                           costo_compra, fecha_garantia_fin, ubicacion_actual_id,
                                           estado_operativo, estado_fisico, asignado_a_id, notas)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                        RETURNING id
                    """, codigo_inventario, categoria_id, nombre, marca, modelo, numero_serie,
                        especificaciones, proveedor_id, fecha_compra.date(), costo_compra,
                        fecha_garantia_fin.date(), ubicacion_id, estado_operativo, estado_fisico,
                        asignado_id, f"Equipo adquirido en {fecha_compra.strftime('%Y-%m-%d')}")
                    equipo_ids.append(equipo_id)
                    print(f"   ✅ {codigo_inventario} - {nombre}")
                except Exception as e:
                    print(f"   ⚠️  Error al insertar equipo: {e}")
        
        # 7. MANTENIMIENTOS
        print("\n🔧 Insertando mantenimientos...")
        mantenimiento_ids = []
        tipos_mantenimiento = ["preventivo", "correctivo"]
        estados_mantenimiento = ["programado", "en_proceso", "completado", "completado", "completado"]
        prioridades = ["urgente", "alta", "media", "baja"]
        tecnicos = [uid for username, uid in usuario_ids.items() if username in ["jperez", "mgarcia"]]
        
        for equipo_id in equipo_ids[:len(equipo_ids)//2]:  # Mantenimientos para la mitad de equipos
            num_mantenimientos = random.randint(1, 4)
            
            for i in range(num_mantenimientos):
                tipo = random.choice(tipos_mantenimiento)
                fecha_programada = datetime.now() - timedelta(days=random.randint(0, 180))
                fecha_realizada = None
                estado = random.choice(estados_mantenimiento)
                
                if estado in ["completado", "en_proceso"]:
                    fecha_realizada = fecha_programada + timedelta(days=random.randint(0, 7))
                
                tecnico_id = random.choice(tecnicos) if tecnicos and random.random() > 0.3 else None
                proveedor_mant_id = random.choice(proveedor_ids) if random.random() > 0.5 else None
                
                costo = Decimal(str(random.uniform(50, 500))) if estado == "completado" else None
                tiempo_fuera = Decimal(str(random.uniform(1, 24))) if estado == "completado" else None
                prioridad = random.choice(prioridades)
                
                descripcion = f"Mantenimiento {tipo} del equipo {equipo_id}"
                problema = f"Problema reportado: {random.choice(['Fallo de hardware', 'Actualización de software', 'Limpieza general', 'Revisión preventiva'])}" if tipo == "correctivo" else None
                solucion = f"Solucionado: {random.choice(['Reparación exitosa', 'Reemplazo de componente', 'Actualización completada', 'Limpieza realizada'])}" if estado == "completado" else None
                
                try:
                    mant_id = await conn.fetchval("""
                        INSERT INTO mantenimientos (equipo_id, tipo, fecha_programada, fecha_realizada,
                                                   tecnico_id, proveedor_id, descripcion, problema_reportado,
                                                   solucion_aplicada, costo, tiempo_fuera_servicio_horas,
                                                   estado, prioridad, observaciones)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        RETURNING id
                    """, equipo_id, tipo, fecha_programada.date(), fecha_realizada.date() if fecha_realizada else None,
                        tecnico_id, proveedor_mant_id, descripcion, problema, solucion, costo, tiempo_fuera,
                        estado, prioridad, f"Observaciones del mantenimiento {i+1}")
                    mantenimiento_ids.append(mant_id)
                    print(f"   ✅ Mantenimiento {tipo} - Equipo {equipo_id}")
                except Exception as e:
                    print(f"   ⚠️  Error al insertar mantenimiento: {e}")
        
        # 8. MOVIMIENTOS DE EQUIPOS
        print("\n📦 Insertando movimientos de equipos...")
        for equipo_id in equipo_ids[:len(equipo_ids)//3]:  # Movimientos para 1/3 de equipos
            num_movimientos = random.randint(1, 3)
            ubicacion_actual = random.choice(ubicacion_ids)
            
            for i in range(num_movimientos):
                ubicacion_origen = ubicacion_actual
                ubicacion_destino = random.choice([u for u in ubicacion_ids if u != ubicacion_actual])
                usuario_responsable = random.choice(list(usuario_ids.values()))
                fecha_movimiento = datetime.now() - timedelta(days=random.randint(1, 180))
                motivo = random.choice([
                    "Reasignación de equipo",
                    "Cambio de ubicación",
                    "Mantenimiento",
                    "Actualización de inventario",
                    "Traslado de oficina"
                ])
                
                try:
                    await conn.execute("""
                        INSERT INTO movimientos_equipos (equipo_id, ubicacion_origen_id, ubicacion_destino_id,
                                                        usuario_responsable_id, fecha_movimiento, motivo, observaciones)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, equipo_id, ubicacion_origen, ubicacion_destino, usuario_responsable,
                        fecha_movimiento, motivo, f"Movimiento {i+1} del equipo")
                    print(f"   ✅ Movimiento de equipo {equipo_id}")
                except Exception as e:
                    print(f"   ⚠️  Error al insertar movimiento: {e}")
                
                ubicacion_actual = ubicacion_destino
        
        # 9. NOTIFICACIONES
        print("\n🔔 Insertando notificaciones...")
        tipos_notificacion = [
            "mantenimiento_programado",
            "garantia_por_vencer",
            "equipo_obsoleto",
            "mantenimiento_completado",
            "movimiento_equipo"
        ]
        
        for i in range(20):
            tipo = random.choice(tipos_notificacion)
            usuario_id = random.choice(list(usuario_ids.values()))
            equipo_id = random.choice(equipo_ids) if random.random() > 0.3 else None
            mantenimiento_id = random.choice(mantenimiento_ids) if mantenimiento_ids and random.random() > 0.5 else None
            
            titulos = {
                "mantenimiento_programado": "Mantenimiento Programado",
                "garantia_por_vencer": "Garantía por Vencer",
                "equipo_obsoleto": "Equipo Obsoleto Detectado",
                "mantenimiento_completado": "Mantenimiento Completado",
                "movimiento_equipo": "Movimiento de Equipo"
            }
            
            mensajes = {
                "mantenimiento_programado": f"El equipo {equipo_id} tiene un mantenimiento programado para la próxima semana.",
                "garantia_por_vencer": f"La garantía del equipo {equipo_id} vence en los próximos 30 días.",
                "equipo_obsoleto": f"El equipo {equipo_id} ha superado su vida útil recomendada.",
                "mantenimiento_completado": f"El mantenimiento del equipo {equipo_id} ha sido completado exitosamente.",
                "movimiento_equipo": f"El equipo {equipo_id} ha sido movido a una nueva ubicación."
            }
            
            fecha_creacion = datetime.now() - timedelta(days=random.randint(0, 30))
            leida = random.choice([True, False])
            fecha_lectura = fecha_creacion + timedelta(days=random.randint(0, 5)) if leida else None
            
            try:
                await conn.execute("""
                    INSERT INTO notificaciones (tipo, titulo, mensaje, usuario_id, equipo_id,
                                              mantenimiento_id, leida, fecha_creacion, fecha_lectura)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, tipo, titulos[tipo], mensajes[tipo], usuario_id, equipo_id, mantenimiento_id,
                    leida, fecha_creacion, fecha_lectura)
                print(f"   ✅ Notificación: {titulos[tipo]}")
            except Exception as e:
                print(f"   ⚠️  Error al insertar notificación: {e}")
        
        # Resumen
        print("\n" + "="*50)
        print("📊 RESUMEN DE DATOS INSERTADOS")
        print("="*50)
        
        counts = {
            "usuarios": await conn.fetchval("SELECT COUNT(*) FROM usuarios"),
            "ubicaciones": await conn.fetchval("SELECT COUNT(*) FROM ubicaciones"),
            "proveedores": await conn.fetchval("SELECT COUNT(*) FROM proveedores"),
            "contratos": await conn.fetchval("SELECT COUNT(*) FROM contratos"),
            "equipos": await conn.fetchval("SELECT COUNT(*) FROM equipos"),
            "mantenimientos": await conn.fetchval("SELECT COUNT(*) FROM mantenimientos"),
            "movimientos": await conn.fetchval("SELECT COUNT(*) FROM movimientos_equipos"),
            "notificaciones": await conn.fetchval("SELECT COUNT(*) FROM notificaciones")
        }
        
        for tabla, count in counts.items():
            print(f"   {tabla.capitalize()}: {count}")
        
        print("\n✅ Base de datos poblada exitosamente!")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al poblar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())




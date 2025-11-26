-- Sistema de Gestión de Equipos de TI - Universidad
-- Esquema de Base de Datos PostgreSQL

-- Crear extensión para UUID si es necesario
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== TABLA: USUARIOS ====================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario',
    nombre_completo VARCHAR(200) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_conexion TIMESTAMP
);

CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);

-- ==================== TABLA: CATEGORIAS_EQUIPOS ====================
CREATE TABLE IF NOT EXISTS categorias_equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    vida_util_anos INTEGER DEFAULT 5,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categorias_nombre ON categorias_equipos(nombre);

-- ==================== TABLA: UBICACIONES ====================
CREATE TABLE IF NOT EXISTS ubicaciones (
    id SERIAL PRIMARY KEY,
    edificio VARCHAR(100) NOT NULL,
    piso VARCHAR(50),
    aula_oficina VARCHAR(100) NOT NULL,
    descripcion TEXT,
    responsable_id INTEGER REFERENCES usuarios(id),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ubicaciones_edificio ON ubicaciones(edificio);
CREATE INDEX idx_ubicaciones_activo ON ubicaciones(activo);
CREATE INDEX idx_ubicaciones_responsable ON ubicaciones(responsable_id);

-- ==================== TABLA: PROVEEDORES ====================
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(200) NOT NULL,
    ruc VARCHAR(20) UNIQUE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(50),
    email VARCHAR(100),
    contacto_nombre VARCHAR(200),
    contacto_telefono VARCHAR(50),
    sitio_web VARCHAR(255),
    calificacion DECIMAL(3,2) CHECK (calificacion >= 0 AND calificacion <= 5),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

CREATE INDEX idx_proveedores_ruc ON proveedores(ruc);
CREATE INDEX idx_proveedores_activo ON proveedores(activo);
CREATE INDEX idx_proveedores_razon_social ON proveedores(razon_social);

-- ==================== TABLA: CONTRATOS ====================
CREATE TABLE IF NOT EXISTS contratos (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
    numero_contrato VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    monto_total DECIMAL(12,2),
    estado VARCHAR(20) DEFAULT 'vigente',
    archivo_url VARCHAR(500),
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (fecha_fin >= fecha_inicio)
);

CREATE INDEX idx_contratos_proveedor ON contratos(proveedor_id);
CREATE INDEX idx_contratos_numero ON contratos(numero_contrato);
CREATE INDEX idx_contratos_estado ON contratos(estado);
CREATE INDEX idx_contratos_fechas ON contratos(fecha_inicio, fecha_fin);

-- ==================== TABLA: EQUIPOS ====================
CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    codigo_inventario VARCHAR(100) UNIQUE NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias_equipos(id),
    nombre VARCHAR(200) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    numero_serie VARCHAR(100) UNIQUE,
    especificaciones JSONB,
    proveedor_id INTEGER REFERENCES proveedores(id),
    fecha_compra DATE,
    costo_compra DECIMAL(12,2),
    fecha_garantia_fin DATE,
    ubicacion_actual_id INTEGER REFERENCES ubicaciones(id),
    estado_operativo VARCHAR(50) DEFAULT 'operativo',
    estado_fisico VARCHAR(50) DEFAULT 'bueno',
    asignado_a_id INTEGER REFERENCES usuarios(id),
    notas TEXT,
    imagen_url VARCHAR(500),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipos_codigo ON equipos(codigo_inventario);
CREATE INDEX idx_equipos_categoria ON equipos(categoria_id);
CREATE INDEX idx_equipos_proveedor ON equipos(proveedor_id);
CREATE INDEX idx_equipos_ubicacion ON equipos(ubicacion_actual_id);
CREATE INDEX idx_equipos_estado_operativo ON equipos(estado_operativo);
CREATE INDEX idx_equipos_asignado ON equipos(asignado_a_id);
CREATE INDEX idx_equipos_fecha_registro ON equipos(fecha_registro);

-- ==================== TABLA: MOVIMIENTOS_EQUIPOS ====================
CREATE TABLE IF NOT EXISTS movimientos_equipos (
    id SERIAL PRIMARY KEY,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    ubicacion_origen_id INTEGER REFERENCES ubicaciones(id),
    ubicacion_destino_id INTEGER NOT NULL REFERENCES ubicaciones(id),
    usuario_responsable_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(200) NOT NULL,
    observaciones TEXT
);

CREATE INDEX idx_movimientos_equipo ON movimientos_equipos(equipo_id);
CREATE INDEX idx_movimientos_fecha ON movimientos_equipos(fecha_movimiento);
CREATE INDEX idx_movimientos_responsable ON movimientos_equipos(usuario_responsable_id);
CREATE INDEX idx_movimientos_destino ON movimientos_equipos(ubicacion_destino_id);

-- ==================== TABLA: MANTENIMIENTOS ====================
CREATE TABLE IF NOT EXISTS mantenimientos (
    id SERIAL PRIMARY KEY,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('preventivo', 'correctivo')),
    fecha_programada DATE NOT NULL,
    fecha_realizada DATE,
    tecnico_id INTEGER REFERENCES usuarios(id),
    proveedor_id INTEGER REFERENCES proveedores(id),
    descripcion TEXT NOT NULL,
    problema_reportado TEXT,
    solucion_aplicada TEXT,
    costo DECIMAL(12,2),
    tiempo_fuera_servicio_horas DECIMAL(8,2),
    estado VARCHAR(50) DEFAULT 'programado' CHECK (estado IN ('programado', 'en_proceso', 'completado', 'cancelado')),
    prioridad VARCHAR(20) DEFAULT 'media' CHECK (prioridad IN ('urgente', 'alta', 'media', 'baja')),
    partes_reemplazadas JSONB,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mantenimientos_equipo ON mantenimientos(equipo_id);
CREATE INDEX idx_mantenimientos_fecha_programada ON mantenimientos(fecha_programada);
CREATE INDEX idx_mantenimientos_fecha_realizada ON mantenimientos(fecha_realizada);
CREATE INDEX idx_mantenimientos_estado ON mantenimientos(estado);
CREATE INDEX idx_mantenimientos_tipo ON mantenimientos(tipo);
CREATE INDEX idx_mantenimientos_prioridad ON mantenimientos(prioridad);
CREATE INDEX idx_mantenimientos_tecnico ON mantenimientos(tecnico_id);

-- ==================== TABLA: NOTIFICACIONES ====================
CREATE TABLE IF NOT EXISTS notificaciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id),
    equipo_id INTEGER REFERENCES equipos(id),
    mantenimiento_id INTEGER REFERENCES mantenimientos(id),
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_lectura TIMESTAMP
);

CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id);
CREATE INDEX idx_notificaciones_equipo ON notificaciones(equipo_id);
CREATE INDEX idx_notificaciones_mantenimiento ON notificaciones(mantenimiento_id);
CREATE INDEX idx_notificaciones_leida ON notificaciones(leida);
CREATE INDEX idx_notificaciones_fecha_creacion ON notificaciones(fecha_creacion);
CREATE INDEX idx_notificaciones_tipo ON notificaciones(tipo);

-- ==================== DATOS INICIALES ====================

-- Insertar categorías de equipos por defecto
INSERT INTO categorias_equipos (nombre, descripcion, vida_util_anos) VALUES
('Laptop', 'Computadoras portátiles', 4),
('Desktop', 'Computadoras de escritorio', 5),
('Monitor', 'Monitores y pantallas', 6),
('Impresora', 'Impresoras y multifuncionales', 5),
('Servidor', 'Servidores y equipos de red', 6),
('Tablet', 'Tablets y dispositivos móviles', 3),
('Proyector', 'Proyectores y equipos de presentación', 5),
('Router', 'Routers y equipos de red', 4),
('Switch', 'Switches y equipos de red', 5),
('Otro', 'Otros equipos de TI', 5)
ON CONFLICT (nombre) DO NOTHING;

-- Insertar usuario administrador por defecto (password: admin123)
-- Nota: En producción, cambiar la contraseña hash
INSERT INTO usuarios (username, email, password_hash, rol, nombre_completo, activo) VALUES
('admin', 'admin@universidad.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJZqJZqJZ', 'admin', 'Administrador del Sistema', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Insertar ubicaciones de ejemplo
INSERT INTO ubicaciones (edificio, piso, aula_oficina, descripcion, activo) VALUES
('Edificio Principal', '1', 'Aula 101', 'Aula de informática', TRUE),
('Edificio Principal', '1', 'Aula 102', 'Aula de informática', TRUE),
('Edificio Principal', '2', 'Oficina 201', 'Oficina administrativa', TRUE),
('Edificio Principal', '2', 'Oficina 202', 'Oficina administrativa', TRUE),
('Edificio Anexo', '1', 'Laboratorio 1', 'Laboratorio de computación', TRUE)
ON CONFLICT DO NOTHING;

-- ==================== TRIGGERS ====================

-- Trigger para actualizar fecha_ultima_actualizacion en equipos
CREATE OR REPLACE FUNCTION update_equipos_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_ultima_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_equipos_timestamp
    BEFORE UPDATE ON equipos
    FOR EACH ROW
    EXECUTE FUNCTION update_equipos_timestamp();

-- ==================== COMENTARIOS EN TABLAS ====================

COMMENT ON TABLE usuarios IS 'Usuarios del sistema';
COMMENT ON TABLE categorias_equipos IS 'Categorías de equipos de TI';
COMMENT ON TABLE ubicaciones IS 'Ubicaciones físicas de los equipos';
COMMENT ON TABLE proveedores IS 'Proveedores de equipos y servicios';
COMMENT ON TABLE contratos IS 'Contratos con proveedores';
COMMENT ON TABLE equipos IS 'Inventario de equipos de TI';
COMMENT ON TABLE movimientos_equipos IS 'Historial de movimientos de equipos';
COMMENT ON TABLE mantenimientos IS 'Registro de mantenimientos preventivos y correctivos';
COMMENT ON TABLE notificaciones IS 'Notificaciones y alertas del sistema';


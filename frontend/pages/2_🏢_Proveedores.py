import streamlit as st

# set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Gestión de Proveedores", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import pandas as pd
import os
from datetime import datetime, date

API_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

st.title("🏢 Gestión de Proveedores")
st.markdown("---")

# Funciones auxiliares
def get_proveedores(activo=None, use_cache=True):
    cache_key = 'proveedores_cache_all'
    
    # Intentar cargar desde el servidor solo si no hay caché o si se fuerza recarga
    if cache_key not in st.session_state or not use_cache:
        try:
            response = requests.get(f"{API_URL}/api/proveedores", timeout=10)
            if response.status_code == 200:
                data = response.json()
                data = data if isinstance(data, list) else []
                # Solo actualizar caché si la respuesta es exitosa
                st.session_state[cache_key] = data
            # Si hay error HTTP, mantener el caché existente (no sobrescribir)
            # Si no hay caché y hay error, no hacer nada (se retornará lista vacía)
        except requests.exceptions.RequestException as e:
            # Si hay error de conexión, mantener el caché existente (no sobrescribir)
            # Si no hay caché y hay error, no hacer nada (se retornará lista vacía)
            pass
        except Exception as e:
            # Si hay otro error, mantener el caché existente (no sobrescribir)
            # Si no hay caché y hay error, no hacer nada (se retornará lista vacía)
            pass
    
    # Obtener datos del caché (puede no existir si nunca se cargó exitosamente)
    data = st.session_state.get(cache_key, [])
    
    # Aplicar filtro si es necesario
    if activo is not None:
        if activo:
            data = [p for p in data if p.get('activo', True)]
        else:
            data = [p for p in data if not p.get('activo', False)]
    
    return data

def refresh_proveedores():
    """Forzar recarga de proveedores desde el servidor"""
    if 'proveedores_cache_all' in st.session_state:
        del st.session_state['proveedores_cache_all']

def get_proveedor(proveedor_id):
    try:
        response = requests.get(f"{API_URL}/api/proveedores/{proveedor_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_contratos(proveedor_id=None):
    params = {}
    if proveedor_id:
        params['proveedor_id'] = proveedor_id
    
    try:
        response = requests.get(f"{API_URL}/api/contratos", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📋 Lista de Proveedores", "➕ Nuevo Proveedor", "📄 Contratos"])

with tab1:
    st.subheader("Catálogo de Proveedores")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_activo = st.selectbox("Estado", ["Todos", "Activos", "Inactivos"])
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Buscar", use_container_width=True):
            st.rerun()
    
    with col3:
        st.write("")
        st.write("")
        if st.button("🔄 Actualizar", use_container_width=True):
            refresh_proveedores()
            st.rerun()
    
    activo_filtro = None
    if filtro_activo == "Activos":
        activo_filtro = True
    elif filtro_activo == "Inactivos":
        activo_filtro = False
    
    # Intentar cargar proveedores
    cache_key = 'proveedores_cache_all'
    proveedores = []
    usando_cache = False
    
    try:
        proveedores = get_proveedores(activo=activo_filtro, use_cache=True)
        # Verificar si estamos usando datos del caché porque la última carga falló
        if cache_key in st.session_state and len(st.session_state[cache_key]) > 0:
            # Intentar una carga fresca en segundo plano (sin bloquear la UI)
            try:
                response = requests.get(f"{API_URL}/api/proveedores", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        st.session_state[cache_key] = data
                        # Recargar con los nuevos datos
                        if activo_filtro is not None:
                            if activo_filtro:
                                proveedores = [p for p in data if p.get('activo', True)]
                            else:
                                proveedores = [p for p in data if not p.get('activo', False)]
                        else:
                            proveedores = data
            except:
                # Si falla la recarga, usar el caché existente
                usando_cache = True
                pass
    except Exception as e:
        # Si hay error, intentar usar el caché
        if cache_key in st.session_state and len(st.session_state[cache_key]) > 0:
            usando_cache = True
            proveedores = st.session_state[cache_key]
            if activo_filtro is not None:
                if activo_filtro:
                    proveedores = [p for p in proveedores if p.get('activo', True)]
                else:
                    proveedores = [p for p in proveedores if not p.get('activo', False)]
        else:
            st.error(f"⚠️ Error al cargar proveedores: {str(e)}")
            proveedores = []
    
    # Mostrar advertencia si estamos usando caché
    if usando_cache:
        st.warning("⚠️ Mostrando datos en caché. Puede que no estén actualizados. Use el botón 'Actualizar' para recargar.")
    
    if proveedores:
        st.success(f"Se encontraron {len(proveedores)} proveedores")
        
        # Convertir a DataFrame
        df = pd.DataFrame(proveedores)
        
        # Seleccionar columnas relevantes
        columnas_mostrar = ['id', 'razon_social', 'ruc', 'telefono', 'email', 'activo']
        columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
        df_mostrar = df[columnas_disponibles]
        
        # Renombrar columnas
        df_mostrar.columns = ['ID', 'Razón Social', 'RUC', 'Teléfono', 'Email', 'Activo'][:len(df_mostrar.columns)]
        
        st.dataframe(df_mostrar, use_container_width=True, height=400)
        
        # Detalle de proveedor seleccionado
        st.markdown("---")
        st.subheader("Detalle de Proveedor")
        
        proveedor_seleccionado = st.selectbox(
            "Seleccionar proveedor",
            options=[p['id'] for p in proveedores],
            format_func=lambda x: f"{x} - {next((p['razon_social'] for p in proveedores if p['id'] == x), '')}"
        )
        
        if proveedor_seleccionado:
            proveedor = get_proveedor(proveedor_seleccionado)
            
            if proveedor:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Información General")
                    st.write(f"**Razón Social:** {proveedor.get('razon_social', 'N/A')}")
                    st.write(f"**RUC:** {proveedor.get('ruc', 'N/A')}")
                    st.write(f"**Dirección:** {proveedor.get('direccion', 'N/A')}")
                    st.write(f"**Teléfono:** {proveedor.get('telefono', 'N/A')}")
                    st.write(f"**Email:** {proveedor.get('email', 'N/A')}")
                    st.write(f"**Sitio Web:** {proveedor.get('sitio_web', 'N/A')}")
                
                with col2:
                    st.markdown("#### Contacto")
                    st.write(f"**Contacto:** {proveedor.get('contacto_nombre', 'N/A')}")
                    st.write(f"**Teléfono Contacto:** {proveedor.get('contacto_telefono', 'N/A')}")
                    
                    if proveedor.get('calificacion'):
                        st.write(f"**Calificación:** {proveedor['calificacion']}/5.0")
                    
                    estado = "Activo" if proveedor.get('activo') else "Inactivo"
                    if proveedor.get('activo'):
                        st.success(f"🟢 {estado}")
                    else:
                        st.error(f"🔴 {estado}")
                    
                    if proveedor.get('estadisticas_compras'):
                        stats = proveedor['estadisticas_compras']
                        st.markdown("#### Estadísticas")
                        total = stats.get('total', 0) or 0
                        total_comprado = stats.get('total_comprado', 0) or 0
                        st.write(f"**Equipos comprados:** {total}")
                        st.write(f"**Total comprado:** ${float(total_comprado):,.2f}")
                
                if proveedor.get('contratos'):
                    st.markdown("---")
                    st.markdown("#### Contratos")
                    df_contratos = pd.DataFrame(proveedor['contratos'])
                    st.dataframe(df_contratos[['numero_contrato', 'tipo', 'fecha_inicio', 'fecha_fin', 'estado', 'monto_total']], use_container_width=True)
    else:
        st.info("No se encontraron proveedores con los filtros seleccionados")

with tab2:
    st.subheader("Registrar Nuevo Proveedor")
    
    with st.form("form_nuevo_proveedor"):
        col1, col2 = st.columns(2)
        
        with col1:
            razon_social = st.text_input("Razón Social*", placeholder="Empresa Tecnológica S.A.")
            ruc = st.text_input("RUC*", placeholder="12345678901")
            direccion = st.text_input("Dirección", placeholder="Av. Principal 123")
            telefono = st.text_input("Teléfono", placeholder="+51 123 456 789")
            email = st.text_input("Email", placeholder="contacto@empresa.com")
        
        with col2:
            contacto_nombre = st.text_input("Nombre de Contacto", placeholder="Juan Pérez")
            contacto_telefono = st.text_input("Teléfono de Contacto", placeholder="+51 987 654 321")
            sitio_web = st.text_input("Sitio Web", placeholder="https://www.empresa.com")
            notas = st.text_area("Notas", placeholder="Información adicional del proveedor...")
        
        submitted = st.form_submit_button("💾 Guardar Proveedor", use_container_width=True)
        
        if submitted:
            if not razon_social or not ruc:
                st.error("⚠️ Los campos Razón Social y RUC son obligatorios")
            else:
                nuevo_proveedor = {
                    "razon_social": razon_social,
                    "ruc": ruc,
                    "direccion": direccion,
                    "telefono": telefono,
                    "email": email,
                    "contacto_nombre": contacto_nombre,
                    "contacto_telefono": contacto_telefono,
                    "sitio_web": sitio_web,
                    "notas": notas
                }
                
                try:
                    response = requests.post(
                        f"{API_URL}/api/proveedores",
                        json=nuevo_proveedor,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Proveedor registrado exitosamente")
                        st.balloons()
                        # Limpiar cache para refrescar datos
                        refresh_proveedores()
                        st.rerun()  # Recargar la página para mostrar el nuevo proveedor
                    else:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("detail", response.text)
                            st.error(f"❌ Error al registrar proveedor: {error_msg}")
                        except:
                            st.error(f"❌ Error al registrar proveedor: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error de conexión: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

with tab3:
    st.subheader("Gestión de Contratos")
    
    proveedores = get_proveedores(activo=True)
    
    if proveedores:
        st.markdown("### Lista de Contratos")
        contratos = get_contratos()
        
        if contratos:
            df_contratos = pd.DataFrame(contratos)
            st.dataframe(df_contratos[['numero_contrato', 'proveedor_nombre', 'tipo', 'fecha_inicio', 'fecha_fin', 'estado', 'monto_total']], use_container_width=True)
        else:
            st.info("No hay contratos registrados")
        
        st.markdown("---")
        st.markdown("### Nuevo Contrato")
        
        with st.form("form_nuevo_contrato"):
            col1, col2 = st.columns(2)
            
            with col1:
                proveedor_id = st.selectbox(
                    "Proveedor*",
                    options=[p['id'] for p in proveedores],
                    format_func=lambda x: next((p['razon_social'] for p in proveedores if p['id'] == x), '')
                )
                numero_contrato = st.text_input("Número de Contrato*", placeholder="CONT-2024-001")
                tipo = st.selectbox("Tipo*", ["compra", "servicio", "mantenimiento", "otro"])
            
            with col2:
                fecha_inicio = st.date_input("Fecha Inicio*", value=date.today())
                fecha_fin = st.date_input("Fecha Fin*", value=date.today())
                monto_total = st.number_input("Monto Total", min_value=0.0, value=0.0, format="%.2f")
                descripcion = st.text_area("Descripción", placeholder="Descripción del contrato...")
            
            submitted = st.form_submit_button("💾 Guardar Contrato", use_container_width=True)
            
            if submitted:
                if not numero_contrato:
                    st.error("⚠️ El número de contrato es obligatorio")
                else:
                    nuevo_contrato = {
                        "proveedor_id": int(proveedor_id),
                        "numero_contrato": numero_contrato.strip(),
                        "tipo": tipo,
                        "fecha_inicio": str(fecha_inicio),
                        "fecha_fin": str(fecha_fin),
                        "monto_total": float(monto_total) if monto_total > 0 else None,
                        "descripcion": descripcion.strip() if descripcion and descripcion.strip() else None
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_URL}/api/contratos",
                            json=nuevo_contrato,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Contrato registrado exitosamente")
                            st.balloons()
                            st.rerun()
                        else:
                            try:
                                error_data = response.json()
                                error_msg = error_data.get("detail", response.text)
                                st.error(f"❌ Error al registrar contrato: {error_msg}")
                                # Mostrar detalles adicionales para depuración
                                with st.expander("Ver detalles del error"):
                                    st.json(error_data)
                            except:
                                st.error(f"❌ Error al registrar contrato: {response.text}")
                                st.code(f"Status Code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Error de conexión: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")
                        import traceback
                        with st.expander("Ver stack trace"):
                            st.code(traceback.format_exc())
    else:
        st.warning("No hay proveedores activos. Registre un proveedor primero.")


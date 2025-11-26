import streamlit as st

# set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Gestión de Mantenimientos", 
    page_icon="🔧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import pandas as pd
import os
from datetime import datetime, date, timedelta

API_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

st.title("🔧 Gestión de Mantenimientos")
st.markdown("---")

# Funciones auxiliares
def get_equipos():
    try:
        response = requests.get(f"{API_URL}/api/equipos", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_mantenimientos(equipo_id=None, estado=None, tipo=None):
    params = {}
    if equipo_id:
        params['equipo_id'] = equipo_id
    if estado:
        params['estado'] = estado
    if tipo:
        params['tipo'] = tipo
    
    try:
        response = requests.get(f"{API_URL}/api/mantenimientos", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def get_calendario_mantenimientos(mes=None, año=None):
    params = {}
    if mes:
        params['mes'] = mes
    if año:
        params['año'] = año
    
    try:
        response = requests.get(f"{API_URL}/api/mantenimientos/calendario", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_estadisticas_mantenimientos():
    try:
        response = requests.get(f"{API_URL}/api/mantenimientos/estadisticas", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Mantenimientos", "➕ Nuevo Mantenimiento", "📅 Calendario", "📊 Estadísticas"])

with tab1:
    st.subheader("Historial de Mantenimientos")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    equipos = get_equipos()
    equipos_opciones = ["Todos"] + [f"{e['codigo_inventario']} - {e['nombre']}" for e in equipos]
    
    with col1:
        equipo_seleccionado = st.selectbox("Equipo", equipos_opciones)
    
    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "programado", "en_proceso", "completado", "cancelado"])
    
    with col3:
        filtro_tipo = st.selectbox("Tipo", ["Todos", "preventivo", "correctivo"])
    
    with col4:
        st.write("")
        st.write("")
        if st.button("🔍 Buscar", use_container_width=True):
            st.rerun()
    
    equipo_id_filtro = None
    if equipo_seleccionado != "Todos":
        codigo = equipo_seleccionado.split(" - ")[0]
        equipo = next((e for e in equipos if e['codigo_inventario'] == codigo), None)
        if equipo:
            equipo_id_filtro = equipo['id']
    
    estado_filtro = filtro_estado if filtro_estado != "Todos" else None
    tipo_filtro = filtro_tipo if filtro_tipo != "Todos" else None
    
    mantenimientos = get_mantenimientos(equipo_id=equipo_id_filtro, estado=estado_filtro, tipo=tipo_filtro)
    
    if mantenimientos:
        st.success(f"Se encontraron {len(mantenimientos)} mantenimientos")
        
        # Convertir a DataFrame
        df = pd.DataFrame(mantenimientos)
        
        # Seleccionar columnas relevantes
        columnas_mostrar = ['id', 'equipo_nombre', 'tipo', 'fecha_programada', 'fecha_realizada', 'estado', 'prioridad', 'costo']
        columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
        df_mostrar = df[columnas_disponibles]
        
        st.dataframe(df_mostrar, use_container_width=True, height=400)
    else:
        st.info("No se encontraron mantenimientos con los filtros seleccionados")

with tab2:
    st.subheader("Registrar Nuevo Mantenimiento")
    
    equipos = get_equipos()
    
    if equipos:
        with st.form("form_nuevo_mantenimiento"):
            col1, col2 = st.columns(2)
            
            with col1:
                equipo_id = st.selectbox(
                    "Equipo*",
                    options=[e['id'] for e in equipos],
                    format_func=lambda x: f"{next((e['codigo_inventario'] for e in equipos if e['id'] == x), '')} - {next((e['nombre'] for e in equipos if e['id'] == x), '')}"
                )
                tipo = st.selectbox("Tipo de Mantenimiento*", ["preventivo", "correctivo"])
                fecha_programada = st.date_input("Fecha Programada*", value=date.today())
                prioridad = st.selectbox("Prioridad", ["baja", "media", "alta", "urgente"], index=1)
                descripcion = st.text_area("Descripción*", placeholder="Descripción del mantenimiento...")
            
            with col2:
                problema_reportado = st.text_area("Problema Reportado", placeholder="Solo para mantenimientos correctivos...")
                observaciones = st.text_area("Observaciones", placeholder="Observaciones adicionales...")
            
            submitted = st.form_submit_button("💾 Guardar Mantenimiento", use_container_width=True)
            
            if submitted:
                if not descripcion:
                    st.error("⚠️ La descripción es obligatoria")
                else:
                    nuevo_mantenimiento = {
                        "equipo_id": equipo_id,
                        "tipo": tipo,
                        "fecha_programada": str(fecha_programada),
                        "descripcion": descripcion,
                        "problema_reportado": problema_reportado if problema_reportado else None,
                        "prioridad": prioridad,
                        "observaciones": observaciones if observaciones else None
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_URL}/api/mantenimientos",
                            json=nuevo_mantenimiento,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Mantenimiento registrado exitosamente")
                            if tipo == "correctivo":
                                st.info("ℹ️ El estado del equipo se ha cambiado a 'en_reparacion'")
                            st.balloons()
                        else:
                            st.error(f"❌ Error al registrar mantenimiento: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error de conexión: {e}")
    else:
        st.warning("No hay equipos registrados. Registre un equipo primero.")

with tab3:
    st.subheader("Calendario de Mantenimientos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
    
    with col2:
        año_seleccionado = st.selectbox("Año", range(2020, 2030), index=4)
    
    calendario = get_calendario_mantenimientos(mes=mes_seleccionado, año=año_seleccionado)
    
    if calendario:
        df_calendario = pd.DataFrame(calendario)
        
        # Agrupar por fecha
        df_por_fecha = df_calendario.groupby('fecha_programada').agg({
            'id': 'count',
            'tipo': lambda x: ', '.join(x),
            'equipo_nombre': lambda x: ', '.join(x)
        }).reset_index()
        df_por_fecha.columns = ['Fecha', 'Cantidad', 'Tipos', 'Equipos']
        
        st.dataframe(df_por_fecha, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Detalle por Fecha")
        
        fecha_seleccionada = st.selectbox(
            "Seleccionar fecha",
            options=df_calendario['fecha_programada'].unique()
        )
        
        mantenimientos_fecha = df_calendario[df_calendario['fecha_programada'] == fecha_seleccionada]
        
        for _, mant in mantenimientos_fecha.iterrows():
            with st.expander(f"{mant['equipo_nombre']} - {mant['tipo'].upper()}"):
                st.write(f"**Prioridad:** {mant.get('prioridad', 'N/A')}")
                st.write(f"**Estado:** {mant.get('estado', 'N/A')}")
                if mant.get('tecnico_nombre'):
                    st.write(f"**Técnico:** {mant['tecnico_nombre']}")
    else:
        st.info(f"No hay mantenimientos programados para {mes_seleccionado}/{año_seleccionado}")

with tab4:
    st.subheader("Estadísticas de Mantenimientos")
    
    estadisticas = get_estadisticas_mantenimientos()
    
    if estadisticas:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Mantenimientos", estadisticas.get('total', 0))
        
        with col2:
            costo_total = estadisticas.get('costo_total', 0)
            st.metric("Costo Total", f"${costo_total:,.2f}")
        
        with col3:
            st.markdown("#### Por Tipo")
            if estadisticas.get('por_tipo'):
                df_tipo = pd.DataFrame(estadisticas['por_tipo'])
                st.bar_chart(df_tipo.set_index('tipo')['cantidad'])
        
        with col4:
            st.markdown("#### Por Estado")
            if estadisticas.get('por_estado'):
                df_estado = pd.DataFrame(estadisticas['por_estado'])
                st.bar_chart(df_estado.set_index('estado')['cantidad'])
        
        st.markdown("---")
        st.markdown("### Costos por Mes (Últimos 6 meses)")
        
        if estadisticas.get('costo_por_mes'):
            df_costos = pd.DataFrame(estadisticas['costo_por_mes'])
            st.line_chart(df_costos.set_index('mes')['total_costo'])
    else:
        st.info("No hay estadísticas disponibles")


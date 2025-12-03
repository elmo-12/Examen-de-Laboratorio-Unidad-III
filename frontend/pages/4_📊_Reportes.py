import streamlit as st

# set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Reportes y Análisis", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

API_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

st.title("📊 Reportes y Análisis")
st.markdown("---")

# Funciones auxiliares
def get_dashboard_data():
    try:
        response = requests.get(f"{API_URL}/api/reportes/dashboard", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_equipos_por_ubicacion():
    try:
        response = requests.get(f"{API_URL}/api/reportes/equipos-por-ubicacion", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_equipos_por_estado():
    try:
        response = requests.get(f"{API_URL}/api/reportes/equipos-por-estado", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_equipos_por_categoria():
    try:
        response = requests.get(f"{API_URL}/api/reportes/equipos-por-categoria", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_costos_mantenimiento(year=None):
    params = {"year": year} if year else {}
    try:
        response = requests.get(f"{API_URL}/api/reportes/costos-mantenimiento", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_equipos_antiguedad():
    try:
        response = requests.get(f"{API_URL}/api/reportes/equipos-antiguedad", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📊 Gráficos", "📄 Exportar", "🔍 Análisis Avanzado"])

with tab1:
    st.subheader("Dashboard General")
    
    dashboard = get_dashboard_data()
    
    if dashboard:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📦 Total Equipos",
                value=dashboard.get("total_equipos", 0)
            )
        
        with col2:
            st.metric(
                label="✅ Equipos Operativos",
                value=dashboard.get("equipos_operativos", 0)
            )
        
        with col3:
            st.metric(
                label="🔧 En Reparación",
                value=dashboard.get("equipos_reparacion", 0)
            )
        
        with col4:
            disponibilidad = dashboard.get("tasa_disponibilidad", 0)
            st.metric(
                label="📊 Disponibilidad",
                value=f"{disponibilidad}%",
                delta=f"{disponibilidad - 95:.1f}%"
            )
        
        st.markdown("---")
        
        # Segunda fila
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor = dashboard.get("valor_inventario", 0)
            st.metric(
                label="💰 Valor Inventario",
                value=f"${valor:,.2f}"
            )
        
        with col2:
            st.metric(
                label="🔧 Mantenimientos (Mes)",
                value=dashboard.get("mantenimientos_mes", 0)
            )
        
        with col3:
            costo = dashboard.get("costo_mantenimiento_mes", 0)
            st.metric(
                label="💵 Costo Mantenim. (Mes)",
                value=f"${costo:,.2f}"
            )
    else:
        st.error("No se pudieron cargar los datos del dashboard")

with tab2:
    st.subheader("Gráficos Estadísticos")
    
    # Equipos por ubicación
    st.markdown("### 📍 Equipos por Ubicación")
    data_ubicacion = get_equipos_por_ubicacion()
    
    if data_ubicacion:
        df_ubicacion = pd.DataFrame(data_ubicacion)
        
        fig1 = px.bar(
            df_ubicacion,
            x='ubicacion',
            y='cantidad',
            title='Distribución de Equipos por Ubicación',
            labels={'ubicacion': 'Ubicación', 'cantidad': 'Cantidad'},
            color='cantidad',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # Equipos por estado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Equipos por Estado")
        data_estado = get_equipos_por_estado()
        
        if data_estado:
            df_estado = pd.DataFrame(data_estado)
            
            fig2 = px.pie(
                df_estado,
                values='cantidad',
                names='estado',
                title='Estado Operativo de Equipos',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("### 📦 Equipos por Categoría")
        data_categoria = get_equipos_por_categoria()
        
        if data_categoria:
            df_categoria = pd.DataFrame(data_categoria)
            
            fig3 = px.pie(
                df_categoria,
                values='cantidad',
                names='categoria',
                title='Distribución por Categoría',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # Costos de mantenimiento
    st.markdown("### 💵 Costos de Mantenimiento")
    
    year_selected = st.selectbox("Seleccionar Año", [2024, 2023, 2022])
    data_costos = get_costos_mantenimiento(year=year_selected)
    
    if data_costos:
        df_costos = pd.DataFrame(data_costos)
        
        if not df_costos.empty:
            # Agrupar por mes
            df_costos_mes = df_costos.groupby('mes')['total_costo'].sum().reset_index()
            
            fig4 = px.line(
                df_costos_mes,
                x='mes',
                y='total_costo',
                title=f'Costos de Mantenimiento por Mes - {year_selected}',
                labels={'mes': 'Mes', 'total_costo': 'Costo Total ($)'},
                markers=True
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            # Gráfico por tipo
            if 'tipo' in df_costos.columns:
                df_costos_tipo = df_costos.groupby('tipo')['total_costo'].sum().reset_index()
                
                fig5 = px.bar(
                    df_costos_tipo,
                    x='tipo',
                    y='total_costo',
                    title='Costos por Tipo de Mantenimiento',
                    labels={'tipo': 'Tipo', 'total_costo': 'Costo Total ($)'},
                    color='total_costo',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # Antigüedad de equipos
    st.markdown("### ⏰ Antigüedad de Equipos")
    data_antiguedad = get_equipos_antiguedad()
    
    if data_antiguedad:
        df_antiguedad = pd.DataFrame(data_antiguedad)
        
        fig6 = px.bar(
            df_antiguedad,
            x='rango_antiguedad',
            y='cantidad',
            title='Distribución de Equipos por Antigüedad',
            labels={'rango_antiguedad': 'Antigüedad', 'cantidad': 'Cantidad'},
            color='cantidad',
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig6, use_container_width=True)

with tab3:
    st.subheader("Exportar Reportes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Exportar a PDF")
        st.write("Genera un reporte completo en formato PDF")
        
        tipo_reporte_pdf = st.selectbox(
            "Tipo de Reporte (PDF)",
            ["equipos", "mantenimientos", "proveedores"]
        )
        
        if st.button("📥 Generar PDF", use_container_width=True, key="gen_pdf"):
            with st.spinner("Generando PDF..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/reportes/export/pdf",
                        json={"type": tipo_reporte_pdf},
                        timeout=30,
                        stream=True
                    )
                    
                    if response.status_code == 200:
                        # Obtener el nombre del archivo del header Content-Disposition
                        content_disposition = response.headers.get('Content-Disposition', '')
                        filename = f"{tipo_reporte_pdf}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"')
                        
                        # Guardar en session_state para que persista después del rerun
                        st.session_state['pdf_data'] = response.content
                        st.session_state['pdf_filename'] = filename
                        st.success(f"✅ PDF generado exitosamente")
                    else:
                        st.error(f"Error al generar PDF: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Mostrar botón de descarga si hay un PDF generado
        if 'pdf_data' in st.session_state and 'pdf_filename' in st.session_state:
            st.download_button(
                label="📥 Descargar PDF",
                data=st.session_state['pdf_data'],
                file_name=st.session_state['pdf_filename'],
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf"
            )
    
    with col2:
        st.markdown("### 📊 Exportar a Excel")
        st.write("Genera un reporte detallado en formato Excel")
        
        tipo_reporte_excel = st.selectbox(
            "Tipo de Reporte (Excel)",
            ["equipos", "mantenimientos", "proveedores"]
        )
        
        if st.button("📥 Generar Excel", use_container_width=True, key="gen_excel"):
            with st.spinner("Generando Excel..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/reportes/export/excel",
                        json={"type": tipo_reporte_excel},
                        timeout=30,
                        stream=True
                    )
                    
                    if response.status_code == 200:
                        # Obtener el nombre del archivo del header Content-Disposition
                        content_disposition = response.headers.get('Content-Disposition', '')
                        filename = f"{tipo_reporte_excel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"')
                        
                        # Guardar en session_state para que persista después del rerun
                        st.session_state['excel_data'] = response.content
                        st.session_state['excel_filename'] = filename
                        st.success(f"✅ Excel generado exitosamente")
                    else:
                        st.error(f"Error al generar Excel: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Mostrar botón de descarga si hay un Excel generado
        if 'excel_data' in st.session_state and 'excel_filename' in st.session_state:
            st.download_button(
                label="📥 Descargar Excel",
                data=st.session_state['excel_data'],
                file_name=st.session_state['excel_filename'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_excel"
            )

with tab4:
    st.subheader("🔍 Análisis Avanzado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Valor por Categoría")
        data_categoria = get_equipos_por_categoria()
        
        if data_categoria:
            df_cat = pd.DataFrame(data_categoria)
            
            if 'valor_total' in df_cat.columns:
                fig = go.Figure(data=[go.Bar(
                    x=df_cat['categoria'],
                    y=df_cat['valor_total'],
                    text=df_cat['valor_total'].apply(lambda x: f'${x:,.0f}'),
                    textposition='auto',
                )])
                
                fig.update_layout(
                    title='Valor Total por Categoría',
                    xaxis_title='Categoría',
                    yaxis_title='Valor ($)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔧 Eficiencia de Mantenimiento")
        dashboard = get_dashboard_data()
        
        if dashboard:
            disponibilidad = dashboard.get("tasa_disponibilidad", 0)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=disponibilidad,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Tasa de Disponibilidad"},
                delta={'reference': 95},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 90], 'color': "yellow"},
                        {'range': [90, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📈 Tendencias")
    st.info("💡 Análisis predictivo y tendencias estarán disponibles en próximas versiones")

# Footer
st.markdown("---")
st.caption(f"⏰ Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


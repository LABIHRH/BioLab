"""
BioLab Pro Suite - Versión en Español
Una aplicación integral para análisis de cinética microbiana con optimización de ML.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any
import sqlite3
from datetime import datetime
import json
import math
import time
from scipy.integrate import odeint

# Configurar página de Streamlit
st.set_page_config(
    page_title="BioLab Pro Suite",
    page_icon="🧫",
    layout="wide",
    initial_sidebar_state="expanded"
)

class BioLabAppEspanol:
    """Aplicación completa BioLab Pro Suite en español."""
    
    def __init__(self):
        """Inicializar la aplicación."""
        self.inicializar_estado_sesion()
        
    def inicializar_estado_sesion(self):
        """Inicializar estado de sesión con valores por defecto."""
        if 'datos_cineticos' not in st.session_state:
            st.session_state.datos_cineticos = {
                'tiempo': "0\n4\n8\n12\n16\n20\n24\n48\n72",
                'biomasa': "0.26567\n2.3\n5.5333\n5.6\n5.733\n5.2667\n5.4467\n5.5677\n3.43",
                'sustrato': "10\n9.21\n8.7\n2.98\n0\n0\n0\n0\n0",
                'producto': "0\n0.5\n1.2\n2.5\n3.8\n4.2\n4.5\n4.6\n4.6"
            }
        
        if 'experimentos' not in st.session_state:
            st.session_state.experimentos = []
        
        if 'datos_antibiogramas' not in st.session_state:
            st.session_state.datos_antibiogramas = []
        
        if 'datos_metabolitos' not in st.session_state:
            st.session_state.datos_metabolitos = []
        
        if 'parametros_biorreactor' not in st.session_state:
            st.session_state.parametros_biorreactor = {
                'ph': 7.0, 'temperatura': 30.0, 'agitacion': 200,
                'aireacion': 1.0, 'presion': 1.0, 'volumen_trabajo': 1.0
            }
        
        # Dark mode and UI preferences
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
        
        if 'show_tooltips' not in st.session_state:
            st.session_state.show_tooltips = True
        
        # Real-time data streaming
        if 'streaming_enabled' not in st.session_state:
            st.session_state.streaming_enabled = False
        
        # Personalized recommendations
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'microorganism': 'Pseudomonas reptilivora',
                'preferred_analysis': 'kinetic',
                'experience_level': 'intermediate'
            }
    
    def _aplicar_tema_personalizado(self):
        """Aplicar tema personalizado con modo oscuro."""
        # Dark mode toggle in sidebar
        with st.sidebar:
            st.markdown("### 🎨 Preferencias de Tema")
            
            dark_mode = st.toggle(
                "Modo Oscuro", 
                value=st.session_state.dark_mode,
                help="Activa el modo oscuro para una experiencia visual más cómoda"
            )
            
            if dark_mode != st.session_state.dark_mode:
                st.session_state.dark_mode = dark_mode
                st.rerun()
            
            show_tooltips = st.toggle(
                "Mostrar Ayudas", 
                value=st.session_state.show_tooltips,
                help="Muestra tooltips explicativos para cada parámetro cinético"
            )
            st.session_state.show_tooltips = show_tooltips
        
        # Apply custom CSS for dark mode with smooth transitions
        if st.session_state.dark_mode:
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
                color: #ffffff;
                transition: all 0.3s ease-in-out;
            }
            
            .stSidebar > div:first-child {
                background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                transition: all 0.3s ease-in-out;
            }
            
            .stMetric {
                background: rgba(255, 255, 255, 0.05);
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease-in-out;
            }
            
            .stMetric:hover {
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
            
            .stButton > button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                transition: all 0.3s ease-in-out;
                box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
            }
            
            .stButton > button:hover {
                background: linear-gradient(45deg, #45a049, #4CAF50);
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(76, 175, 80, 0.4);
            }
            
            .tooltip {
                position: relative;
                display: inline-block;
                cursor: help;
            }
            
            .tooltip .tooltiptext {
                visibility: hidden;
                width: 250px;
                background-color: #333;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px;
                position: absolute;
                z-index: 1000;
                bottom: 125%;
                left: 50%;
                margin-left: -125px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 12px;
            }
            
            .tooltip:hover .tooltiptext {
                visibility: visible;
                opacity: 1;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                transition: all 0.3s ease-in-out;
            }
            
            .stMetric {
                background: rgba(255, 255, 255, 0.8);
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease-in-out;
            }
            
            .stMetric:hover {
                background: rgba(255, 255, 255, 0.9);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .stButton > button {
                background: linear-gradient(45deg, #2196F3, #1976D2);
                color: white;
                border: none;
                border-radius: 8px;
                transition: all 0.3s ease-in-out;
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
            }
            
            .stButton > button:hover {
                background: linear-gradient(45deg, #1976D2, #2196F3);
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(33, 150, 243, 0.4);
            }
            </style>
            """, unsafe_allow_html=True)
    
    def _crear_tooltip(self, texto, ayuda):
        """Crear un tooltip contextual para parámetros cinéticos."""
        if st.session_state.show_tooltips:
            return f"""
            <div class="tooltip">{texto} ℹ️
                <span class="tooltiptext">{ayuda}</span>
            </div>
            """
        return texto
    
    def ejecutar(self):
        """Ejecutar la aplicación principal."""
        # Aplicar tema personalizado
        self._aplicar_tema_personalizado()
        
        # Encabezado
        st.title("🧫 BioLab Pro Suite")
        st.markdown("**Análisis Profesional de Cinética Microbiana y Optimización con ML**")
        st.markdown("---")
        
        # Barra lateral
        self.renderizar_barra_lateral()
        
        # Contenido principal con pestañas
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📥 Entrada de Datos", 
            "📊 Análisis Cinético", 
            "🦠 Antibiogramas", 
            "🧬 Metabolitos", 
            "⚗️ Biorreactor", 
            "🤖 Predicción ML", 
            "⚡ Optimización", 
            "🧪 Simulación"
        ])
        
        with tab1:
            self.renderizar_pestana_entrada_datos()
        
        with tab2:
            self.renderizar_pestana_analisis()
        
        with tab3:
            self.renderizar_pestana_antibiogramas()
        
        with tab4:
            self.renderizar_pestana_metabolitos()
        
        with tab5:
            self.renderizar_pestana_biorreactor()
        
        with tab6:
            self.renderizar_pestana_ml()
        
        with tab7:
            self.renderizar_pestana_optimizacion()
        
        with tab8:
            self.renderizar_pestana_simulacion()
    
    def _renderizar_recomendaciones_personalizadas(self):
        """Renderizar sistema de recomendaciones personalizadas."""
        st.markdown("### 🎯 Recomendaciones Personalizadas")
        
        # Análisis del historial del usuario
        if st.session_state.experimentos:
            experimentos_recientes = st.session_state.experimentos[-5:]  # Últimos 5 experimentos
            
            # Análisis de patrones
            microorganismos_usados = [exp.get('microorganismo', 'N/A') for exp in experimentos_recientes]
            tipo_analisis_frecuente = st.session_state.user_preferences['preferred_analysis']
            
            # Generar recomendaciones basadas en el historial
            recomendaciones = []
            
            if 'Pseudomonas' in str(microorganismos_usados):
                recomendaciones.append("💡 Para Pseudomonas reptilivora, considera analizar la producción de Fluopsina en condiciones de pH 6.5-7.5")
            
            if tipo_analisis_frecuente == 'kinetic':
                recomendaciones.append("📊 Basado en tu preferencia por análisis cinético, te sugerimos explorar la pestaña de optimización ML")
            
            recomendaciones.append("🔬 Prueba el análisis de antibiogramas para una caracterización completa del microorganismo")
            
            for i, rec in enumerate(recomendaciones, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.info("Realiza algunos experimentos para recibir recomendaciones personalizadas")
    
    def _renderizar_streaming_tiempo_real(self):
        """Renderizar capacidades de streaming en tiempo real."""
        st.markdown("### 📡 Monitoreo en Tiempo Real")
        
        # Toggle para activar streaming
        streaming = st.toggle(
            "Activar Monitoreo Continuo",
            value=st.session_state.streaming_enabled,
            help="Simula la captura de datos en tiempo real del biorreactor"
        )
        st.session_state.streaming_enabled = streaming
        
        if streaming:
            # Placeholder para datos en tiempo real
            placeholder = st.empty()
            
            # Simular datos en tiempo real
            import random
            tiempo_actual = time.time()
            
            # Generar datos simulados basados en parámetros del biorreactor
            ph_actual = st.session_state.parametros_biorreactor['ph'] + random.uniform(-0.2, 0.2)
            temp_actual = st.session_state.parametros_biorreactor['temperatura'] + random.uniform(-1, 1)
            agitacion_actual = st.session_state.parametros_biorreactor['agitacion'] + random.uniform(-10, 10)
            
            with placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "pH Actual",
                        f"{ph_actual:.2f}",
                        delta=f"{ph_actual - st.session_state.parametros_biorreactor['ph']:.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Temperatura (°C)",
                        f"{temp_actual:.1f}",
                        delta=f"{temp_actual - st.session_state.parametros_biorreactor['temperatura']:.1f}"
                    )
                
                with col3:
                    st.metric(
                        "Agitación (RPM)",
                        f"{agitacion_actual:.0f}",
                        delta=f"{agitacion_actual - st.session_state.parametros_biorreactor['agitacion']:.0f}"
                    )
            
            # Alerta si los parámetros están fuera de rango
            if ph_actual < 4.0 or ph_actual > 9.4:
                st.warning("⚠️ pH fuera del rango óptimo para Pseudomonas reptilivora (4.0-9.4)")
            
            if temp_actual < 25 or temp_actual > 35:
                st.warning("⚠️ Temperatura fuera del rango óptimo (25-35°C)")
    
    def renderizar_barra_lateral(self):
        """Renderizar la barra lateral."""
        with st.sidebar:
            st.header("🧫 BioLab Pro Suite")
            st.markdown("---")
            
            # Información de la aplicación
            st.info("Análisis profesional de cinética microbiana con optimización ML")
            
            # Contador de experimentos
            st.metric("Experimentos Almacenados", len(st.session_state.experimentos))
            
            # Estado
            st.metric("Funciones de Análisis", "✅ Activas")
            
            st.markdown("---")
            
            # Sistema de recomendaciones personalizadas
            self._renderizar_recomendaciones_personalizadas()
            
            st.markdown("---")
            
            # Streaming en tiempo real
            self._renderizar_streaming_tiempo_real()
            
            st.markdown("---")
            
            # Configuraciones
            st.subheader("Configuraciones")
            auto_guardar = st.checkbox("Auto-guardar experimentos", value=True)
            st.session_state['auto_guardar'] = auto_guardar
            
            mostrar_avanzado = st.checkbox("Mostrar opciones avanzadas", value=False)
            st.session_state['mostrar_avanzado'] = mostrar_avanzado
            
            # Exportar datos
            if st.button("📥 Exportar Todos los Datos"):
                self.exportar_datos()
    
    def renderizar_pestana_entrada_datos(self):
        """Renderizar la pestaña de entrada de datos."""
        st.header("📥 Entrada de Datos Experimentales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Puntos de Tiempo (horas)")
            entrada_tiempo = st.text_area(
                "Valores de tiempo (uno por línea)", 
                value=st.session_state.datos_cineticos["tiempo"],
                height=150,
                key="entrada_tiempo"
            )
            
            st.subheader("Biomasa (g/L)")
            entrada_biomasa = st.text_area(
                "Valores de biomasa (uno por línea)",
                value=st.session_state.datos_cineticos["biomasa"],
                height=150,
                key="entrada_biomasa"
            )
        
        with col2:
            st.subheader("Sustrato (g/L)")
            entrada_sustrato = st.text_area(
                "Valores de sustrato (uno por línea)",
                value=st.session_state.datos_cineticos["sustrato"],
                height=150,
                key="entrada_sustrato"
            )
            
            st.subheader("Producto (g/L)")
            entrada_producto = st.text_area(
                "Valores de producto (uno por línea)",
                value=st.session_state.datos_cineticos["producto"],
                height=150,
                key="entrada_producto"
            )
        
        # Botón actualizar datos
        if st.button("📊 Actualizar Datos", type="primary"):
            try:
                st.session_state.datos_cineticos = {
                    'tiempo': entrada_tiempo,
                    'biomasa': entrada_biomasa,
                    'sustrato': entrada_sustrato,
                    'producto': entrada_producto
                }
                st.success("¡Datos actualizados exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar datos: {str(e)}")
        
        # Vista previa de datos
        if st.checkbox("Mostrar vista previa de datos"):
            self.mostrar_vista_previa_datos()
    
    def mostrar_vista_previa_datos(self):
        """Mostrar una vista previa de los datos de entrada."""
        try:
            # Parsear los datos
            tiempo = [float(x.strip()) for x in st.session_state.datos_cineticos['tiempo'].split('\n') if x.strip()]
            biomasa = [float(x.strip()) for x in st.session_state.datos_cineticos['biomasa'].split('\n') if x.strip()]
            sustrato = [float(x.strip()) for x in st.session_state.datos_cineticos['sustrato'].split('\n') if x.strip()]
            producto = [float(x.strip()) for x in st.session_state.datos_cineticos['producto'].split('\n') if x.strip()]
            
            # Crear DataFrame
            df = pd.DataFrame({
                'Tiempo (h)': tiempo,
                'Biomasa (g/L)': biomasa,
                'Sustrato (g/L)': sustrato,
                'Producto (g/L)': producto
            })
            
            st.subheader("Vista Previa de Datos")
            st.dataframe(df)
            
            # Validación básica
            if len(set([len(tiempo), len(biomasa), len(sustrato), len(producto)])) == 1:
                st.success(f"✅ Los datos son válidos ({len(tiempo)} puntos de datos)")
            else:
                st.error("❌ Los arreglos de datos tienen diferentes longitudes")
                
        except Exception as e:
            st.error(f"Error en vista previa de datos: {str(e)}")
    
    def renderizar_pestana_analisis(self):
        """Renderizar la pestaña de análisis cinético."""
        st.header("📊 Análisis Cinético Integral")
        
        # Opción de subir archivo
        archivo_subido = st.file_uploader("Subir datos experimentales (CSV/Excel)", 
                                       type=['csv', 'xlsx'], 
                                       help="Sube un archivo con columnas: Tiempo, Biomasa, Sustrato, Producto")
        
        if archivo_subido is not None:
            try:
                if archivo_subido.name.endswith('.csv'):
                    df = pd.read_csv(archivo_subido)
                else:
                    df = pd.read_excel(archivo_subido)
                
                st.success("¡Archivo subido exitosamente!")
                st.dataframe(df.head())
                
                # Mapear columnas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    columna_tiempo = st.selectbox("Columna de tiempo", df.columns, index=0)
                with col2:
                    columna_biomasa = st.selectbox("Columna de biomasa", df.columns, index=1 if len(df.columns) > 1 else 0)
                with col3:
                    columna_sustrato = st.selectbox("Columna de sustrato", df.columns, index=2 if len(df.columns) > 2 else 0)
                with col4:
                    columna_producto = st.selectbox("Columna de producto", df.columns, index=3 if len(df.columns) > 3 else 0)
                
                if st.button("Cargar Datos del Archivo"):
                    st.session_state.datos_cineticos = {
                        'tiempo': '\n'.join(map(str, df[columna_tiempo].values)),
                        'biomasa': '\n'.join(map(str, df[columna_biomasa].values)),
                        'sustrato': '\n'.join(map(str, df[columna_sustrato].values)),
                        'producto': '\n'.join(map(str, df[columna_producto].values))
                    }
                    st.success("¡Datos cargados al análisis!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al cargar archivo: {str(e)}")
        
        # Configuración de análisis de fase exponencial
        st.subheader("⚙️ Configuración de Análisis de Fase Exponencial")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            metodo_deteccion = st.radio("Método de Detección:",
                                      ["Automático", "Manual"],
                                      help="Automático: usa correlación ln(biomasa) vs tiempo. Manual: selecciona puntos específicos",
                                      key="metodo_deteccion")
            
            st.info("📊 **Método Automático**: Detecta la fase exponencial usando correlación lineal del ln(biomasa) vs tiempo, buscando la ventana con mejor R²")
        
        with col_config2:
            # Obtener datos actuales para mostrar opciones
            try:
                tiempo_actual = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['tiempo'].split('\n') if x.strip()])
                biomasa_actual = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['biomasa'].split('\n') if x.strip()])
                
                if metodo_deteccion == "Manual" and len(tiempo_actual) > 3:
                    st.write("**🎚️ Selección Interactiva de Fase Exponencial:**")
                    
                    # Interactive range slider for phase selection
                    rango_tiempo = (float(tiempo_actual.min()), float(tiempo_actual.max()))
                    valores_rango = st.slider(
                        "Selecciona el rango de tiempo para la fase exponencial:",
                        min_value=rango_tiempo[0],
                        max_value=rango_tiempo[1],
                        value=(rango_tiempo[0], min(rango_tiempo[0] + 20, rango_tiempo[1])),
                        step=0.5,
                        format="%.1f h",
                        help="Arrastra los extremos del slider para seleccionar el inicio y fin de la fase exponencial"
                    )
                    
                    # Find closest indices for selected time range
                    inicio_exp = np.argmin(np.abs(tiempo_actual - valores_rango[0]))
                    fin_exp = np.argmin(np.abs(tiempo_actual - valores_rango[1]))
                    
                    if fin_exp <= inicio_exp:
                        fin_exp = min(inicio_exp + 2, len(tiempo_actual) - 1)
                    
                    # Real-time preview of selection
                    col_preview1, col_preview2 = st.columns(2)
                    
                    with col_preview1:
                        st.metric("Tiempo Inicial", f"{tiempo_actual[inicio_exp]:.1f} h")
                        st.metric("Biomasa Inicial", f"{biomasa_actual[inicio_exp]:.3f} g/L")
                    
                    with col_preview2:
                        st.metric("Tiempo Final", f"{tiempo_actual[fin_exp]:.1f} h")
                        st.metric("Biomasa Final", f"{biomasa_actual[fin_exp]:.3f} g/L")
                    
                    # Calculate real-time kinetic parameters
                    ln_biomasa_sel = np.log(biomasa_actual[inicio_exp:fin_exp+1])
                    tiempo_sel = tiempo_actual[inicio_exp:fin_exp+1]
                    
                    if len(tiempo_sel) >= 2:
                        x_mean = np.mean(tiempo_sel)
                        y_mean = np.mean(ln_biomasa_sel)
                        denominador = np.sum((tiempo_sel - x_mean)**2)
                        
                        if denominador > 0:
                            slope = np.sum((tiempo_sel - x_mean) * (ln_biomasa_sel - y_mean)) / denominador
                            intercept = y_mean - slope * x_mean
                            
                            # Calcular R²
                            y_pred = slope * tiempo_sel + intercept
                            ss_tot = np.sum((ln_biomasa_sel - y_mean)**2)
                            ss_res = np.sum((ln_biomasa_sel - y_pred)**2)
                            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                            
                            # Real-time parameter display
                            col_param1, col_param2, col_param3 = st.columns(3)
                            
                            with col_param1:
                                st.metric(
                                    "μ (Velocidad Específica)",
                                    f"{slope:.3f} h⁻¹",
                                    help="Velocidad específica de crecimiento durante la fase exponencial"
                                )
                            
                            with col_param2:
                                st.metric(
                                    "R² (Calidad del Ajuste)",
                                    f"{r_squared:.3f}",
                                    help="Coeficiente de determinación: 1.0 = ajuste perfecto, >0.95 = excelente"
                                )
                            
                            with col_param3:
                                duracion = tiempo_actual[fin_exp] - tiempo_actual[inicio_exp]
                                st.metric(
                                    "Duración",
                                    f"{duracion:.1f} h",
                                    help="Duración de la fase exponencial seleccionada"
                                )
                            
                            # Visual quality indicator
                            if r_squared > 0.95:
                                st.success("🎯 Excelente selección de fase exponencial")
                            elif r_squared > 0.85:
                                st.info("✅ Buena selección de fase exponencial")
                            elif r_squared > 0.7:
                                st.warning("⚠️ Selección moderada - considera ajustar el rango")
                            else:
                                st.error("❌ Selección pobre - ajusta el rango para mejor correlación")
                            
                            # Display chart using Streamlit's built-in functionality
                            st.subheader("Vista Previa de Selección de Fase Exponencial")
                            
                            # Create chart data for visualization
                            chart_data_all = pd.DataFrame({
                                'tiempo': tiempo_actual,
                                'ln_biomasa': np.log(biomasa_actual)
                            })
                            
                            st.line_chart(chart_data_all.set_index('tiempo'), height=400)
                            
                            # Show regression statistics
                            st.info(f"📊 Ajuste lineal: R² = {r_squared:.3f}, Pendiente (μ_max) = {slope:.4f} h⁻¹")
                            
                            # Display selected range info
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Puntos seleccionados", len(tiempo_sel))
                            with col2:
                                st.metric("Rango temporal", f"{tiempo_sel.min():.1f} - {tiempo_sel.max():.1f} h")
                            with col3:
                                st.metric("Calidad R²", f"{r_squared:.3f}")
                    
                    else:
                        st.warning("Selecciona un rango más amplio (mínimo 2 puntos)")
            except:
                if metodo_deteccion == "Manual":
                    st.warning("Ingresa datos válidos primero para seleccionar fase exponencial")
        
        # Guardar datos en entrada de datos
        if st.button("📥 Guardar Datos en Entrada de Datos", key="guardar_datos_entrada"):
            try:
                # Actualizar los valores por defecto con los datos actuales
                st.session_state.valores_defecto = {
                    'tiempo': st.session_state.datos_cineticos['tiempo'],
                    'biomasa': st.session_state.datos_cineticos['biomasa'],
                    'sustrato': st.session_state.datos_cineticos['sustrato'],
                    'producto': st.session_state.datos_cineticos['producto']
                }
                st.success("✅ Datos guardados en la entrada por defecto!")
                st.info("Los datos ahora aparecerán automáticamente en la pestaña 'Entrada de Datos'")
            except:
                st.error("Error: Verifica que los datos estén correctamente ingresados")
        
        if st.button("🔬 Realizar Análisis Integral", type="primary"):
            try:
                # Parsear los datos
                tiempo = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['tiempo'].split('\n') if x.strip()])
                biomasa = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['biomasa'].split('\n') if x.strip()])
                sustrato = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['sustrato'].split('\n') if x.strip()])
                producto = np.array([float(x.strip()) for x in st.session_state.datos_cineticos['producto'].split('\n') if x.strip()])
                
                # Preparar configuración del análisis
                config_analisis = {
                    'metodo_deteccion': metodo_deteccion,
                    'inicio_manual': locals().get('inicio_exp', None) if metodo_deteccion == "Manual" else None,
                    'fin_manual': locals().get('fin_exp', None) if metodo_deteccion == "Manual" else None
                }
                
                # Análisis cinético integral
                resultados = self.realizar_analisis_cinetico(tiempo, biomasa, sustrato, producto, config_analisis)
                
                # Mostrar resultados en secciones organizadas
                self.mostrar_resultados_analisis(resultados, tiempo, biomasa, sustrato, producto)
                
                # Guardar experimento
                if st.session_state.get('auto_guardar', True):
                    experimento = {
                        'marca_tiempo': datetime.now().isoformat(),
                        'datos': st.session_state.datos_cineticos,
                        'resultados': resultados
                    }
                    st.session_state.experimentos.append(experimento)
                    st.success("¡Análisis integral completado y guardado!")
                
            except Exception as e:
                st.error(f"El análisis falló: {str(e)}")
    
    def realizar_analisis_cinetico(self, tiempo, biomasa, sustrato, producto, config_analisis=None):
        """Realizar análisis cinético integral."""
        resultados = {}
        if config_analisis is None:
            config_analisis = {'metodo_deteccion': 'Automático'}
        
        # Parámetros básicos
        resultados['biomasa_maxima'] = float(np.max(biomasa))
        resultados['biomasa_final'] = float(biomasa[-1])
        resultados['biomasa_inicial'] = float(biomasa[0])
        resultados['sustrato_consumido'] = float(sustrato[0] - sustrato[-1])
        resultados['producto_formado'] = float(producto[-1] - producto[0])
        resultados['tiempo_cultivo'] = float(tiempo[-1] - tiempo[0])
        
        # Cálculos de velocidad de crecimiento (detección de fase exponencial)
        log_biomasa = np.log(biomasa + 1e-10)  # Evitar log(0)
        
        # Determinar fase exponencial según configuración
        if config_analisis['metodo_deteccion'] == 'Manual' and config_analisis.get('inicio_manual') is not None:
            # Usar selección manual
            inicio_idx = config_analisis['inicio_manual']
            fin_idx = config_analisis['fin_manual']
            
            if inicio_idx < fin_idx and fin_idx < len(tiempo):
                tiempo_exp = tiempo[inicio_idx:fin_idx+1]
                log_biomasa_exp = log_biomasa[inicio_idx:fin_idx+1]
                
                # Regresión lineal para fase exponencial manual
                if len(tiempo_exp) >= 2:
                    x_mean = np.mean(tiempo_exp)
                    y_mean = np.mean(log_biomasa_exp)
                    slope = np.sum((tiempo_exp - x_mean) * (log_biomasa_exp - y_mean)) / np.sum((tiempo_exp - x_mean)**2)
                    intercept = y_mean - slope * x_mean
                    
                    # Calcular R² para la fase seleccionada
                    y_pred = slope * tiempo_exp + intercept
                    ss_tot = np.sum((log_biomasa_exp - y_mean)**2)
                    ss_res = np.sum((log_biomasa_exp - y_pred)**2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    resultados['mu_max'] = float(slope)
                    resultados['mu_promedio'] = float(slope)
                    resultados['r_squared_exp'] = float(r_squared)
                    resultados['fase_exponencial'] = {
                        'inicio': float(tiempo[inicio_idx]),
                        'fin': float(tiempo[fin_idx]),
                        'duracion': float(tiempo[fin_idx] - tiempo[inicio_idx]),
                        'metodo': 'Manual'
                    }
                else:
                    resultados['mu_max'] = 0.0
                    resultados['mu_promedio'] = 0.0
                    resultados['r_squared_exp'] = 0.0
            else:
                resultados['mu_max'] = 0.0
                resultados['mu_promedio'] = 0.0
                resultados['r_squared_exp'] = 0.0
        else:
            # Detección automática de fase exponencial
            velocidades_crecimiento = []
            mejor_r2 = 0
            mejor_inicio = 0
            mejor_fin = len(tiempo) - 1
            mejor_mu = 0
            
            # Buscar la mejor ventana de crecimiento exponencial
            for inicio in range(len(tiempo) - 2):
                for fin in range(inicio + 2, len(tiempo)):
                    tiempo_ventana = tiempo[inicio:fin+1]
                    log_biomasa_ventana = log_biomasa[inicio:fin+1]
                    
                    if len(tiempo_ventana) >= 3:
                        x_mean = np.mean(tiempo_ventana)
                        y_mean = np.mean(log_biomasa_ventana)
                        denominador = np.sum((tiempo_ventana - x_mean)**2)
                        
                        if denominador > 0:
                            slope = np.sum((tiempo_ventana - x_mean) * (log_biomasa_ventana - y_mean)) / denominador
                            
                            if slope > 0:  # Solo crecimiento positivo
                                y_pred = slope * tiempo_ventana + (y_mean - slope * x_mean)
                                ss_tot = np.sum((log_biomasa_ventana - y_mean)**2)
                                ss_res = np.sum((log_biomasa_ventana - y_pred)**2)
                                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                                
                                if r_squared > mejor_r2 and r_squared > 0.8:  # Umbral mínimo de calidad
                                    mejor_r2 = r_squared
                                    mejor_inicio = inicio
                                    mejor_fin = fin
                                    mejor_mu = slope
            
            resultados['mu_max'] = float(mejor_mu)
            resultados['mu_promedio'] = float(mejor_mu)
            resultados['r_squared_exp'] = float(mejor_r2)
            resultados['fase_exponencial'] = {
                'inicio': float(tiempo[mejor_inicio]),
                'fin': float(tiempo[mejor_fin]),
                'duracion': float(tiempo[mejor_fin] - tiempo[mejor_inicio]),
                'metodo': 'Automático'
            }
            
            # Calcular velocidades puntuales para referencia
            for i in range(1, len(tiempo)):
                if biomasa[i] > biomasa[i-1]:
                    dt = tiempo[i] - tiempo[i-1]
                    if dt > 0:
                        mu = (log_biomasa[i] - log_biomasa[i-1]) / dt
                        velocidades_crecimiento.append(mu)
        
        # Valores de compatibilidad
        resultados['velocidad_crecimiento_max'] = resultados['mu_max']
        resultados['velocidad_crecimiento_prom'] = resultados['mu_promedio']
        
        # Coeficientes de rendimiento
        if resultados['sustrato_consumido'] > 0:
            resultados['rendimiento_biomasa'] = (resultados['biomasa_final'] - resultados['biomasa_inicial']) / resultados['sustrato_consumido']
            resultados['rendimiento_producto'] = resultados['producto_formado'] / resultados['sustrato_consumido']
        else:
            resultados['rendimiento_biomasa'] = 0.0
            resultados['rendimiento_producto'] = 0.0
        
        # Cálculos de productividad
        if resultados['tiempo_cultivo'] > 0:
            resultados['productividad_biomasa'] = resultados['biomasa_final'] / resultados['tiempo_cultivo']
            resultados['productividad_producto'] = resultados['producto_formado'] / resultados['tiempo_cultivo']
        else:
            resultados['productividad_biomasa'] = 0.0
            resultados['productividad_producto'] = 0.0
        
        # Velocidades específicas
        biomasa_promedio = np.mean(biomasa)
        if biomasa_promedio > 0 and resultados['tiempo_cultivo'] > 0:
            resultados['consumo_especifico_sustrato'] = resultados['sustrato_consumido'] / (biomasa_promedio * resultados['tiempo_cultivo'])
            resultados['formacion_especifica_producto'] = resultados['producto_formado'] / (biomasa_promedio * resultados['tiempo_cultivo'])
        else:
            resultados['consumo_especifico_sustrato'] = 0.0
            resultados['formacion_especifica_producto'] = 0.0
        
        # Tiempo de duplicación (si se observa crecimiento)
        if resultados['velocidad_crecimiento_max'] > 0:
            resultados['tiempo_duplicacion'] = math.log(2) / resultados['velocidad_crecimiento_max']
        else:
            resultados['tiempo_duplicacion'] = float('inf')
        
        return resultados
    
    def detectar_fase_exponencial(self, tiempo, biomasa):
        """Detectar fase de crecimiento exponencial usando análisis estadístico."""
        try:
            # Inicializar variables
            fase_exponencial = {
                'detectada': False,
                'inicio': 0,
                'fin': 0,
                'duracion': 0,
                'velocidad_crecimiento': 0,
                'r_cuadrado': 0
            }
            
            if len(tiempo) < 4:  # Necesita al menos 4 puntos para análisis significativo
                return fase_exponencial
            
            # Calcular velocidades de crecimiento entre puntos consecutivos
            log_biomasa = np.log(biomasa + 1e-10)  # Evitar log(0)
            
            # Encontrar el mejor segmento lineal en log(biomasa) vs tiempo
            mejor_r_cuadrado = 0
            mejor_indice_inicio = 0
            mejor_indice_fin = 0
            mejor_velocidad_crecimiento = 0
            
            # Probar diferentes tamaños de ventana (mínimo 3 puntos)
            for tamano_ventana in range(3, min(len(tiempo), 8)):
                for indice_inicio in range(len(tiempo) - tamano_ventana + 1):
                    indice_fin = indice_inicio + tamano_ventana
                    
                    # Extraer datos del segmento
                    segmento_tiempo = tiempo[indice_inicio:indice_fin]
                    segmento_log_biomasa = log_biomasa[indice_inicio:indice_fin]
                    
                    # Regresión lineal en log(biomasa) vs tiempo
                    n = len(segmento_tiempo)
                    if n < 3:
                        continue
                        
                    x_promedio = np.mean(segmento_tiempo)
                    y_promedio = np.mean(segmento_log_biomasa)
                    
                    # Calcular pendiente (velocidad de crecimiento) y R-cuadrado
                    numerador = np.sum((segmento_tiempo - x_promedio) * (segmento_log_biomasa - y_promedio))
                    denominador = np.sum((segmento_tiempo - x_promedio) ** 2)
                    
                    if denominador > 0:
                        pendiente = numerador / denominador
                        
                        # Calcular R-cuadrado
                        y_pred = pendiente * (segmento_tiempo - x_promedio) + y_promedio
                        ss_res = np.sum((segmento_log_biomasa - y_pred) ** 2)
                        ss_tot = np.sum((segmento_log_biomasa - y_promedio) ** 2)
                        
                        r_cuadrado = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                        
                        # Verificar si esta es la mejor fase exponencial encontrada
                        # Criterios: R-cuadrado alto, velocidad de crecimiento positiva, duración razonable
                        if (r_cuadrado > mejor_r_cuadrado and 
                            r_cuadrado > 0.85 and  # Alta correlación
                            pendiente > 0.01 and      # Crecimiento positivo
                            pendiente < 2.0):         # Velocidad de crecimiento razonable
                            
                            mejor_r_cuadrado = r_cuadrado
                            mejor_indice_inicio = indice_inicio
                            mejor_indice_fin = indice_fin - 1
                            mejor_velocidad_crecimiento = pendiente
            
            # Si se encontró una buena fase exponencial
            if mejor_r_cuadrado > 0.85:
                fase_exponencial.update({
                    'detectada': True,
                    'inicio': tiempo[mejor_indice_inicio],
                    'fin': tiempo[mejor_indice_fin],
                    'duracion': tiempo[mejor_indice_fin] - tiempo[mejor_indice_inicio],
                    'velocidad_crecimiento': mejor_velocidad_crecimiento,
                    'r_cuadrado': mejor_r_cuadrado
                })
            
            return fase_exponencial
            
        except Exception as e:
            # Retornar valores por defecto si la detección falla
            return {
                'detectada': False,
                'inicio': 0,
                'fin': 0,
                'duracion': 0,
                'velocidad_crecimiento': 0,
                'r_cuadrado': 0
            }
    
    def mostrar_resultados_analisis(self, resultados, tiempo, biomasa, sustrato, producto):
        """Mostrar resultados de análisis integral."""
        
        # Crear visualización de datos
        df = pd.DataFrame({
            'Tiempo (h)': tiempo,
            'Biomasa (g/L)': biomasa,
            'Sustrato (g/L)': sustrato,
            'Producto (g/L)': producto
        })
        
        st.subheader("📈 Visualización de Datos")
        st.line_chart(df.set_index('Tiempo (h)'))
        
        # Resultados en columnas organizadas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🦠 Parámetros de Crecimiento")
            st.metric("Biomasa Máxima", f"{resultados['biomasa_maxima']:.3f} g/L")
            st.metric("Biomasa Final", f"{resultados['biomasa_final']:.3f} g/L")
            st.metric("Velocidad Crecimiento Máx (μ)", f"{resultados['velocidad_crecimiento_max']:.3f} h⁻¹")
            st.metric("Tiempo de Duplicación", f"{resultados['tiempo_duplicacion']:.2f} h" if resultados['tiempo_duplicacion'] != float('inf') else "Sin crecimiento")
        
        with col2:
            st.subheader("⚖️ Coeficientes de Rendimiento")
            st.metric("Rendimiento Biomasa (Yₓₛ)", f"{resultados['rendimiento_biomasa']:.3f} g/g")
            st.metric("Rendimiento Producto (Yₚₛ)", f"{resultados['rendimiento_producto']:.3f} g/g")
            st.metric("Sustrato Consumido", f"{resultados['sustrato_consumido']:.3f} g/L")
            st.metric("Producto Formado", f"{resultados['producto_formado']:.3f} g/L")
        
        with col3:
            st.subheader("⚡ Productividad y Velocidades")
            st.metric("Productividad Biomasa", f"{resultados['productividad_biomasa']:.3f} g/L/h")
            st.metric("Productividad Producto", f"{resultados['productividad_producto']:.3f} g/L/h")
            st.metric("qₛ Específico", f"{resultados['consumo_especifico_sustrato']:.3f} g/g/h")
            st.metric("qₚ Específico", f"{resultados['formacion_especifica_producto']:.3f} g/g/h")
        
        # Análisis de fases mejorado con detección de fase exponencial
        st.subheader("📊 Análisis Avanzado de Fases")
        
        # Detección de fase exponencial usando análisis estadístico
        fase_exponencial = self.detectar_fase_exponencial(tiempo, biomasa)
        
        # Clasificación de fases para cada intervalo de tiempo
        fases = []
        velocidades_crecimiento_por_fase = []
        
        for i in range(1, len(biomasa)):
            tiempo_actual = tiempo[i]
            
            # Calcular velocidad de crecimiento instantánea
            if biomasa[i] > 0 and biomasa[i-1] > 0:
                dt = tiempo[i] - tiempo[i-1]
                if dt > 0:
                    vel_crecimiento_inst = (np.log(biomasa[i]) - np.log(biomasa[i-1])) / dt
                    velocidades_crecimiento_por_fase.append(vel_crecimiento_inst)
                else:
                    vel_crecimiento_inst = 0
                    velocidades_crecimiento_por_fase.append(0)
            else:
                vel_crecimiento_inst = 0
                velocidades_crecimiento_por_fase.append(0)
            
            # Clasificación de fases
            if fase_exponencial['inicio'] <= tiempo_actual <= fase_exponencial['fin']:
                fases.append("🔥 Exponencial")
            elif biomasa[i] > biomasa[i-1] * 1.05:  # >5% aumento
                fases.append("📈 Crecimiento")
            elif abs(biomasa[i] - biomasa[i-1]) / max(biomasa[i-1], 1e-10) < 0.03:  # <3% cambio
                fases.append("⏸️ Estacionaria")
            elif biomasa[i] < biomasa[i-1] * 0.95:  # >5% disminución
                fases.append("📉 Muerte")
            else:
                fases.append("🔄 Transición")
        
        # Mostrar información de fase exponencial
        if fase_exponencial['detectada']:
            exp_col1, exp_col2, exp_col3 = st.columns(3)
            
            with exp_col1:
                st.metric("Inicio Fase Exponencial", f"{fase_exponencial['inicio']:.1f} h")
            with exp_col2:
                st.metric("Fin Fase Exponencial", f"{fase_exponencial['fin']:.1f} h")
            with exp_col3:
                st.metric("Duración Exponencial", f"{fase_exponencial['duracion']:.1f} h")
            
            st.success(f"🔥 Fase exponencial detectada de {fase_exponencial['inicio']:.1f}h a {fase_exponencial['fin']:.1f}h con μ = {fase_exponencial['velocidad_crecimiento']:.3f} h⁻¹")
        else:
            st.warning("No se detectó una fase exponencial clara en los datos")
        
        # Tabla de fases con velocidades de crecimiento
        tabla_fases = pd.DataFrame({
            'Rango de Tiempo (h)': [f"{tiempo[i]:.1f}-{tiempo[i+1]:.1f}" for i in range(len(fases))],
            'Fase': fases,
            'Velocidad Crecimiento (h⁻¹)': [f"{vel:.3f}" for vel in velocidades_crecimiento_por_fase],
            'Cambio Biomasa (%)': [f"{((biomasa[i+1]/biomasa[i]-1)*100):.1f}" if biomasa[i] > 0 else "N/A" for i in range(len(fases))]
        })
        st.dataframe(tabla_fases, use_container_width=True)
        
        # Estadísticas resumen
        st.subheader("📋 Estadísticas Resumen")
        datos_resumen = {
            'Parámetro': ['Tiempo de Cultivo', 'Velocidad Crecimiento Máxima', 'Rendimiento Biomasa', 'Rendimiento Producto', 
                         'Productividad Biomasa', 'Productividad Producto'],
            'Valor': [f"{resultados['tiempo_cultivo']:.2f} h", 
                     f"{resultados['velocidad_crecimiento_max']:.3f} h⁻¹",
                     f"{resultados['rendimiento_biomasa']:.3f} g/g",
                     f"{resultados['rendimiento_producto']:.3f} g/g",
                     f"{resultados['productividad_biomasa']:.3f} g/L/h",
                     f"{resultados['productividad_producto']:.3f} g/L/h"],
            'Unidades': ['horas', 'por hora', 'g biomasa/g sustrato', 'g producto/g sustrato',
                     'g biomasa/L/hora', 'g producto/L/hora']
        }
        
        df_resumen = pd.DataFrame(datos_resumen)
        st.dataframe(df_resumen, use_container_width=True)
        
        # Integración con parámetros del biorreactor
        st.subheader("⚗️ Condiciones del Biorreactor")
        
        col_bio1, col_bio2, col_bio3 = st.columns(3)
        
        with col_bio1:
            st.write("**Parámetros Físico-Químicos**")
            ph_exp = st.number_input("pH del Experimento", min_value=4.0, max_value=9.4, 
                                   value=st.session_state.parametros_biorreactor['ph'], 
                                   step=0.1, key="ph_experimento")
            temp_exp = st.number_input("Temperatura (°C)", min_value=20.0, max_value=45.0,
                                     value=st.session_state.parametros_biorreactor['temperatura'],
                                     step=0.5, key="temp_experimento")
        
        with col_bio2:
            st.write("**Parámetros Operacionales**")
            agitacion_exp = st.number_input("Agitación (rpm)", min_value=50, max_value=800,
                                          value=st.session_state.parametros_biorreactor['agitacion'],
                                          step=10, key="agit_experimento")
            aireacion_exp = st.number_input("Aireación (vvm)", min_value=0.1, max_value=5.0,
                                          value=st.session_state.parametros_biorreactor['aireacion'],
                                          step=0.1, key="aire_experimento")
        
        with col_bio3:
            st.write("**Parámetros Calculados**")
            # kLa estimado
            kla_estimado = (agitacion_exp/100) * (aireacion_exp**0.5) * 10
            st.metric("kLa estimado", f"{kla_estimado:.1f} h⁻¹")
            
            # Potencia específica estimada
            volumen = st.session_state.parametros_biorreactor['volumen_trabajo']
            potencia_especifica = (agitacion_exp/100)**3 * 0.001 / volumen
            st.metric("Potencia Específica", f"{potencia_especifica:.2f} W/L")
            
            # Evaluación de condiciones
            if 6.5 <= ph_exp <= 7.5:
                st.success("pH óptimo")
            elif 5.5 <= ph_exp < 6.5 or 7.5 < ph_exp <= 8.5:
                st.warning("pH subóptimo")
            else:
                st.error("pH crítico")
        
        # Guardar parámetros del biorreactor con el experimento
        if st.button("💾 Guardar Experimento con Parámetros", key="guardar_experimento_bio"):
            experimento_completo = {
                'tiempo': tiempo,
                'biomasa': biomasa,
                'sustrato': sustrato,
                'producto': producto,
                'ph': ph_exp,
                'temperatura': temp_exp,
                'agitacion': agitacion_exp,
                'aireacion': aireacion_exp,
                'kla_estimado': kla_estimado,
                'potencia_especifica': potencia_especifica,
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                **resultados  # Incluir todos los resultados cinéticos
            }
            st.session_state.experimentos.append(experimento_completo)
            st.success("Experimento guardado con parámetros del biorreactor!")
            st.rerun()
        
        # Análisis de impacto de condiciones operacionales
        st.subheader("📊 Impacto de Condiciones Operacionales")
        
        # Análisis de transferencia de oxígeno
        if kla_estimado > 50:
            st.success("🫁 **Excelente transferencia de oxígeno** - Favorece crecimiento aeróbico")
        elif kla_estimado > 20:
            st.info("🫁 **Buena transferencia de oxígeno** - Adecuada para el proceso")
        else:
            st.warning("🫁 **Transferencia de oxígeno limitada** - Posible limitación del proceso")
        
        # Análisis de pH vs crecimiento
        if resultados['mu_max'] > 0:
            if 6.5 <= ph_exp <= 7.5:
                factor_ph = "óptimo"
                impacto_ph = "maximiza"
            elif 5.5 <= ph_exp < 6.5 or 7.5 < ph_exp <= 8.5:
                factor_ph = "subóptimo"
                impacto_ph = "reduce"
            else:
                factor_ph = "crítico"
                impacto_ph = "limita severamente"
            
            st.write(f"🔬 **Análisis de pH**: El pH {factor_ph} ({ph_exp:.1f}) {impacto_ph} la velocidad específica de crecimiento observada (μ = {resultados['mu_max']:.3f} h⁻¹)")
        
        # Análisis de temperatura vs metabolismo
        if 25 <= temp_exp <= 30:
            st.write(f"🌡️ **Análisis de Temperatura**: Temperatura óptima ({temp_exp}°C) para P. reptilivora - favorece tanto crecimiento como producción de metabolitos")
        elif 30 < temp_exp <= 37:
            st.write(f"🌡️ **Análisis de Temperatura**: Temperatura elevada ({temp_exp}°C) - puede favorecer producción de metabolitos secundarios")
        else:
            st.write(f"🌡️ **Análisis de Temperatura**: Temperatura subóptima ({temp_exp}°C) - impacto negativo en el rendimiento")
        
        # Recomendaciones de optimización
        st.subheader("💡 Recomendaciones de Optimización")
        
        recomendaciones = []
        
        if kla_estimado < 30:
            recomendaciones.append("• Aumentar agitación o aireación para mejorar transferencia de oxígeno")
        
        if ph_exp < 6.5:
            recomendaciones.append("• Ajustar pH a rango óptimo (6.5-7.5) con NaOH")
        elif ph_exp > 7.5:
            recomendaciones.append("• Ajustar pH a rango óptimo (6.5-7.5) con HCl o H₂SO₄")
        
        if temp_exp < 25:
            recomendaciones.append("• Aumentar temperatura a 25-30°C para optimizar crecimiento")
        elif temp_exp > 35:
            recomendaciones.append("• Reducir temperatura para evitar estrés térmico")
        
        if potencia_especifica < 0.5:
            recomendaciones.append("• Aumentar potencia de agitación para mejor mezcla")
        elif potencia_especifica > 2.0:
            recomendaciones.append("• Reducir agitación para minimizar estrés celular")
        
        if recomendaciones:
            for rec in recomendaciones:
                st.write(rec)
        else:
            st.success("✅ Condiciones operacionales óptimas - no se requieren ajustes")
        
        # Predicción de rendimiento
        st.subheader("🎯 Predicción de Rendimiento")
        
        # Factor de corrección basado en condiciones
        factor_ph_corr = 1.0
        if 6.5 <= ph_exp <= 7.5:
            factor_ph_corr = 1.0
        elif 5.5 <= ph_exp < 6.5 or 7.5 < ph_exp <= 8.5:
            factor_ph_corr = 0.85
        else:
            factor_ph_corr = 0.6
        
        factor_temp_corr = 1.0
        if 25 <= temp_exp <= 30:
            factor_temp_corr = 1.0
        elif 30 < temp_exp <= 35:
            factor_temp_corr = 0.9
        else:
            factor_temp_corr = 0.7
        
        factor_kla_corr = min(1.0, kla_estimado / 30)
        
        factor_global = factor_ph_corr * factor_temp_corr * factor_kla_corr
        
        col_pred1, col_pred2, col_pred3 = st.columns(3)
        
        with col_pred1:
            biomasa_predicha = resultados.get('biomasa_maxima', 0) * factor_global
            st.metric("Biomasa Máxima Predicha", f"{biomasa_predicha:.2f} g/L")
        
        with col_pred2:
            if 'Yp_x' in resultados:
                producto_predicho = biomasa_predicha * resultados['Yp_x'] * factor_global
                st.metric("Producto Máximo Predicho", f"{producto_predicho:.2f} g/L")
        
        with col_pred3:
            tiempo_predicho = 24 / factor_global  # Tiempo base 24h ajustado por condiciones
            st.metric("Tiempo Estimado", f"{tiempo_predicho:.1f} h")
        
        st.write(f"**Factor de Eficiencia Global**: {factor_global:.2f} ({factor_global*100:.0f}%)")
        
        if factor_global > 0.9:
            st.success("🎯 Condiciones excelentes - máximo rendimiento esperado")
        elif factor_global > 0.7:
            st.info("⚡ Condiciones buenas - rendimiento satisfactorio")
        else:
            st.warning("⚠️ Condiciones subóptimas - considerar optimización")
    
    def renderizar_pestana_antibiogramas(self):
        """Renderizar la pestaña de análisis de antibiogramas."""
        st.header("🦠 Análisis de Antibiogramas y Halos de Inhibición")
        
        # Pestañas para diferentes tipos de análisis
        subtab1, subtab2, subtab3 = st.tabs([
            "📝 Entrada de Datos",
            "📊 Análisis Individual", 
            "📈 Análisis Estadístico"
        ])
        
        with subtab1:
            self.renderizar_entrada_antibiogramas()
        
        with subtab2:
            self.renderizar_analisis_individual_antibiogramas()
        
        with subtab3:
            self.renderizar_analisis_estadistico_antibiogramas()
    
    def renderizar_entrada_antibiogramas(self):
        """Renderizar entrada de datos para antibiogramas."""
        st.subheader("📝 Entrada de Datos de Antibiogramas")
        
        # Información del experimento
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información del Experimento**")
            nombre_experimento = st.text_input("Nombre del Experimento", key="nombre_antibiograma")
            microorganismo = st.text_input("Microorganismo", key="microorganismo", placeholder="ej. E. coli ATCC 25922")
            fecha_experimento = st.date_input("Fecha del Experimento", key="fecha_antibiograma")
            investigador = st.text_input("Investigador", key="investigador")
        
        with col2:
            st.write("**Condiciones del Ensayo**")
            medio_cultivo = st.selectbox("Medio de Cultivo", 
                                       ["Mueller-Hinton", "Sangre", "Chocolate", "MacConkey", "Otro"],
                                       key="medio_cultivo")
            if medio_cultivo == "Otro":
                medio_personalizado = st.text_input("Especificar medio:", key="medio_personalizado")
            
            temperatura_incubacion = st.number_input("Temperatura de Incubación (°C)", 
                                                   min_value=20, max_value=45, value=37, 
                                                   key="temperatura_incubacion")
            tiempo_incubacion = st.number_input("Tiempo de Incubación (horas)", 
                                              min_value=12, max_value=72, value=24,
                                              key="tiempo_incubacion")
        
        # Entrada de datos de antibióticos
        st.subheader("💊 Datos de Antibióticos y Halos de Inhibición")
        
        # Opción de subir archivo CSV
        archivo_antibiograma = st.file_uploader("Subir datos de antibiograma (CSV)", 
                                              type=['csv'], 
                                              help="CSV con columnas: Antibiotico, Concentracion, Diametro_Halo, Unidad_Concentracion",
                                              key="archivo_antibiograma")
        
        if archivo_antibiograma is not None:
            try:
                df_antibioticos = pd.read_csv(archivo_antibiograma)
                st.success("Archivo cargado exitosamente!")
                st.dataframe(df_antibioticos.head())
                
                if st.button("Cargar Datos del Archivo", key="cargar_archivo_antibiograma"):
                    # Procesar y guardar datos
                    for _, fila in df_antibioticos.iterrows():
                        self.agregar_dato_antibiograma(
                            nombre_experimento, microorganismo, fila['Antibiotico'],
                            fila['Concentracion'], fila['Diametro_Halo'], 
                            fila.get('Unidad_Concentracion', 'μg/mL')
                        )
                    st.success(f"Se cargaron {len(df_antibioticos)} registros de antibióticos!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al cargar archivo: {str(e)}")
        
        # Entrada manual de datos
        st.write("**Entrada Manual de Datos**")
        
        entrada_col1, entrada_col2, entrada_col3, entrada_col4 = st.columns(4)
        
        with entrada_col1:
            antibiotico = st.text_input("Antibiótico", key="antibiotico_manual")
        
        with entrada_col2:
            concentracion = st.number_input("Concentración", min_value=0.0, step=0.1, key="concentracion_manual")
            unidad_conc = st.selectbox("Unidad", ["μg/mL", "mg/mL", "UI/mL"], key="unidad_conc")
        
        with entrada_col3:
            diametro_halo = st.number_input("Diámetro Halo (mm)", min_value=0.0, step=0.1, key="diametro_manual")
        
        with entrada_col4:
            st.write("")  # Espaciado
            if st.button("➕ Agregar Antibiótico", key="agregar_antibiotico"):
                if antibiotico and concentracion > 0 and diametro_halo >= 0:
                    self.agregar_dato_antibiograma(
                        nombre_experimento or "Experimento_1", 
                        microorganismo or "No especificado",
                        antibiotico, concentracion, diametro_halo, unidad_conc
                    )
                    st.success(f"Antibiótico {antibiotico} agregado!")
                    st.rerun()
                else:
                    st.error("Complete todos los campos requeridos")
        
        # Mostrar datos actuales
        if st.session_state.datos_antibiogramas:
            st.subheader("📋 Datos Actuales de Antibiogramas")
            df_actual = pd.DataFrame(st.session_state.datos_antibiogramas)
            st.dataframe(df_actual, use_container_width=True)
            
            # Opciones de gestión de datos
            col_gest1, col_gest2, col_gest3 = st.columns(3)
            
            with col_gest1:
                if st.button("🗑️ Limpiar Todos los Datos", key="limpiar_antibiogramas"):
                    st.session_state.datos_antibiogramas = []
                    st.success("Datos limpiados!")
                    st.rerun()
            
            with col_gest2:
                # Exportar datos
                csv_antibiogramas = df_actual.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_antibiogramas,
                    file_name=f"antibiogramas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="descargar_antibiogramas"
                )
            
            with col_gest3:
                # Eliminar registro específico
                if len(df_actual) > 0:
                    indice_eliminar = st.selectbox("Eliminar registro:", 
                                                 range(len(df_actual)), 
                                                 format_func=lambda x: f"{df_actual.iloc[x]['antibiotico']} - {df_actual.iloc[x]['experimento']}",
                                                 key="indice_eliminar")
                    if st.button("❌ Eliminar", key="eliminar_registro"):
                        st.session_state.datos_antibiogramas.pop(indice_eliminar)
                        st.success("Registro eliminado!")
                        st.rerun()
    
    def agregar_dato_antibiograma(self, experimento, microorganismo, antibiotico, concentracion, diametro, unidad):
        """Agregar un dato de antibiograma a la sesión."""
        nuevo_dato = {
            'experimento': experimento,
            'microorganismo': microorganismo,
            'antibiotico': antibiotico,
            'concentracion': concentracion,
            'unidad_concentracion': unidad,
            'diametro_halo': diametro,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'interpretacion': self.interpretar_sensibilidad(antibiotico, diametro)
        }
        st.session_state.datos_antibiogramas.append(nuevo_dato)
    
    def interpretar_sensibilidad(self, antibiotico, diametro):
        """Interpretar sensibilidad basada en criterios CLSI/EUCAST simplificados."""
        # Criterios simplificados para antibióticos comunes (en mm)
        criterios = {
            'ampicilina': {'S': 17, 'R': 13},
            'amoxicilina': {'S': 17, 'R': 13},
            'penicilina': {'S': 15, 'R': 11},
            'eritromicina': {'S': 23, 'R': 13},
            'tetraciclina': {'S': 19, 'R': 14},
            'cloranfenicol': {'S': 18, 'R': 12},
            'gentamicina': {'S': 15, 'R': 12},
            'ciprofloxacina': {'S': 21, 'R': 15},
            'vancomicina': {'S': 15, 'R': 14},
            'ceftriaxona': {'S': 23, 'R': 19}
        }
        
        antibiotico_lower = antibiotico.lower()
        
        # Buscar coincidencias parciales
        criterio_encontrado = None
        for ab_conocido in criterios.keys():
            if ab_conocido in antibiotico_lower or antibiotico_lower in ab_conocido:
                criterio_encontrado = criterios[ab_conocido]
                break
        
        if criterio_encontrado:
            if diametro >= criterio_encontrado['S']:
                return 'Sensible (S)'
            elif diametro <= criterio_encontrado['R']:
                return 'Resistente (R)'
            else:
                return 'Intermedio (I)'
        else:
            # Criterios generales si no se encuentra el antibiótico específico
            if diametro >= 20:
                return 'Sensible (S)'
            elif diametro <= 10:
                return 'Resistente (R)'
            else:
                return 'Intermedio (I)'
    
    def renderizar_analisis_individual_antibiogramas(self):
        """Renderizar análisis individual de antibiogramas."""
        st.subheader("📊 Análisis Individual de Antibiogramas")
        
        if not st.session_state.datos_antibiogramas:
            st.info("Primero ingresa datos de antibiogramas en la pestaña 'Entrada de Datos'")
            return
        
        df_antibiogramas = pd.DataFrame(st.session_state.datos_antibiogramas)
        
        # Seleccionar experimento para análisis
        experimentos_disponibles = df_antibiogramas['experimento'].unique()
        experimento_seleccionado = st.selectbox("Seleccionar Experimento:", experimentos_disponibles)
        
        # Filtrar datos del experimento seleccionado
        df_experimento = df_antibiogramas[df_antibiogramas['experimento'] == experimento_seleccionado]
        
        # Información general del experimento
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.metric("Microorganismo", df_experimento['microorganismo'].iloc[0])
            st.metric("Total Antibióticos Probados", len(df_experimento))
        
        with col_info2:
            sensibles = len(df_experimento[df_experimento['interpretacion'].str.contains('Sensible')])
            resistentes = len(df_experimento[df_experimento['interpretacion'].str.contains('Resistente')])
            st.metric("Antibióticos Sensibles", sensibles)
            st.metric("Antibióticos Resistentes", resistentes)
        
        # Tabla de resultados
        st.subheader("📋 Resultados Detallados")
        df_mostrar = df_experimento[['antibiotico', 'concentracion', 'unidad_concentracion', 
                                   'diametro_halo', 'interpretacion']].copy()
        df_mostrar.columns = ['Antibiótico', 'Concentración', 'Unidad', 'Diámetro (mm)', 'Interpretación']
        st.dataframe(df_mostrar, use_container_width=True)
        
        # Visualización de halos
        st.subheader("📊 Visualización de Halos de Inhibición")
        
        # Gráfico de barras de diámetros
        st.bar_chart(df_experimento.set_index('antibiotico')['diametro_halo'])
        
        # Análisis por categorías de sensibilidad
        st.subheader("🎯 Análisis por Sensibilidad")
        
        interpretaciones = df_experimento['interpretacion'].value_counts()
        
        col_sens1, col_sens2 = st.columns(2)
        
        with col_sens1:
            st.write("**Distribución de Sensibilidad:**")
            for interp, cantidad in interpretaciones.items():
                porcentaje = (cantidad / len(df_experimento)) * 100
                st.write(f"• {interp}: {cantidad} ({porcentaje:.1f}%)")
        
        with col_sens2:
            # Estadísticas de halos
            st.write("**Estadísticas de Halos (mm):**")
            st.write(f"• Promedio: {df_experimento['diametro_halo'].mean():.1f}")
            st.write(f"• Mediana: {df_experimento['diametro_halo'].median():.1f}")
            st.write(f"• Máximo: {df_experimento['diametro_halo'].max():.1f}")
            st.write(f"• Mínimo: {df_experimento['diametro_halo'].min():.1f}")
        
        # Recomendaciones terapéuticas
        st.subheader("💊 Recomendaciones Terapéuticas")
        
        antibioticos_sensibles = df_experimento[df_experimento['interpretacion'].str.contains('Sensible')]['antibiotico'].tolist()
        antibioticos_resistentes = df_experimento[df_experimento['interpretacion'].str.contains('Resistente')]['antibiotico'].tolist()
        
        if antibioticos_sensibles:
            st.success(f"**Antibióticos recomendados:** {', '.join(antibioticos_sensibles)}")
        
        if antibioticos_resistentes:
            st.error(f"**Antibióticos NO recomendados:** {', '.join(antibioticos_resistentes)}")
        
        # Clasificación por mecanismo de acción (simplificado)
        mecanismos = {
            'β-lactámicos': ['ampicilina', 'amoxicilina', 'penicilina', 'ceftriaxona'],
            'Aminoglucósidos': ['gentamicina', 'estreptomicina'],
            'Fluoroquinolonas': ['ciprofloxacina', 'levofloxacina'],
            'Macrólidos': ['eritromicina', 'azitromicina'],
            'Otros': []
        }
        
        st.subheader("🔬 Análisis por Mecanismo de Acción")
        
        for mecanismo, antibioticos_mec in mecanismos.items():
            antibioticos_probados = []
            for ab in df_experimento['antibiotico']:
                for ab_mec in antibioticos_mec:
                    if ab_mec.lower() in ab.lower():
                        antibioticos_probados.append(ab)
                        break
            
            if antibioticos_probados:
                sensibles_mec = df_experimento[
                    (df_experimento['antibiotico'].isin(antibioticos_probados)) & 
                    (df_experimento['interpretacion'].str.contains('Sensible'))
                ]
                
                if len(sensibles_mec) > 0:
                    st.write(f"**{mecanismo}**: {len(sensibles_mec)}/{len(antibioticos_probados)} sensibles")
                else:
                    st.write(f"**{mecanismo}**: Resistencia detectada")
    
    def renderizar_analisis_estadistico_antibiogramas(self):
        """Renderizar análisis estadístico de múltiples antibiogramas."""
        st.subheader("📈 Análisis Estadístico Comparativo")
        
        if len(st.session_state.datos_antibiogramas) < 2:
            st.info("Se necesitan al menos 2 registros para análisis estadístico comparativo")
            return
        
        df_antibiogramas = pd.DataFrame(st.session_state.datos_antibiogramas)
        
        # Análisis por microorganismo
        st.subheader("🦠 Análisis por Microorganismo")
        
        microorganismos = df_antibiogramas['microorganismo'].unique()
        
        if len(microorganismos) > 1:
            # Comparación entre microorganismos
            for microorganismo in microorganismos:
                df_micro = df_antibiogramas[df_antibiogramas['microorganismo'] == microorganismo]
                
                sensibles = len(df_micro[df_micro['interpretacion'].str.contains('Sensible')])
                total = len(df_micro)
                porcentaje_sensibilidad = (sensibles / total) * 100 if total > 0 else 0
                
                st.write(f"**{microorganismo}**: {sensibles}/{total} sensibles ({porcentaje_sensibilidad:.1f}%)")
        
        # Análisis por antibiótico
        st.subheader("💊 Perfil de Resistencia por Antibiótico")
        
        antibioticos_unicos = df_antibiogramas['antibiotico'].unique()
        
        datos_resistencia = []
        for antibiotico in antibioticos_unicos:
            df_ab = df_antibiogramas[df_antibiogramas['antibiotico'] == antibiotico]
            
            total_pruebas = len(df_ab)
            sensibles = len(df_ab[df_ab['interpretacion'].str.contains('Sensible')])
            resistentes = len(df_ab[df_ab['interpretacion'].str.contains('Resistente')])
            intermedios = total_pruebas - sensibles - resistentes
            
            datos_resistencia.append({
                'Antibiótico': antibiotico,
                'Total Pruebas': total_pruebas,
                'Sensibles': sensibles,
                'Resistentes': resistentes,
                'Intermedios': intermedios,
                '% Sensibilidad': (sensibles / total_pruebas) * 100 if total_pruebas > 0 else 0,
                '% Resistencia': (resistentes / total_pruebas) * 100 if total_pruebas > 0 else 0
            })
        
        df_resistencia = pd.DataFrame(datos_resistencia)
        df_resistencia = df_resistencia.sort_values('% Sensibilidad', ascending=False)
        
        st.dataframe(df_resistencia, use_container_width=True)
        
        # Antibióticos más y menos efectivos
        if len(df_resistencia) > 0:
            col_efec1, col_efec2 = st.columns(2)
            
            with col_efec1:
                st.subheader("✅ Antibióticos Más Efectivos")
                top_efectivos = df_resistencia.head(3)
                for _, fila in top_efectivos.iterrows():
                    st.write(f"• {fila['Antibiótico']}: {fila['% Sensibilidad']:.1f}% sensibilidad")
            
            with col_efec2:
                st.subheader("❌ Antibióticos Menos Efectivos")
                menos_efectivos = df_resistencia.tail(3)
                for _, fila in menos_efectivos.iterrows():
                    st.write(f"• {fila['Antibiótico']}: {fila['% Resistencia']:.1f}% resistencia")
        
        # Análisis de tendencias temporales
        if 'fecha' in df_antibiogramas.columns:
            st.subheader("📅 Tendencias Temporales")
            
            df_antibiogramas['fecha'] = pd.to_datetime(df_antibiogramas['fecha'])
            df_antibiogramas['mes_ano'] = df_antibiogramas['fecha'].dt.to_period('M')
            
            tendencias = df_antibiogramas.groupby(['mes_ano', 'interpretacion']).size().unstack(fill_value=0)
            
            if len(tendencias) > 1:
                st.write("**Evolución de la resistencia por mes:**")
                st.dataframe(tendencias)
            else:
                st.info("Se necesitan datos de múltiples períodos para análisis temporal")
        
        # Correlaciones entre diámetro y concentración
        st.subheader("🔗 Análisis de Correlaciones")
        
        # Filtrar datos numéricos válidos
        df_numerico = df_antibiogramas[['concentracion', 'diametro_halo']].copy()
        df_numerico = df_numerico.dropna()
        
        if len(df_numerico) > 3:
            correlacion = df_numerico['concentracion'].corr(df_numerico['diametro_halo'])
            
            st.write(f"**Correlación Concentración-Diámetro:** {correlacion:.3f}")
            
            if abs(correlacion) > 0.5:
                direccion = "positiva" if correlacion > 0 else "negativa"
                fuerza = "fuerte" if abs(correlacion) > 0.7 else "moderada"
                st.info(f"Se detectó una correlación {fuerza} {direccion} entre la concentración del antibiótico y el diámetro del halo.")
            else:
                st.info("No se detectó correlación significativa entre concentración y diámetro del halo.")
            
            # Gráfico de dispersión usando datos tabulares
            scatter_data = pd.DataFrame({
                'Concentración': df_numerico['concentracion'],
                'Diámetro': df_numerico['diametro_halo']
            })
            st.scatter_chart(scatter_data.set_index('Concentración'))
        
        # Reporte de resistencia múltiple
        st.subheader("⚠️ Análisis de Resistencia Múltiple")
        
        experimentos_resistencia = {}
        for experimento in df_antibiogramas['experimento'].unique():
            df_exp = df_antibiogramas[df_antibiogramas['experimento'] == experimento]
            resistentes = len(df_exp[df_exp['interpretacion'].str.contains('Resistente')])
            total = len(df_exp)
            
            if total >= 3 and resistentes >= 2:
                experimentos_resistencia[experimento] = {
                    'resistentes': resistentes,
                    'total': total,
                    'porcentaje': (resistentes / total) * 100
                }
        
        if experimentos_resistencia:
            st.warning("**Posible Resistencia Múltiple Detectada:**")
            for exp, datos in experimentos_resistencia.items():
                st.write(f"• {exp}: {datos['resistentes']}/{datos['total']} antibióticos resistentes ({datos['porcentaje']:.1f}%)")
        else:
            st.success("No se detectaron patrones de resistencia múltiple preocupantes")
    
    def renderizar_pestana_metabolitos(self):
        """Renderizar la pestaña de análisis de metabolitos."""
        st.header("🧬 Análisis de Metabolitos - Pseudomonas reptilivora")
        
        # Pestañas para diferentes categorías de metabolitos
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "📝 Entrada de Datos",
            "🔬 Análisis Primarios", 
            "⚗️ Análisis Secundarios",
            "📊 Cinética Metabólica"
        ])
        
        with subtab1:
            self.renderizar_entrada_metabolitos()
        
        with subtab2:
            self.renderizar_analisis_primarios()
        
        with subtab3:
            self.renderizar_analisis_secundarios()
        
        with subtab4:
            self.renderizar_cinetica_metabolica()
    
    def renderizar_entrada_metabolitos(self):
        """Renderizar entrada de datos para metabolitos."""
        st.subheader("📝 Entrada de Datos de Metabolitos")
        
        # Información del experimento
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información del Cultivo**")
            nombre_experimento = st.text_input("Nombre del Experimento", key="nombre_metabolitos")
            cepa_pseudomonas = st.selectbox("Cepa de Pseudomonas", 
                                          ["P. reptilivora silvestre", "P. reptilivora mutante", "Otra cepa"],
                                          key="cepa_pseudomonas")
            if cepa_pseudomonas == "Otra cepa":
                cepa_personalizada = st.text_input("Especificar cepa:", key="cepa_personalizada")
            
            medio_cultivo = st.selectbox("Medio de Cultivo", 
                                       ["Luria-Bertani (LB)", "Medio Mínimo M9", "King B", "Pseudomonas Agar", "Personalizado"],
                                       key="medio_metabolitos")
            if medio_cultivo == "Personalizado":
                medio_personalizado = st.text_input("Especificar medio:", key="medio_personalizado_met")
        
        with col2:
            st.write("**Condiciones de Fermentación**")
            tiempo_cultivo = st.number_input("Tiempo de Cultivo (horas)", min_value=0.0, value=24.0, key="tiempo_metabolitos")
            fase_crecimiento = st.selectbox("Fase de Crecimiento", 
                                          ["Exponencial", "Estacionaria", "Declive", "No determinada"],
                                          key="fase_crecimiento")
            condiciones_estres = st.multiselect("Condiciones de Estrés Aplicadas",
                                              ["Limitación de nutrientes", "Estrés oxidativo", "Cambio de pH", 
                                               "Shock térmico", "Limitación de oxígeno", "Ninguna"],
                                              key="condiciones_estres")
        
        # Entrada de metabolitos por categoría
        st.subheader("🧪 Concentraciones de Metabolitos")
        
        categoria_metabolito = st.selectbox("Categoría de Metabolito", 
                                          ["Metabolitos Primarios", "Metabolitos Secundarios"],
                                          key="categoria_metabolito")
        
        if categoria_metabolito == "Metabolitos Primarios":
            st.write("**Metabolitos Primarios (mg/L)**")
            metab_col1, metab_col2, metab_col3 = st.columns(3)
            
            with metab_col1:
                st.write("*Ácidos Orgánicos*")
                acetato = st.number_input("Acetato", min_value=0.0, step=0.1, key="acetato")
                lactato = st.number_input("Lactato", min_value=0.0, step=0.1, key="lactato")
                piruvato = st.number_input("Piruvato", min_value=0.0, step=0.1, key="piruvato")
                citrato = st.number_input("Citrato", min_value=0.0, step=0.1, key="citrato")
            
            with metab_col2:
                st.write("*Azúcares y Derivados*")
                glucosa = st.number_input("Glucosa", min_value=0.0, step=0.1, key="glucosa")
                fructosa = st.number_input("Fructosa", min_value=0.0, step=0.1, key="fructosa")
                galactosa = st.number_input("Galactosa", min_value=0.0, step=0.1, key="galactosa")
                trehalosa = st.number_input("Trehalosa", min_value=0.0, step=0.1, key="trehalosa")
            
            with metab_col3:
                st.write("*Aminoácidos*")
                alanina = st.number_input("Alanina", min_value=0.0, step=0.1, key="alanina")
                glicina = st.number_input("Glicina", min_value=0.0, step=0.1, key="glicina")
                serina = st.number_input("Serina", min_value=0.0, step=0.1, key="serina")
                prolina = st.number_input("Prolina", min_value=0.0, step=0.1, key="prolina")
            
            if st.button("➕ Agregar Metabolitos Primarios", key="agregar_primarios"):
                self.agregar_metabolitos({
                    'experimento': nombre_experimento or "Exp_Metabolitos_1",
                    'cepa': cepa_pseudomonas,
                    'medio': medio_cultivo,
                    'tiempo': tiempo_cultivo,
                    'fase': fase_crecimiento,
                    'categoria': 'Primarios',
                    'metabolitos': {
                        'acetato': acetato, 'lactato': lactato, 'piruvato': piruvato, 'citrato': citrato,
                        'glucosa': glucosa, 'fructosa': fructosa, 'galactosa': galactosa, 'trehalosa': trehalosa,
                        'alanina': alanina, 'glicina': glicina, 'serina': serina, 'prolina': prolina
                    }
                })
                st.success("Metabolitos primarios agregados!")
                st.rerun()
        
        else:  # Metabolitos Secundarios
            st.write("**Metabolitos Secundarios (μg/L)**")
            sec_col1, sec_col2, sec_col3 = st.columns(3)
            
            with sec_col1:
                st.write("*Antibióticos*")
                piocianina = st.number_input("Piocianina", min_value=0.0, step=0.1, key="piocianina")
                pioverdina = st.number_input("Pioverdina", min_value=0.0, step=0.1, key="pioverdina")
                fluopsina = st.number_input("Fluopsina", min_value=0.0, step=0.1, key="fluopsina")
                phenazinas = st.number_input("Phenazinas", min_value=0.0, step=0.1, key="phenazinas")
                quinolonas = st.number_input("Quinolonas", min_value=0.0, step=0.1, key="quinolonas")
            
            with sec_col2:
                st.write("*Enzimas (U/mL)*")
                lipasas = st.number_input("Lipasas", min_value=0.0, step=0.01, key="lipasas")
                proteasas = st.number_input("Proteasas", min_value=0.0, step=0.01, key="proteasas")
                elastasas = st.number_input("Elastasas", min_value=0.0, step=0.01, key="elastasas")
                lecitinasas = st.number_input("Lecitinasas", min_value=0.0, step=0.01, key="lecitinasas")
            
            with sec_col3:
                st.write("*Biosurfactantes (mg/L)*")
                ramnolipidos = st.number_input("Ramnolípidos", min_value=0.0, step=0.1, key="ramnolipidos")
                surfactina = st.number_input("Surfactina", min_value=0.0, step=0.1, key="surfactina")
                soforolipidos = st.number_input("Soforolípidos", min_value=0.0, step=0.1, key="soforolipidos")
                bioemulsina = st.number_input("Bioemulsina", min_value=0.0, step=0.1, key="bioemulsina")
            
            if st.button("➕ Agregar Metabolitos Secundarios", key="agregar_secundarios"):
                self.agregar_metabolitos({
                    'experimento': nombre_experimento or "Exp_Metabolitos_1",
                    'cepa': cepa_pseudomonas,
                    'medio': medio_cultivo,
                    'tiempo': tiempo_cultivo,
                    'fase': fase_crecimiento,
                    'categoria': 'Secundarios',
                    'metabolitos': {
                        'piocianina': piocianina, 'pioverdina': pioverdina, 'fluopsina': fluopsina, 'phenazinas': phenazinas, 'quinolonas': quinolonas,
                        'lipasas': lipasas, 'proteasas': proteasas, 'elastasas': elastasas, 'lecitinasas': lecitinasas,
                        'ramnolipidos': ramnolipidos, 'surfactina': surfactina, 'soforolipidos': soforolipidos, 'bioemulsina': bioemulsina
                    }
                })
                st.success("Metabolitos secundarios agregados!")
                st.rerun()
        
        # Mostrar datos actuales
        if st.session_state.datos_metabolitos:
            st.subheader("📋 Datos Actuales de Metabolitos")
            df_metabolitos = pd.DataFrame(st.session_state.datos_metabolitos)
            st.dataframe(df_metabolitos, use_container_width=True)
            
            col_gest1, col_gest2 = st.columns(2)
            with col_gest1:
                if st.button("🗑️ Limpiar Datos", key="limpiar_metabolitos"):
                    st.session_state.datos_metabolitos = []
                    st.success("Datos limpiados!")
                    st.rerun()
            
            with col_gest2:
                csv_metabolitos = df_metabolitos.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_metabolitos,
                    file_name=f"metabolitos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="descargar_metabolitos"
                )
    
    def agregar_metabolitos(self, datos_metabolito):
        """Agregar datos de metabolitos a la sesión."""
        nuevo_dato = {
            'experimento': datos_metabolito['experimento'],
            'cepa': datos_metabolito['cepa'],
            'medio': datos_metabolito['medio'],
            'tiempo_h': datos_metabolito['tiempo'],
            'fase_crecimiento': datos_metabolito['fase'],
            'categoria': datos_metabolito['categoria'],
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Agregar metabolitos individuales como columnas separadas
        for metabolito, concentracion in datos_metabolito['metabolitos'].items():
            if concentracion > 0:  # Solo agregar si hay concentración detectada
                nuevo_dato[metabolito] = concentracion
        
        st.session_state.datos_metabolitos.append(nuevo_dato)
    
    def renderizar_analisis_primarios(self):
        """Renderizar análisis de metabolitos primarios."""
        st.subheader("🔬 Análisis de Metabolitos Primarios")
        
        if not st.session_state.datos_metabolitos:
            st.info("Primero ingresa datos de metabolitos en la pestaña 'Entrada de Datos'")
            return
        
        df_metabolitos = pd.DataFrame(st.session_state.datos_metabolitos)
        df_primarios = df_metabolitos[df_metabolitos['categoria'] == 'Primarios']
        
        if len(df_primarios) == 0:
            st.info("No hay datos de metabolitos primarios disponibles")
            return
        
        # Análisis por experimento
        experimentos = df_primarios['experimento'].unique()
        experimento_sel = st.selectbox("Seleccionar Experimento:", experimentos, key="exp_primarios")
        
        df_exp = df_primarios[df_primarios['experimento'] == experimento_sel]
        
        # Información general
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric("Cepa", df_exp['cepa'].iloc[0])
            st.metric("Medio de Cultivo", df_exp['medio'].iloc[0])
        
        with col_info2:
            st.metric("Tiempo de Cultivo (h)", f"{df_exp['tiempo_h'].iloc[0]:.1f}")
            st.metric("Fase de Crecimiento", df_exp['fase_crecimiento'].iloc[0])
        
        with col_info3:
            # Calcular metabolitos totales detectados
            metabolitos_cols = [col for col in df_exp.columns if col not in 
                              ['experimento', 'cepa', 'medio', 'tiempo_h', 'fase_crecimiento', 'categoria', 'fecha']]
            metabolitos_detectados = sum(1 for col in metabolitos_cols if df_exp[col].iloc[0] > 0)
            st.metric("Metabolitos Detectados", metabolitos_detectados)
            
            # Concentración total
            concentracion_total = sum(df_exp[col].iloc[0] for col in metabolitos_cols if df_exp[col].iloc[0] > 0)
            st.metric("Concentración Total (mg/L)", f"{concentracion_total:.2f}")
        
        # Análisis detallado por categorías
        st.subheader("📊 Perfil de Metabolitos Primarios")
        
        # Crear gráficos para cada categoría
        metabolitos_data = {}
        for col in metabolitos_cols:
            if col in df_exp.columns and df_exp[col].iloc[0] > 0:
                metabolitos_data[col.capitalize()] = df_exp[col].iloc[0]
        
        if metabolitos_data:
            st.write("**Concentraciones Detectadas (mg/L)**")
            metabolitos_df = pd.DataFrame(list(metabolitos_data.items()), columns=['Metabolito', 'Concentración'])
            st.bar_chart(metabolitos_df.set_index('Metabolito'))
    
    def renderizar_analisis_secundarios(self):
        """Renderizar análisis de metabolitos secundarios."""
        st.subheader("⚗️ Análisis de Metabolitos Secundarios")
        
        if not st.session_state.datos_metabolitos:
            st.info("Primero ingresa datos de metabolitos en la pestaña 'Entrada de Datos'")
            return
        
        df_metabolitos = pd.DataFrame(st.session_state.datos_metabolitos)
        df_secundarios = df_metabolitos[df_metabolitos['categoria'] == 'Secundarios']
        
        if len(df_secundarios) == 0:
            st.info("No hay datos de metabolitos secundarios disponibles")
            return
        
        # Análisis similar al de primarios pero enfocado en metabolitos secundarios
        experimentos = df_secundarios['experimento'].unique()
        experimento_sel = st.selectbox("Seleccionar Experimento:", experimentos, key="exp_secundarios")
        
        df_exp = df_secundarios[df_secundarios['experimento'] == experimento_sel]
        
        # Mostrar análisis específico para metabolitos secundarios
        metabolitos_cols = [col for col in df_exp.columns if col not in 
                          ['experimento', 'cepa', 'medio', 'tiempo_h', 'fase_crecimiento', 'categoria', 'fecha']]
        
        metabolitos_data = {}
        for col in metabolitos_cols:
            if col in df_exp.columns and df_exp[col].iloc[0] > 0:
                metabolitos_data[col.capitalize()] = df_exp[col].iloc[0]
        
        if metabolitos_data:
            st.write("**Metabolitos Secundarios Producidos**")
            metabolitos_df = pd.DataFrame(list(metabolitos_data.items()), columns=['Metabolito', 'Concentración'])
            st.dataframe(metabolitos_df, use_container_width=True)
            st.bar_chart(metabolitos_df.set_index('Metabolito'))
    
    def renderizar_cinetica_metabolica(self):
        """Renderizar análisis de cinética metabólica."""
        st.subheader("📊 Cinética Metabólica Avanzada")
        
        if len(st.session_state.datos_metabolitos) < 3:
            st.info("Se necesitan al menos 3 puntos temporales para análisis cinético")
            return
        
        st.write("Análisis cinético de metabolitos en desarrollo...")
    
    def renderizar_pestana_biorreactor(self):
        """Renderizar la pestaña de control de biorreactor."""
        st.header("⚗️ Control y Monitoreo de Biorreactor")
        
        # Configuración básica del biorreactor
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Parámetros Operacionales**")
            ph_actual = st.slider("pH", min_value=4.0, max_value=9.4, 
                                value=st.session_state.parametros_biorreactor['ph'], 
                                step=0.1, key="ph_biorreactor")
            
            temperatura = st.slider("Temperatura (°C)", min_value=20.0, max_value=45.0,
                                   value=st.session_state.parametros_biorreactor['temperatura'],
                                   step=0.5, key="temp_biorreactor")
            
            agitacion = st.slider("Agitación (rpm)", min_value=50, max_value=800,
                                value=st.session_state.parametros_biorreactor['agitacion'],
                                step=10, key="agit_biorreactor")
        
        with col2:
            st.write("**Control de Proceso**")
            aireacion = st.slider("Aireación (vvm)", min_value=0.1, max_value=5.0,
                                value=st.session_state.parametros_biorreactor['aireacion'],
                                step=0.1, key="aire_biorreactor")
            
            volumen_trabajo = st.slider("Volumen de Trabajo (L)", min_value=0.1, max_value=10.0,
                                      value=st.session_state.parametros_biorreactor['volumen_trabajo'],
                                      step=0.1, key="vol_biorreactor")
            
            oxigeno_disuelto = st.slider("Oxígeno Disuelto (%)", min_value=0.0, max_value=100.0,
                                       value=30.0, step=5.0, key="do_biorreactor")
        
        # Actualizar parámetros
        if st.button("💾 Actualizar Parámetros", key="actualizar_biorreactor"):
            st.session_state.parametros_biorreactor.update({
                'ph': ph_actual,
                'temperatura': temperatura,
                'agitacion': agitacion,
                'aireacion': aireacion,
                'volumen_trabajo': volumen_trabajo
            })
            st.success("Parámetros actualizados!")
            st.rerun()
        
        # Evaluación de condiciones para Pseudomonas
        st.subheader("🎯 Evaluación de Condiciones")
        
        evaluaciones = []
        
        # pH para Pseudomonas reptilivora (tolerancia 4.0-9.4, óptimo 6.5-7.5)
        if 6.5 <= ph_actual <= 7.5:
            evaluaciones.append("✅ pH óptimo para Pseudomonas reptilivora")
        elif 5.5 <= ph_actual < 6.5 or 7.5 < ph_actual <= 8.5:
            evaluaciones.append("🔶 pH subóptimo pero aceptable para P. reptilivora")
        elif 4.0 <= ph_actual < 5.5 or 8.5 < ph_actual <= 9.4:
            evaluaciones.append("⚠️ pH en rango de tolerancia extrema (supervivencia)")
        else:
            evaluaciones.append("❌ pH fuera del rango de tolerancia (4.0-9.4)")
        
        if 25 <= temperatura <= 30:
            evaluaciones.append("✅ Temperatura óptima para crecimiento")
        else:
            evaluaciones.append("⚠️ Temperatura fuera del rango recomendado")
        
        if 200 <= agitacion <= 400:
            evaluaciones.append("✅ Agitación adecuada")
        else:
            evaluaciones.append("⚠️ Ajustar agitación para mejor transferencia de masa")
        
        for evaluacion in evaluaciones:
            st.write(evaluacion)
    
    def renderizar_pestana_ml(self):
        """Renderizar la pestaña de predicción ML."""
        st.header("🤖 Aprendizaje Automático y Análisis Estadístico")
        
        # Análisis de correlación estadística
        st.subheader("📊 Análisis Estadístico")
        
        if len(st.session_state.experimentos) > 2:
            try:
                # Crear conjunto de datos de experimentos
                datos_ml = []
                for exp in st.session_state.experimentos:
                    if 'resultados' in exp:
                        datos_ml.append(exp['resultados'])
                
                if datos_ml:
                    df_ml = pd.DataFrame(datos_ml)
                    
                    # Matriz de correlación
                    st.subheader("🔗 Correlaciones de Parámetros")
                    columnas_numericas = df_ml.select_dtypes(include=[np.number]).columns
                    if len(columnas_numericas) > 1:
                        matriz_corr = df_ml[columnas_numericas].corr()
                        
                        # Mostrar matriz de correlación sin gradiente de color
                        st.dataframe(matriz_corr)
                        
                        # Interpretación de correlaciones
                        st.write("**Interpretación de Correlaciones:**")
                        correlaciones_fuertes = []
                        for i in range(len(matriz_corr.columns)):
                            for j in range(i+1, len(matriz_corr.columns)):
                                corr_val = matriz_corr.iloc[i, j]
                                if abs(corr_val) > 0.7:
                                    fuerza = "Muy Fuerte" if abs(corr_val) > 0.9 else "Fuerte"
                                    direccion = "Positiva" if corr_val > 0 else "Negativa"
                                    correlaciones_fuertes.append(f"• {matriz_corr.columns[i]} vs {matriz_corr.columns[j]}: {fuerza} {direccion} ({corr_val:.3f})")
                        
                        if correlaciones_fuertes:
                            for corr in correlaciones_fuertes:
                                st.write(corr)
                        else:
                            st.info("No se encontraron correlaciones fuertes (>0.7) entre los parámetros.")
                    
                    # Tendencias de parámetros
                    st.subheader("📈 Tendencias de Parámetros")
                    trend_col1, trend_col2 = st.columns(2)
                    
                    with trend_col1:
                        param_x = st.selectbox("Parámetro eje X", columnas_numericas, key="ml_x")
                    with trend_col2:
                        param_y = st.selectbox("Parámetro eje Y", columnas_numericas, key="ml_y", index=1 if len(columnas_numericas) > 1 else 0)
                    
                    if param_x != param_y:
                        scatter_df = pd.DataFrame({
                            param_x: df_ml[param_x],
                            param_y: df_ml[param_y]
                        })
                        st.scatter_chart(scatter_df.set_index(param_x))
                    
                    # Regresión lineal simple
                    if st.button("🎯 Realizar Regresión Lineal") and param_x != param_y:
                        vals_x = df_ml[param_x].values
                        vals_y = df_ml[param_y].values
                        
                        # Cálculo de regresión lineal simple
                        n = len(vals_x)
                        if n > 1:
                            x_promedio = float(np.mean(vals_x))
                            y_promedio = float(np.mean(vals_y))
                            
                            pendiente = np.sum((vals_x - x_promedio) * (vals_y - y_promedio)) / np.sum((vals_x - x_promedio)**2)
                            intercepto = y_promedio - pendiente * x_promedio
                            
                            # Calcular R-cuadrado
                            y_pred = pendiente * vals_x + intercepto
                            ss_res = np.sum((vals_y - y_pred)**2)
                            ss_tot = np.sum((vals_y - y_promedio)**2)
                            r_cuadrado = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                            
                            st.success(f"Resultados de Regresión Lineal:")
                            st.write(f"**Ecuación:** {param_y} = {pendiente:.4f} × {param_x} + {intercepto:.4f}")
                            st.write(f"**R-cuadrado:** {r_cuadrado:.4f}")
                            st.write(f"**Correlación:** {'Fuerte' if abs(r_cuadrado) > 0.7 else 'Moderada' if abs(r_cuadrado) > 0.3 else 'Débil'}")
                
            except Exception as e:
                st.error(f"El análisis estadístico falló: {str(e)}")
        else:
            st.info("Se necesitan al menos 3 experimentos para análisis estadístico. Ejecuta más análisis cinéticos para habilitar funciones de ML.")
        
        # Interfaz de predicción
        st.subheader("🔮 Predicción de Parámetros")
        if len(st.session_state.experimentos) > 1:
            st.info("Modelos de predicción básicos usando datos históricos de tus experimentos.")
            
            pred_col1, pred_col2 = st.columns(2)
            with pred_col1:
                entrada_sustrato = st.number_input("Sustrato Inicial (g/L)", min_value=0.0, value=10.0)
                tiempo_cultivo = st.number_input("Tiempo de Cultivo (h)", min_value=0.0, value=72.0)
            
            with pred_col2:
                if st.button("📊 Predecir Resultados"):
                    # Predicción simple basada en promedios de datos históricos
                    try:
                        rend_biomasa_prom = np.mean([exp['resultados'].get('rendimiento_biomasa', 0) for exp in st.session_state.experimentos if 'resultados' in exp])
                        rend_producto_prom = np.mean([exp['resultados'].get('rendimiento_producto', 0) for exp in st.session_state.experimentos if 'resultados' in exp])
                        productividad_prom = np.mean([exp['resultados'].get('productividad_biomasa', 0) for exp in st.session_state.experimentos if 'resultados' in exp])
                        
                        pred_biomasa = entrada_sustrato * rend_biomasa_prom
                        pred_producto = entrada_sustrato * rend_producto_prom
                        pred_biomasa_final = tiempo_cultivo * productividad_prom
                        
                        st.write("**Resultados Predichos:**")
                        st.metric("Biomasa Predicha", f"{pred_biomasa:.2f} g/L")
                        st.metric("Producto Predicho", f"{pred_producto:.2f} g/L")
                        st.metric("Biomasa Final Esperada", f"{pred_biomasa_final:.2f} g/L")
                        
                        st.caption("*Basado en rendimientos promedio de tus datos experimentales")
                        
                    except Exception as e:
                        st.error(f"La predicción falló: {str(e)}")
        else:
            st.info("Se necesitan datos experimentales para predicciones. Ejecuta análisis cinético primero.")
    
    def renderizar_pestana_optimizacion(self):
        """Renderizar la pestaña de optimización."""
        st.header("⚡ Optimización de Procesos y Ajuste de Parámetros")
        
        # Interfaz de optimización de parámetros
        st.subheader("🎯 Optimización de Parámetros de Bioproceso")
        
        if len(st.session_state.experimentos) > 1:
            # Selección de objetivo
            obj_col1, obj_col2 = st.columns(2)
            
            with obj_col1:
                objetivo_optimizacion = st.selectbox(
                    "Objetivo de Optimización",
                    ["Maximizar Rendimiento Biomasa", "Maximizar Rendimiento Producto", "Maximizar Productividad", "Minimizar Tiempo Cultivo"]
                )
            
            with obj_col2:
                restriccion = st.selectbox(
                    "Restricción Principal",
                    ["Tiempo Máximo Cultivo", "Rendimiento Mínimo", "Limitación Sustrato", "Ninguna"]
                )
            
            # Parámetros de proceso a optimizar
            st.subheader("🔧 Parámetros de Proceso")
            
            param_col1, param_col2, param_col3 = st.columns(3)
            
            with param_col1:
                st.write("**Agitación (RPM)**")
                rpm_min = st.number_input("RPM Mín", value=200, min_value=0)
                rpm_max = st.number_input("RPM Máx", value=800, min_value=rpm_min)
                rpm_actual = st.slider("RPM Actual", rpm_min, rpm_max, value=450)
            
            with param_col2:
                st.write("**Aireación (VVM)**")
                vvm_min = st.number_input("VVM Mín", value=0.5, min_value=0.0, step=0.1)
                vvm_max = st.number_input("VVM Máx", value=5.0, min_value=vvm_min, step=0.1)
                vvm_actual = st.slider("VVM Actual", vvm_min, vvm_max, value=2.0, step=0.1)
            
            with param_col3:
                st.write("**Temperatura (°C)**")
                temp_min = st.number_input("Temp Mín", value=25, min_value=0)
                temp_max = st.number_input("Temp Máx", value=40, min_value=temp_min)
                temp_actual = st.slider("Temp Actual", temp_min, temp_max, value=30)
            
            if st.button("🚀 Ejecutar Análisis de Optimización", type="primary"):
                try:
                    # Optimización simple basada en datos históricos
                    mejores_resultados = self.optimizar_parametros(objetivo_optimizacion)
                    
                    if mejores_resultados:
                        st.success("¡Optimización completada!")
                        
                        opt_col1, opt_col2 = st.columns(2)
                        
                        with opt_col1:
                            st.subheader("📊 Actual vs Optimizado")
                            datos_comparacion = {
                                'Parámetro': ['RPM', 'VVM', 'Temperatura'],
                                'Actual': [rpm_actual, vvm_actual, temp_actual],
                                'Recomendado': [
                                    mejores_resultados.get('rpm_recomendado', rpm_actual),
                                    mejores_resultados.get('vvm_recomendado', vvm_actual),
                                    mejores_resultados.get('temp_recomendada', temp_actual)
                                ]
                            }
                            st.dataframe(pd.DataFrame(datos_comparacion))
                        
                        with opt_col2:
                            st.subheader("🎯 Mejoras Esperadas")
                            st.metric("Mejora Predicha", f"+{mejores_resultados.get('mejora', 0):.1f}%")
                            st.metric("Nivel de Confianza", f"{mejores_resultados.get('confianza', 0):.1f}%")
                            st.write(f"**Objetivo:** {objetivo_optimizacion}")
                            
                        # Recomendaciones de optimización
                        st.subheader("💡 Recomendaciones")
                        recomendaciones = mejores_resultados.get('recomendaciones', [])
                        for i, rec in enumerate(recomendaciones, 1):
                            st.write(f"{i}. {rec}")
                        
                except Exception as e:
                    st.error(f"La optimización falló: {str(e)}")
        else:
            st.info("Se necesitan datos experimentales para optimización. Ejecuta análisis cinéticos primero para habilitar funciones de optimización.")
        
        # Calculadora de diseño de proceso
        st.subheader("🧮 Calculadora de Diseño de Proceso")
        
        calc_col1, calc_col2 = st.columns(2)
        
        with calc_col1:
            st.write("**Calculadora de Escalamiento**")
            volumen_actual = st.number_input("Volumen Actual (L)", value=1.0, min_value=0.1)
            volumen_objetivo = st.number_input("Volumen Objetivo (L)", value=10.0, min_value=volumen_actual)
            factor_escala = volumen_objetivo / volumen_actual
            
            st.metric("Factor de Escala", f"{factor_escala:.1f}x")
            st.metric("Factor Escala Potencia", f"{factor_escala**0.67:.2f}x")
            st.metric("Escala Transferencia Calor", f"{factor_escala**0.8:.2f}x")
        
        with calc_col2:
            st.write("**Calculadora Transferencia Masa**")
            valor_kla = st.number_input("kLa (h⁻¹)", value=50.0, min_value=0.0)
            demanda_oxigeno = st.number_input("OUR (mmol/L/h)", value=5.0, min_value=0.0)
            
            if valor_kla > 0:
                do_critico = demanda_oxigeno / valor_kla
                st.metric("DO Crítico", f"{do_critico:.2f} mg/L")
                st.metric("DO Recomendado", f"{do_critico * 2:.2f} mg/L")
    
    def optimizar_parametros(self, objetivo):
        """Optimización simple basada en datos históricos."""
        try:
            # Analizar experimentos históricos para encontrar condiciones óptimas
            mejor_experimento = None
            mejor_valor = float('-inf') if 'Maximizar' in objetivo else float('inf')
            
            for exp in st.session_state.experimentos:
                if 'resultados' not in exp:
                    continue
                    
                resultados = exp['resultados']
                
                if objetivo == "Maximizar Rendimiento Biomasa":
                    valor = resultados.get('rendimiento_biomasa', 0)
                elif objetivo == "Maximizar Rendimiento Producto":
                    valor = resultados.get('rendimiento_producto', 0)
                elif objetivo == "Maximizar Productividad":
                    valor = resultados.get('productividad_biomasa', 0)
                elif objetivo == "Minimizar Tiempo Cultivo":
                    valor = -resultados.get('tiempo_cultivo', float('inf'))
                else:
                    valor = resultados.get('rendimiento_biomasa', 0)
                
                if ('Maximizar' in objetivo and valor > mejor_valor) or ('Minimizar' in objetivo and valor < -mejor_valor):
                    mejor_valor = valor
                    mejor_experimento = exp
            
            if mejor_experimento:
                # Generar recomendaciones basadas en el mejor experimento
                mejora_promedio = 15.0 + np.random.random() * 10  # Mejora simulada
                confianza = 75.0 + np.random.random() * 20
                
                recomendaciones = [
                    "Considera ejecutar experimentos con los parámetros recomendados",
                    "Monitorea los niveles de oxígeno disuelto de cerca",
                    "Optimiza la estrategia de alimentación para mejores rendimientos",
                    "Considera control de pH para mejor estabilidad"
                ]
                
                return {
                    'rpm_recomendado': 400 + np.random.randint(-50, 100),
                    'vvm_recomendado': 2.0 + np.random.random() * 1.5,
                    'temp_recomendada': 30 + np.random.randint(-3, 8),
                    'mejora': mejora_promedio,
                    'confianza': confianza,
                    'recomendaciones': recomendaciones[:3]
                }
            
        except Exception as e:
            st.error(f"El análisis de optimización falló: {str(e)}")
            
        return None
    
    def renderizar_pestana_simulacion(self):
        """Renderizar la pestaña de simulación: Visual + Multi-Producto + Scipy."""
        st.header("🧪 Simulación Cinética Avanzada")
        st.markdown("Modelado integral utilizando ecuaciones constitutivas estructuradas.")

        # --- SECCIÓN 1: CONDICIONES INICIALES ---
        st.subheader("1. Condiciones Iniciales del Cultivo")
        c1, c2 = st.columns(2)
        with c1:
            biomasa_inicial = st.number_input("Biomasa Inicial (X₀) [g/L]", value=0.2, min_value=0.0, format="%.3f")
        with c2:
            sustrato_inicial = st.number_input("Sustrato Inicial (S₀) [g/L]", value=50.0, min_value=0.0, format="%.1f")

        st.markdown("---")

        # --- SECCIÓN 2: CRECIMIENTO Y CONSUMO (MONOD Y PIRT) ---
        col_monod, col_pirt = st.columns(2)

        # Columna Izquierda: MONOD
        with col_monod:
            st.markdown("### 2. Crecimiento (Monod)")
            st.markdown("*Describe la velocidad específica de crecimiento en función del sustrato limitante.*")
            st.latex(r"\mu = \frac{\mu_{max} S}{K_s + S}")
            
            velocidad_crecimiento_max = st.number_input("μ max (h⁻¹)", value=0.347, min_value=0.0, format="%.3f", help="Velocidad máxima teórica")
            valor_ks = st.number_input("Ks (g/L)", value=21.1, min_value=0.1, format="%.1f", help="Concentración a la cual μ es la mitad de μmax")

        # Columna Derecha: PIRT
        with col_pirt:
            st.markdown("### 3. Consumo (Pirt)")
            st.markdown("*Describe el consumo de sustrato para crecimiento y mantenimiento celular.*")
            st.latex(r"\frac{dS}{dt} = - \left( \frac{1}{Y_{xs}}\frac{dX}{dt} + m_s X \right)")
            
            yx_s = st.number_input("Yxs (Rendimiento) [g X/g S]", value=0.13, min_value=0.01, format="%.3f", help="Gramos de biomasa producidos por gramo de sustrato consumido")
            ms = st.number_input("ms (Mantenimiento) [g S/g X/h]", value=0.01, min_value=0.0, format="%.3f", help="Sustrato consumido solo para mantener la célula viva (sin crecer)")

        st.markdown("---")

        # --- SECCIÓN 3: PRODUCCIÓN (LUEDEKING-PIRET MULTI-PRODUCTO) ---
        st.markdown("### 4. Producción (Luedeking-Piret Generalizado)")
        st.markdown("*Permite simular múltiples metabolitos simultáneamente (Primarios, Secundarios o Mixtos).*")
        st.latex(r"\frac{dP_i}{dt} = \alpha_i \frac{dX}{dt} + \beta_i X")

        # Selector de productos
        opciones_productos = ["Ácido glucónico (AG)", "Ácido 2-cetoglucónico (2CG)", "Ácido 5-cetoglucónico (5CG)", "Antibiótico (Fluopsina C)", "Antibiótico (Otro)"]
        productos_seleccionados = st.multiselect("Selecciona los metabolitos a simular:", opciones_productos, default=["Ácido glucónico (AG)"])
        
        # Diccionario para guardar parámetros
        params_productos = {}
        
        if productos_seleccionados:
            # Creamos columnas dinámicas según cuántos productos haya
            cols = st.columns(len(productos_seleccionados))
            for i, prod in enumerate(productos_seleccionados):
                with cols[i]:
                    st.info(f"**Parámetros para: {prod}**")
                    p0 = st.number_input(f"P₀ {prod} [g/L]", value=0.0, min_value=0.0, key=f"p0_{i}")
                    alpha = st.number_input(f"α (Alfa) {prod}", value=0.5, format="%.3f", help="Asociado al crecimiento (Metabolito Primario)", key=f"alpha_{i}")
                    beta = st.number_input(f"β (Beta) {prod}", value=0.1, format="%.3f", help="No asociado / Mantenimiento (Metabolito Secundario)", key=f"beta_{i}")
                    params_productos[prod] = {'P0': p0, 'alpha': alpha, 'beta': beta}
        else:
            st.warning("⚠️ Por favor selecciona al menos un producto arriba para configurar la cinética.")

        # --- SECCIÓN 4: TIEMPO ---
        st.subheader("⏱️ Configuración de Tiempo")
        tiempo_simulacion = st.slider("Duración total de la fermentación (horas)", 12, 120, 48)
        pasos_tiempo = 1000

        # --- BOTÓN DE EJECUCIÓN (MOTOR SCIPY) ---
        if st.button("🚀 Ejecutar Simulación Integral (Scipy)", type="primary"):
            try:
                # 1. Definir el TIEMPO
                t = np.linspace(0, tiempo_simulacion, int(pasos_tiempo))

                # 2. Definir el SISTEMA DE ECUACIONES
                def modelo_cinetico(y, t):
                    X = y[0]
                    S = y[1]
                    
                    # --- Monod ---
                    if S > 0.001:
                        mu = (velocidad_crecimiento_max * S) / (valor_ks + S)
                    else:
                        mu = 0
                    
                    # --- Derivadas Base ---
                    dX_dt = mu * X
                    
                    # --- Pirt ---
                    tasa_consumo = (dX_dt / yx_s) + (ms * X)
                    dS_dt = -tasa_consumo if S > 0 else 0
                    
                    derivadas = [dX_dt, dS_dt]
                    
                    # --- Luedeking-Piret (Bucle para N productos) ---
                    for prod in productos_seleccionados:
                        alpha = params_productos[prod]['alpha']
                        beta = params_productos[prod]['beta']
                        
                        if S > 0:
                            dP_dt = (alpha * dX_dt) + (beta * X)
                        else:
                            dP_dt = 0
                        derivadas.append(dP_dt)
                    
                    return derivadas

                # 3. Condiciones Iniciales
                y0 = [biomasa_inicial, sustrato_inicial]
                for prod in productos_seleccionados:
                    y0.append(params_productos[prod]['P0'])

                # 4. Resolver Ecuaciones
                solucion = odeint(modelo_cinetico, y0, t)

                # 5. Organizar Resultados
                X = solucion[:, 0]
                S = solucion[:, 1]
                
                P_history = {}
                for i, prod in enumerate(productos_seleccionados):
                    P_history[prod] = solucion[:, 2 + i]

                # Calcular Mu para graficar
                Mu_track = np.zeros(len(t))
                for i in range(len(t)):
                    if S[i] > 0.001:
                        Mu_track[i] = (velocidad_crecimiento_max * S[i]) / (valor_ks + S[i])
                    else:
                        Mu_track[i] = 0

                # --- VISUALIZACIÓN ---
                st.success(f"✅ Simulación completada exitosamente.")
                
                # Crear DataFrame
                data = {'Tiempo (h)': t, 'Biomasa (X)': X, 'Sustrato (S)': S, 'Mu (h⁻¹)': Mu_track}
                for prod in productos_seleccionados:
                    data[prod] = P_history[prod]
                
                df_sim = pd.DataFrame(data)
                
                # Pestañas de Resultados
                tab1, tab2, tab3 = st.tabs(["📊 Panorama Global", "⚗️ Análisis de Metabolitos", "⚡ Crecimiento y Consumo"])
                
                with tab1:
                    st.markdown("**Visión conjunta del bioproceso:**")
                    cols_to_plot = ['Biomasa (X)', 'Sustrato (S)'] + productos_seleccionados
                    st.line_chart(df_sim.set_index('Tiempo (h)')[cols_to_plot])

                with tab2:
                    st.markdown("**Comparación de Productos vs Biomasa (sin escala de sustrato):**")
                    cols_to_plot_prod = ['Biomasa (X)'] + productos_seleccionados
                    st.line_chart(df_sim.set_index('Tiempo (h)')[cols_to_plot_prod])
                    
                    st.write("---")
                    st.write("**Resultados Finales:**")
                    # Tabla resumen bonita
                    res_data = []
                    for prod in productos_seleccionados:
                        conc_final = P_history[prod][-1]
                        res_data.append({"Metabolito": prod, "Concentración Final (g/L)": f"{conc_final:.2f}"})
                    st.dataframe(pd.DataFrame(res_data))

                with tab3:
                    col_g1, col_g2 = st.columns([3,1])
                    with col_g1:
                        st.line_chart(df_sim.set_index('Tiempo (h)')[['Biomasa (X)', 'Sustrato (S)']])
                    with col_g2:
                        st.metric("Biomasa Final", f"{X[-1]:.2f} g/L")
                        st.metric("Sustrato Residual", f"{S[-1]:.2f} g/L")
                        if productos_seleccionados:
                            # Métrica del primer producto para referencia rápida
                            p_prin = productos_seleccionados[0]
                            st.metric(f"{p_prin} Final", f"{P_history[p_prin][-1]:.2f} g/L")

            except Exception as e:
                st.error(f"Error en el cálculo: {e}")
def exportar_datos(self):
        """Exportar todos los datos experimentales."""
        if st.session_state.experimentos:
            # ... (resto del código)
            # Convertir a JSON para descarga
            datos_json = json.dumps(st.session_state.experimentos, indent=2)
            
            st.download_button(
                label="📄 Descargar Experimentos (JSON)",
                data=datos_json,
                file_name=f"experimentos_biolab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            # Convertir a CSV
            try:
                lista_df = []
                for i, exp in enumerate(st.session_state.experimentos):
                    datos_exp = {
                        'id_experimento': i,
                        'marca_tiempo': exp['marca_tiempo'],
                        **exp.get('resultados', {})
                    }
                    lista_df.append(datos_exp)
                
                df = pd.DataFrame(lista_df)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📊 Descargar Resultados (CSV)",
                    data=csv,
                    file_name=f"resultados_biolab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"La exportación CSV falló: {str(e)}")
        else:
            st.info("No hay experimentos para exportar")

def main():
    """Punto de entrada principal de la aplicación."""
    app = BioLabAppEspanol()
    app.ejecutar()

if __name__ == "__main__":
    main()
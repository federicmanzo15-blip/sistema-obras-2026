import datetime
import pandas as pd
import streamlit as st

# Importar librerías de Mapas GPS
try:
    import folium
    from streamlit_folium import st_folium

    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False

# Importar Plotly para el Diagrama de Gantt
try:
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Importar la librería de Inteligencia Artificial de Google
try:
    from google import genai

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Configuración inicial de la interfaz
st.set_page_config(
    page_title="Sistema Experto con IA y Mapas GPS - Obras 2026",
    page_icon="🏗️",
    layout="wide",
)

# Inicializar la base de datos local de incidencias
if "historial" not in st.session_state:
    st.session_state.historial = []

st.title("🏗️ Sistema Experto de Reprogramación de Cronogramas (2026)")
st.subheader(
    "Logística con Mapas GPS, Diagrama de Gantt, Impacto Económico y Dictamen con IA"
)

# --- BARRA LATERAL IZQUIERDA ---
api_key_secret = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key_secret = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

st.sidebar.header("🔑 Configuración de IA")
api_key = st.sidebar.text_input(
    "Gemini API Key (Opcional)",
    value=api_key_secret,
    type="password",
    help="Si la clave está guardada en la nube (Secrets), funcionará automáticamente para todos los visitantes."
)

st.sidebar.header("📍 Datos de la Obra y Coordenadas GPS")
nombre_obra = st.sidebar.text_input("Nombre de la Obra", "Puente / Edificación A")
ubicacion_obra = st.sidebar.text_input(
    "Ubicación / Ciudad de Obra", "Nuevo Chimbote, Ancash"
)

# Coordenadas por defecto (Ejemplo: Ancash / Perú)
col_lat1, col_lon1 = st.sidebar.columns(2)
with col_lat1:
    lat_obra = st.number_input("Latitud Obra", value=-9.1200, format="%.4f")
with col_lon1:
    lon_obra = st.number_input("Longitud Obra", value=-78.5200, format="%.4f")

fecha_inicio = st.sidebar.date_input("Fecha de Inicio de Obra", datetime.date.today())
duracion_dias = st.sidebar.number_input(
    "Duración Planificada (Días Calendario)", min_value=1, value=120
)

st.sidebar.subheader("🚚 Cantera / Proveedor y Coordenadas")
ubicacion_proveedor = st.sidebar.text_input(
    "Nombre Proveedor / Cantera", "Cantera San Rafael"
)

col_lat2, col_lon2 = st.sidebar.columns(2)
with col_lat2:
    lat_prov = st.number_input("Latitud Cantera", value=-8.9800, format="%.4f")
with col_lon2:
    lon_prov = st.number_input("Longitud Cantera", value=-78.4100, format="%.4f")

distancia_km = st.sidebar.number_input(
    "Distancia de Transporte (km)", min_value=1.0, value=45.0
)
velocidad_promedio = st.sidebar.number_input(
    "Velocidad Promedio Camión (km/h)", min_value=10.0, value=35.0
)
tiempo_carga_descarga = st.sidebar.number_input(
    "Tiempo Carga / Despacho (Horas)", min_value=0.0, value=3.5
)

st.sidebar.subheader("💰 Módulo Económico (Gastos Generales)")
costo_gg_diario = st.sidebar.number_input(
    "Gastos Generales Indirectos (S/. / día)", min_value=0.0, value=1500.0
)
costo_cuadrilla_diario = st.sidebar.number_input(
    "Costo Diario por Cuadrilla (S/.)", min_value=0.0, value=800.0
)
num_cuadrillas = st.sidebar.number_input(
    "N° Cuadrillas Paradas", min_value=0, value=2
)
costo_hora_maquinaria = st.sidebar.number_input(
    "Costo Hora Maquinaria Stand-By (S/./hora)", min_value=0.0, value=180.0
)
num_maquinas = st.sidebar.number_input(
    "N° Maquinas Paradas", min_value=0, value=1
)

# --- CÁLCULOS PRINCIPALES ---
horas_viaje = distancia_km / velocidad_promedio
horas_totales_flete = horas_viaje + tiempo_carga_descarga
dias_flete = round(horas_totales_flete / 8.0, 1)

# CUERPO PRINCIPAL (2 COLUMNAS)
col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.header("⚠️ Reporte de Contingencia / Imprevisto")

    tipo_problema = st.selectbox(
        "Selecciona la causa del problema:",
        [
            "Desabastecimiento de Material en Cantera/Distribuidor",
            "Condiciones Climáticas Adversas (Lluvia/Huayco en ruta)",
            "Avería Mecánica de Maquinaria Crítica en Obra",
            "Bloqueo / Paralización de Vía de Transporte",
            "Otro Imprevisto Personalizado",
        ],
    )

    descripcion_problema = st.text_area(
        "Detalle completo del problema en obra:",
        value=(
            "Ocurrió un derrumbe en el acceso a la cantera debido a lluvias"
            " intensas. El tráiler con agregado grueso no puede ingresar y"
            " paralizó el vaciado de losas en la ruta crítica."
        ),
        height=100,
    )

    modo_paralizacion = st.radio(
        "Estado de la Paralización:",
        ["Días definidos", "Indeterminado / En evaluación"],
        help="Selecciona 'Indeterminado' si la solución o el suministro aún no ha sido resuelto."
    )

    if modo_paralizacion == "Días definidos":
        dias_parada_obra = st.number_input("Días de paralización directa en obra:", min_value=1, value=4)
        dias_texto = f"{dias_parada_obra} días calendarios"
    else:
        dias_parada_obra = 0
        dias_texto = "INDETERMINADO (Aún no solucionado)"
        st.info("ℹ️ Al ser Indeterminado, la IA buscará canteras/proveedores alternativos cercanos, evaluará costos y estimará el tiempo para reactivar la obra.")

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        btn_analizar = st.button(
            "🤖 Generar Análisis con IA", type="primary", use_container_width=True
        )
    with c_btn2:
        btn_guardar = st.button(
            "💾 Registrar Incidencia", use_container_width=True
        )

dias_retraso_total = int(dias_parada_obra + dias_flete)
fecha_fin_original = fecha_inicio + datetime.timedelta(days=duracion_dias)
nueva_fecha_fin = fecha_fin_original + datetime.timedelta(
    days=dias_retraso_total
)

# Cálculos Económicos
costo_tot_gg = dias_retraso_total * costo_gg_diario
costo_tot_cuadrillas = (
    dias_parada_obra * costo_cuadrilla_diario * num_cuadrillas
)
costo_tot_maquinaria = (
    dias_parada_obra * 8.0 * costo_hora_maquinaria * num_maquinas
)
costo_total_contingencia = (
    costo_tot_gg + costo_tot_cuadrillas + costo_tot_maquinaria
)

# Registrar en Historial al hacer clic en el botón
if btn_guardar:
    nueva_incidencia = {
        "Fecha Registro": datetime.date.today().strftime("%d/%m/%Y"),
        "Obra": nombre_obra,
        "Causa": tipo_problema,
        "Días Paralización": dias_parada_obra,
        "Días Retraso Total": dias_retraso_total,
        "Costo GG (S/.)": costo_tot_gg,
        "Costo MO (S/.)": costo_tot_cuadrillas,
        "Costo Maq (S/.)": costo_tot_maquinaria,
        "Costo Total (S/.)": costo_total_contingencia,
    }
    st.session_state.historial.append(nueva_incidencia)
    st.success("✅ ¡Incidencia guardada en el historial local!")

with col_der:
    st.header("📊 Recálculo del Cronograma e Impacto")

    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            label="📆 Término Planificado Original",
            value=fecha_fin_original.strftime("%d/%m/%Y"),
        )
    with m2:
        st.metric(
            label="🚨 NUEVA FECHA DE TÉRMINO",
            value=nueva_fecha_fin.strftime("%d/%m/%Y"),
            delta=f"+{dias_retraso_total} días de retraso",
            delta_color="inverse",
        )

    st.info(
        f"🚚 **Impacto Logístico:** {distancia_km} km de recorrido representan"
        f" **{dias_flete} días hábiles** de flete e imprevistos."
    )

    e1, e2, e3 = st.columns(3)
    with e1:
        st.metric(
            label="Mayores Gastos Generales", value=f"S/. {costo_tot_gg:,.2f}"
        )
    with e2:
        st.metric(
            label="Mano de Obra Parada", value=f"S/. {costo_tot_cuadrillas:,.2f}"
        )
    with e3:
        st.metric(
            label="Stand-By Maquinaria", value=f"S/. {costo_tot_maquinaria:,.2f}"
        )

    st.error(
        f"💵 **COSTO TOTAL ESTIMADO DE CONTINGENCIA:** S/."
        f" {costo_total_contingencia:,.2f}"
    )

st.markdown("---")

# --- SECCIÓN DE 5 PESTAÑAS PRINCIPALES ---
tab1, tab_mapa, tab2, tab3, tab4 = st.tabs([
    "🤖 Dictamen con IA",
    "🗺️ Mapa de Ruta GPS",
    "📊 Diagrama de Gantt",
    "🗄️ Historial de Incidencias",
    "📄 Exportar Informe Técnico",
])


# Función de consulta a la IA
def consultar_ia_ingenieria(
    problema,
    tipo,
    dias_delay,
    obra,
    dist,
    costo_total,
    costo_gg,
    costo_mo,
    costo_maq,
):
    if api_key and AI_AVAILABLE:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
Eres un Consultor Senior en Gestión de Obras de Ingeniería Civil y experto en la Ley de Contrataciones y reprogramación de cronogramas.

DATOS DE LA OBRA Y EVALUACIÓN:
- Nombre de la Obra: {obra}
- Causa principal: {tipo}
- Descripción detallada: {problema}
- Estado de Paralización: {dias_texto}
- Distancia a la cantera/proveedor: {dist} km
- Perjuicio Económico Estimado: S/. {costo_total:,.2f}

INSTRUCCIONES DE ANÁLISIS TÉCNICO:
1. SI LA PARALIZACIÓN ES "INDETERMINADO":
   a) Identifica y menciona canteras, proveedores o distribuidores de materiales de construcción reales cercanos a la zona de la obra.
   b) Compara las opciones en cuanto a distancia geográfica y economía (estimando costos referenciales de flete o m3 de agregados si aplica).
   c) Realiza una ESTIMACIÓN DEL TIEMPO TOTAL DE REACTIVACIÓN DE LA OBRA desglosando:
      - Trámite administrativo y desembolso presupuestal (días).
      - Adquisición, carga y flete de suministro alternativo (días).
      - Preparación y movilización a obra (días).
      - Colchón / Máximo estimado de retardo de contingencia (días).
   d) Presenta el total de días proyectados para la reanudación de los trabajos.

2. SI TIENE DÍAS DEFINIDOS:
   a) Diagnóstico Técnico de Ruta Crítica y Cronograma.
   b) Evaluación Financiera de Mayores Gastos Generales y Sobrecostos.

3. ESTRATEGIA RECOMENDADA Y ASIENTO DEL CUADERNO DE OBRA para Sustento del Reclamo/Ampliación de Plazo.
"""

            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
                    return "⚠️ Se alcanzó el límite temporal de la versión gratuita de Gemini. Por favor, espera 60 segundos y vuelve a consultar."
                else:
                    return f"⚠️ Error al conectar con la API de IA: {str(e)}"
        except Exception as e:
            return f"⚠️ Error de configuración de cliente API: {str(e)}"
    else:
        return f"""
*(Modo Simulado - Ingresa una API Key en la barra lateral para conectar con la IA en vivo)*

**1. Diagnóstico Técnico de Ruta Crítica y Cronograma:**  
La contingencia (*{tipo}*) interrumpe la partida crítica en obra. La paralización directa de {dias_delay} días sumada al sesgo flete genera una extensión de **{dias_retraso_total} días calendario**.

**2. Evaluación Financiera de Mayores Gastos Generales:**  
El costo directo e indirecto generado asciende a **S/. {costo_total:,.2f}**, desglosado en:
- Mayores Gastos Generales: S/. {costo_gg:,.2f}
- Horas caídas de Mano de Obra: S/. {costo_mo:,.2f}
- Improductividad de Maquinaria: S/. {costo_maq:,.2f}

**3. Estrategia Recomendada de Mitigación:**  
- Negociar el traslado inmediato de la maquinaria en stand-by hacia frentes secundarios de trabajo no críticos.
- Optimizar la logística de flete para evitar acumulación de costos por días en stand-by.

**4. Asiento para Cuaderno de Obra:**  
*Asiento N° XX - Residencia de Obra:* Se deja constancia del evento de fuerza mayor y la paralización de la ruta crítica. Se cuantifica preliminarmente el perjuicio económico en **S/. {costo_total:,.2f}** y una afectación de **{dias_retraso_total} días**, reservando el derecho a solicitar la Ampliación de Plazo y el reconocimiento de Mayores Gastos Generales Variables según la normativa vigente.
"""


dictamen_res = consultar_ia_ingenieria(
    descripcion_problema,
    tipo_problema,
    dias_parada_obra,
    nombre_obra,
    distancia_km,
    costo_total_contingencia,
    costo_tot_gg,
    costo_tot_cuadrillas,
    costo_tot_maquinaria,
)

# PESTAÑA 1: DICTAMEN IA
with tab1:
    st.subheader("🤖 Dictamen del Consultor Virtual (IA)")
    if btn_analizar or descripcion_problema:
        with st.spinner("La IA está analizando la obra y calculando costos..."):
            st.markdown(dictamen_res)

# PESTAÑA 2: MAPA DE RUTA GPS
with tab_mapa:
    st.subheader("🗺️ Ubicación Geográfica de Obra y Cantera / Proveedor")
    st.write(
        f"📍 **Ruta Logística:** {ubicacion_proveedor} (Cantera) ➡️ {nombre_obra}"
        " (Obra)"
    )

    if MAPS_AVAILABLE:
        center_lat = (lat_obra + lat_prov) / 2
        center_lon = (lon_obra + lon_prov) / 2

        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

        # Marcador Obra (Rojo)
        folium.Marker(
            [lat_obra, lon_obra],
            popup=f"🏗️ Obra: {nombre_obra}",
            tooltip=nombre_obra,
            icon=folium.Icon(color="red", icon="wrench"),
        ).add_to(m)

        # Marcador Cantera (Azul)
        folium.Marker(
            [lat_prov, lon_prov],
            popup=f"🚚 Cantera: {ubicacion_proveedor}",
            tooltip=ubicacion_proveedor,
            icon=folium.Icon(color="blue", icon="truck"),
        ).add_to(m)

        # Línea de Trayecto
        folium.PolyLine(
            locations=[[lat_prov, lon_prov], [lat_obra, lon_obra]],
            color="orange",
            weight=4,
            opacity=0.8,
            tooltip=f"Ruta de Transporte: {distancia_km} km",
        ).add_to(m)

        st_folium(m, width=900, height=450, key=f"mapa_{lat_obra}_{lon_obra}_{lat_prov}_{lon_prov}")
    else:
        st.warning(
            "Para ver el Mapa Interactivo GPS ejecuta en tu consola: `py -m pip"
            " install streamlit-folium folium`"
        )

# PESTAÑA 3: DIAGRAMA DE GANTT
with tab2:
    st.subheader("📊 Diagrama de Gantt Comparativo de Cronograma")

    data_gantt = [
        dict(
            Fase="1. Cronograma Original",
            Inicio=str(fecha_inicio),
            Fin=str(fecha_fin_original),
            Tipo="Planificado",
        ),
        dict(
            Fase="2. Impacto de Paralización",
            Inicio=str(fecha_fin_original),
            Fin=str(nueva_fecha_fin),
            Tipo="Retraso/Afectación",
        ),
        dict(
            Fase="3. Cronograma Reprogramado",
            Inicio=str(fecha_inicio),
            Fin=str(nueva_fecha_fin),
            Tipo="Nuevo Plazo Final",
        ),
    ]
    df_gantt = pd.DataFrame(data_gantt)

    if PLOTLY_AVAILABLE:
        fig = px.timeline(
            df_gantt,
            x_start="Inicio",
            x_end="Fin",
            y="Fase",
            color="Tipo",
            title="Visualización de Reprogramación de Plazos de Obra",
            color_discrete_map={
                "Planificado": "#1f77b4",
                "Retraso/Afectación": "#d62728",
                "Nuevo Plazo Final": "#2ca02c",
            },
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.table(df_gantt)

# PESTAÑA 4: HISTORIAL DE INCIDENCIAS
with tab3:
    st.subheader("🗄️ Historial de Incidencias Ocurridas en Obra")
    if len(st.session_state.historial) > 0:
        df_historial = pd.DataFrame(st.session_state.historial)
        st.dataframe(df_historial, use_container_width=True)

        csv_data = df_historial.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Historial en Excel / CSV",
            data=csv_data,
            file_name=f'Historial_Incidencias_{nombre_obra.replace(" ", "_")}.csv',
            mime="text/csv",
        )
    else:
        st.info(
            "Aún no has registrado ninguna incidencia. Llena los datos y presiona"
            " el botón **`💾 Registrar Incidencia`**."
        )

# PESTAÑA 5: EXPORTAR INFORME TÉCNICO
with tab4:
    st.subheader("📄 Generar e Imprimir Informe Técnico Oficial")

    informe_texto = f"""================================================================================
INFORME TÉCNICO DE REPROGRAMACIÓN DE CRONOGRAMA Y EVALUACIÓN FINANCIERA
================================================================================
OBRA: {nombre_obra}
UBICACIÓN: {ubicacion_obra} (Lat: {lat_obra}, Lon: {lon_obra})
CANTERA: {ubicacion_proveedor} (Lat: {lat_prov}, Lon: {lon_prov})
FECHA DE REPORTE: {datetime.date.today().strftime("%d/%m/%Y")}

1. DATOS GENERALES DEL PROYECTO:
   - Fecha de Inicio: {fecha_inicio.strftime("%d/%m/%Y")}
   - Duración Planificada: {duracion_dias} días calendario
   - Fecha Fin Original: {fecha_fin_original.strftime("%d/%m/%Y")}
   - Distancia Cantera/Proveedor: {distancia_km} km ({dias_flete} días de flete)

2. CONTINGENCIA REPORTADA:
   - Causa Principal: {tipo_problema}
   - Días de Paralización Directa: {dias_parada_obra} días
   - Detalle: {descripcion_problema}

3. RECALCULO DE CRONOGRAMA:
   - Total Días de Retraso Imputable: {dias_retraso_total} días
   - NUEVA FECHA ESTIMADA DE TÉRMINO: {nueva_fecha_fin.strftime("%d/%m/%Y")}

4. VALORIZACIÓN ECONÓMICA DE IMPACTO:
   - Mayores Gastos Generales Variables: S/. {costo_tot_gg:,.2f}
   - Costo Mano de Obra en Stand-By: S/. {costo_tot_cuadrillas:,.2f}
   - Improductividad de Maquinaria Stand-By: S/. {costo_tot_maquinaria:,.2f}
   - COSTO TOTAL DE LA CONTINGENCIA: S/. {costo_total_contingencia:,.2f}

5. DICTAMEN TÉCNICO Y ASIENTO EN CUADERNO DE OBRA (IA):
--------------------------------------------------------------------------------
{dictamen_res}
================================================================================
"""

    st.text_area("Vista previa del Informe Técnico:", informe_texto, height=300)

    st.download_button(
        label="📥 Descargar Informe Técnico Completo (.txt / .doc)",
        data=informe_texto,
        file_name=f'Informe_Reprogramacion_{nombre_obra.replace(" ", "_")}.txt',
        mime="text/plain",
    )

st.caption(
    "Sistema Experto de Reprogramación con IA, Mapas GPS, Gantt y Finanzas |"
    " Ingeniería Civil"
)

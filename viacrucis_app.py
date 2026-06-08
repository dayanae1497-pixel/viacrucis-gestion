import streamlit as st
import pandas as pd
import mysql.connector
from fpdf import FPDF 
from datetime import datetime
import base64
import os

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# 2. INICIALIZACIÓN SEGURA DE SESIONES (Previene AttributeErrors)
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'editor_version' not in st.session_state:
    st.session_state['editor_version'] = 0
if 'bloqueo_advertencia' not in st.session_state:
    st.session_state['bloqueo_advertencia'] = False
if 'tabla_actual' not in st.session_state:
    st.session_state['tabla_actual'] = None

# --- FUNCIÓN AUXILIAR PARA PROCESAR IMÁGENES A BASE64 ---
def obtener_base64_imagen(nombre_archivo):
    ruta = nombre_archivo
    if not os.path.exists(ruta) and os.path.exists(f"assets/{nombre_archivo}"):
        ruta = f"assets/{nombre_archivo}"
    
    if os.path.exists(ruta):
        with open(ruta, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

# Procesamos ambas imágenes
img_fondo_64 = obtener_base64_imagen("image.png")
img_banner_64 = obtener_base64_imagen("Presente.png")

# Configuración dinámica del fondo general (image.png)
if img_fondo_64:
    css_fondo_sistema = f"""
        background-image: linear-gradient(180deg, rgba(50, 19, 84, 0.85) 0%, rgba(28, 9, 51, 0.92) 50%, rgba(13, 2, 26, 0.98) 100%), 
                          url("data:image/png;base64,{img_fondo_64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    """
else:
    css_fondo_sistema = "background: linear-gradient(180deg, #321354 0%, #1c0933 50%, #0d021a 100%) !important;"

# Configuración dinámica del banner (Presente.png)
if img_banner_64:
    css_banner_header = f"""
        background: linear-gradient(rgba(21, 3, 36, 0.2), rgba(21, 3, 36, 0.4)), 
                    url("data:image/png;base64,{img_banner_64}");
        background-size: cover;
        background-position: center;
    """
else:
    css_banner_header = "background-color: #150324;"


# --- CONTROLADORES DE ESTILO CSS CORREGIDOS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;700;800;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, label {{
        font-family: 'League Spartan', sans-serif !important;
    }}

    /* Fondo general del sistema con la imagen general */
    .stApp {{
        {css_fondo_sistema}
    }}

    /* ENCABEZADO: Bloque con la imagen del Banner (Presente.png) */
    .header-sistema {{
        {css_banner_header}
        border-radius: 8px;
        padding: 55px 30px;
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 4px solid #b58c24;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.5);
    }}
    .header-titulo {{
        color: #ffffff !important;
        font-size: 52px !important;
        font-weight: 900 !important;
        line-height: 1.1;
        margin: 0 !important;
        letter-spacing: -1px;
        text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.85);
    }}

    /* SECCIÓN DE ACCESO */
    .banner-acceso {{
        background-color: #2b203a;
        padding: 15px;
        text-align: center;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 30px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
    }}
    .texto-acceso {{
        color: #e5b82b !important;
        font-size: 44px !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }}

    /* INPUTS DEL LOGIN */
    .stTextInput > div > div > input {{
        background-color: #ffffff !important;
        color: #150324 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 35px !important;
        padding: 14px 25px !important;
    }}
    
    /* PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #312d38 !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #e5b82b !important;
        font-weight: 800 !important;
        font-size: 19px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #1c0933 !important;
        border-bottom: 4px solid #e5b82b !important;
    }}

    /* Visibilidad de celdas dataframes */
    div[data-testid="stDataFrame"] div, div[data-testid="stDataEditor"] div {{
        color: #ffffff !important;
    }}
    
    /* REPLICA EXACTA DEL AVISO DE SEGURIDAD */
    .aviso-seguridad-box {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px;
        padding: 25px;
        border-top: 15px solid #e5b82b;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        margin-top: 20px;
        margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO DEL SISTEMA RENDERIZADO
st.markdown("""
    <div class="header-sistema">
        <h1 class="header-titulo">Sistema de gestión<br>de Patrimonio</h1>
    </div>
""", unsafe_allow_html=True)

def conectar():
    password_db = st.secrets.get("password", "AVNS_ytphqSAjobNIHWjlbex")
    return mysql.connector.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com", 
        user="avnadmin", 
        password=password_db, 
        port=18358, 
        database="viacrucis_2026"
    )

@st.cache_data(ttl=600)
def cargar_tabla_optimizado(nombre_tabla):
    conn_cache = conectar()
    try:
        df = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn_cache)
    finally:
        conn_cache.close()
    return df

# --- CONTROL DE ACCESO ---
if not st.session_state['autenticado']:
    st.markdown("""
        <div class="banner-acceso">
            <h2 class="texto-acceso">Acceso al sistema 🔒🔑</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col_cen, _ = st.columns([2, 1])
    with col_cen:
        with st.form("login"):
            user_input = st.text_input("Usuario 👤")
            pass_input = st.text_input("Contraseña 🔑", type="password")
            
            if st.form_submit_button("💥 INGRESAR"):
                db = conectar()
                cursor = db.cursor()
                query = "SELECT nombre_usuario, id_rol FROM usuarios WHERE nombre_usuario=%s AND clave=%s"
                cursor.execute(query, (user_input, pass_input))
                resultado = cursor.fetchone()
                db.close()
                
                if resultado:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_nom'] = resultado[0]
                    st.session_state['usuario_rol'] = resultado[1] 
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.sidebar.markdown(f"👤 **Usuario Activo:**\n### {st.session_state['usuario_nom']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

nombres_tabs = ["Personal 👥", "Economía 💵", "Inventario 📦"]
if st.session_state['usuario_rol'] == 1:
    nombres_tabs.append("Data 📝")

tabs = st.tabs(nombres_tabs)
db = conectar()

# --- TAB 0: PERSONAL ---
with tabs[0]:
    st.markdown("<h2 style='color:#e5b82b;'>Personal 👥</h2>", unsafe_allow_html=True)
    query_p = """
    SELECT p.Nombre, p.Apellido, p.Edad, per.Descripción AS Personaje, 
           r.Descripción AS Rol, pa.`Nombre Parroquia` AS Parroquia, 
           c.Descripción AS Comisión, p.teléfono AS Teléfono
    FROM participantes p
    JOIN parroquia pa ON p.id_parroquia = pa.id_parroquia
    JOIN comisiones c ON p.id_comision = c.id_comsion
    JOIN roles r ON p.id_rol = r.id_rol
    LEFT JOIN personajes per ON p.id_participante = per.id_participante
    """
    df_p = pd.read_sql(query_p, db)

    st.sidebar.header("🔍 Filtros")
    f_parroquia = st.sidebar.multiselect("Parroquia", options=df_p["Parroquia"].unique())
    f_rol = st.sidebar.multiselect("Rol/Personaje", options=df_p["Rol"].unique())
    f_comision = st.sidebar.multiselect("Comisión", options=df_p["Comisión"].unique())

    df_f = df_p.copy()
    if f_parroquia: df_f = df_f[df_f["Parroquia"].isin(f_parroquia)]
    if f_rol: df_f = df_f[df_f["Rol"].isin(f_rol)]
    if f_comision: df_f = df_f[df_f["Comisión"].isin(f_comision)]

    st.metric("Total Personas", len(df_f))
    st.dataframe(df_f, use_container_width=True, hide_index=True)

# --- TAB 1: ECONOMÍA ---
with tabs[1]:
    res_in = pd.read_sql("SELECT SUM(abono) as total FROM pago_patrocinantes", db)
    total_in = res_in['total'].iloc[0] or 0
    res_out = pd.read_sql("SELECT SUM(monto) as total FROM gastos", db)
    total_out = res_out['total'].iloc[0] or 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Total", f"{total_in} COP")
    c2.metric("Gastos Total", f"{total_out} COP")
    c3.metric("Saldo Neto", f"{total_in - total_out} COP")
    st.divider()

    try:
        q_estilo = """
            SELECT p.negocio AS Patrocinante, p.`monto a pagar` AS Pactado, 
                   IFNULL(SUM(pg.abono), 0) AS Abonado, (p.`monto a pagar` - IFNULL(SUM(pg.abono), 0)) AS Pendiente
            FROM patrocinantes p LEFT JOIN pago_patrocinantes pg ON p.id_patrocinante = pg.id_patrocinante
            GROUP BY p.id_patrocinante
        """
        df_pagos = pd.read_sql(q_estilo, db)
        filtro = st.selectbox("🔍 Estatus de pago:", ["Todos", "Sin abonos", "Abonos", "Cancelado"])
        if filtro == "Sin abonos": df_pagos = df_pagos[df_pagos['Abonado'] == 0]
        elif filtro == "Abonos": df_pagos = df_pagos[(df_pagos['Abonado'] > 0) & (df_pagos['Pendiente'] > 0)]
        elif filtro == "Cancelado": df_pagos = df_pagos[df_pagos['Pendiente'] <= 0]
        st.dataframe(df_pagos, use_container_width=True, hide_index=True)

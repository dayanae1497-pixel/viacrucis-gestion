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
if 'mostrar_descarga_pdf' not in st.session_state:
    st.session_state['mostrar_descarga_pdf'] = False

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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
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
/* INYECCIÓN DE ESTILOS AVANZADOS */
button[data-testid="stDataEditor-AddRowOverlay"],
.stDataEditor div[data-baseweb="table"] div,
.stDataEditor canvas {{
    cursor: default !important;
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

# --- FUNCIÓN PARA GENERAR EL PDF REPORTE CON FPDF (Sin Dependencias Complejas) ---
def generar_pdf_reporte_bytes(total_in, total_out, df_pagos, df_gastos):
    pdf = FPDF()
    pdf.add_page()
    
    # Fuentes y diseño elegante
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(50, 19, 84) # Morado Principal
    pdf.cell(0, 10, "REPORTE GENERAL DE PATRIMONIO Y ECONOMIA", 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "VIACRUCIS VIVIENTE 2026", 0, 1, "C")
    pdf.ln(3)
    
    # Fecha de generación
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, "R")
    pdf.ln(5)
    
    # 1. BALANCE GENERAL
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(181, 140, 36) # Dorado Accent
    pdf.cell(0, 8, "1. RESUMEN DE BALANCE FINANCIERO", 0, 1, "L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 8, f" Total Ingresos (Patrocinios):", 0, 0)
    pdf.cell(60, 8, f"{total_in:,.2f} COP", 0, 1)
    pdf.cell(60, 8, f" Total Egresos (Gastos):", 0, 0)
    pdf.cell(60, 8, f"{total_out:,.2f} COP", 0, 1)
    
    saldo = total_in - total_out
    pdf.set_font("Arial", "B", 11)
    pdf.cell(60, 8, f" Saldo Neto Actual:", 0, 0)
    if saldo >= 0:
        pdf.set_text_color(37, 141, 25) # Verde
    else:
        pdf.set_text_color(214, 48, 49) # Rojo
    pdf.cell(60, 8, f"{saldo:,.2f} COP", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)
    
    # Helper para caracteres especiales en FPDF estándar
    def clean_s(txt):
        return str(txt).encode('latin-1', 'ignore').decode('latin-1')
        
    # 2. TABLA DE PATROCINANTES
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(181, 140, 36)
    pdf.cell(0, 8, "2. ESTADO DE CUENTA DE PATROCINANTES", 0, 1, "L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(50, 19, 84)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(65, 7, "Patrocinante / Negocio", 1, 0, "C", True)
    pdf.cell(40, 7, "Pactado", 1, 0, "C", True)
    pdf.cell(45, 7, "Abonado", 1, 0, "C", True)
    pdf.cell(40, 7, "Pendiente", 1, 1, "C", True)
    
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(0, 0, 0)
    for _, row in df_pagos.iterrows():
        pdf.cell(65, 7, clean_s(row['Patrocinante']), 1, 0, "L")
        pdf.cell(40, 7, f"{row['Pactado']:,.2f} COP", 1, 0, "R")
        pdf.cell(45, 7, f"{row['Abonado']:,.2f} COP", 1, 0, "R")
        pdf.cell(40, 7, f"{row['Pendiente']:,.2f} COP", 1, 1, "R")
    
    # 3. TABLA DE GASTOS
    if not df_gastos.empty:
        pdf.add_page()
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(181, 140, 36)
        pdf.cell(0, 8, "3. DETALLE DE GASTOS / EGRESOS", 0, 1, "L")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        
        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(50, 19, 84)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(35, 7, "Fecha", 1, 0, "C", True)
        pdf.cell(105, 7, "Concepto del Gasto", 1, 0, "C", True)
        pdf.cell(50, 7, "Monto (COP)", 1, 1, "C", True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        for _, row in df_gastos.iterrows():
            pdf.cell(35, 7, str(row['Fecha']), 1, 0, "C")
            pdf.cell(105, 7, clean_s(row['Concepto']), 1, 0, "L")
            pdf.cell(50, 7, f"{row['Monto (COP)']:,.2f} COP", 1, 1, "R")
            
    pdf_out = pdf.output(dest='S')
    if isinstance(pdf_out, str):
        return pdf_out.encode('latin-1', 'replace')
    return pdf_out

# --- CONTROL DE ACCESO ---
if not st.session_state['autenticado']:
    st.markdown("""
    <div class="banner-acceso">
        <h2 class="texto-acceso">Acceso al sistema  🔒🔑 </h2>
    </div>
    """, unsafe_allow_html=True)

    col_cen, _ = st.columns([2, 1])
    with col_cen:
        with st.form("login"):
            user_input = st.text_input("Usuario  👤 ")
            pass_input = st.text_input("Contraseña  🔑 ", type="password")

            if st.form_submit_button(" 💥  INGRESAR"):
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
                    st.error(" ❌  Credenciales incorrectas.")
    st.stop() # CORRECCIÓN CRÍTICA

# --- INTERFAZ PRINCIPAL (Solo accesible autenticado) ---
st.sidebar.markdown(f" 👤  **Usuario Activo:**\n### {st.session_state['usuario_nom']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.session_state.mostrar_descarga_pdf = False
    st.rerun()

# --- BLOQUE INTEGRADO DE REPORTES PDF ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🖨️ Reportes del Sistema")
if st.sidebar.button("📊 Preparar Reporte PDF"):
    st.session_state.mostrar_descarga_pdf = True

if st.session_state.mostrar_descarga_pdf:
    try:
        db_rep = conectar()
        res_in_rep = pd.read_sql("SELECT SUM(abono) as total FROM pago_patrocinantes", db_rep)
        t_in = res_in_rep['total'].iloc[0] or 0
        res_out_rep = pd.read_sql("SELECT SUM(monto) as total FROM gastos", db_rep)
        t_out = res_out_rep['total'].iloc[0] or 0
        
        q_pags = """
        SELECT p.negocio AS Patrocinante, p.`monto a pagar` AS Pactado,
        IFNULL(SUM(pg.abono), 0) AS Abonado, (p.`monto a pagar` - IFNULL(SUM(pg.abono), 0)) AS Pendiente
        FROM patrocinantes p LEFT JOIN pago_patrocinantes pg ON p.id_patrocinante = pg.id_patrocinante
        GROUP BY p.id_patrocinante
        """
        df_pags_rep = pd.read_sql(q_pags, db_rep)
        df_gastos_rep = pd.read_sql("SELECT `fecha del gasto` as Fecha, concepto as Concepto, monto as `Monto (COP)` FROM gastos ORDER BY `fecha del gasto` DESC", db_rep)
        db_rep.close()
        
        pdf_bytes = generar_pdf_reporte_bytes(t_in, t_out, df_pags_rep, df_gastos_rep)
        
        st.sidebar.download_button(
            label="📥 ¡DESCARGAR REPORTE PDF!",
            data=pdf_bytes,
            file_name=f"Reporte_Patrimonio_Viacrucis_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            key="btn_descarga_pdf_real"
        )
    except Exception as e:
        st.sidebar.error(f"Error generando PDF: {e}")

nombres_tabs = ["Personal  👥 ", "Economía  💵 ", "Inventario  📦 "]
if st.session_state['usuario_rol'] == 1:
    nombres_tabs.append("Data  📝 ")
tabs = st.tabs(nombres_tabs)

db = conectar()

# --- TAB 0: PERSONAL ---
with tabs[0]:
    st.markdown("<h2 style='color:#e5b82b;'>Personal  👥 </h2>", unsafe_allow_html=True)
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
    st.sidebar.header(" 🔍  Filtros")
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
    c1.metric("Ingresos", f"{total_in} COP")
    c2.metric("Gastos", f"{total_out} COP")
    c3.metric("Saldo", f"{total_in - total_out} COP")
    st.divider()

    try:
        q_estilo = """
        SELECT
        p.negocio AS Patrocinante,
        p.`monto a pagar` AS Pactado,
        IFNULL(SUM(pg.abono), 0) AS Abonado,
        (p.`monto a pagar` - IFNULL(SUM(pg.abono), 0)) AS Pendiente
        FROM patrocinantes p
        LEFT JOIN pago_patrocinantes pg ON p.id_patrocinante = pg.id_patrocinante
        GROUP BY p.id_patrocinante
        """
        df_pagos = pd.read_sql(q_estilo, db)

        filtro = st.selectbox(
            " 🔍  Filtrar por estatus de pago:",
            ["Todos", "Sin abonos", "Abonos", "Cancelado"]
        )

        if filtro == "Sin abonos":
            df_pagos = df_pagos[df_pagos['Abonado'] == 0]
        elif filtro == "Abonos":
            df_pagos = df_pagos[(df_pagos['Abonado'] > 0) & (df_pagos['Pendiente'] > 0)]
        elif filtro == "Cancelado":
            df_pagos = df_pagos[df_pagos['Pendiente'] <= 0]

        def resaltar_estatus(row):
            if row['Abonado'] == 0:
                return ['background-color: #ff7c70; color: black'] * len(row)
            elif row['Pendiente'] <= 0:
                return ['background-color: #258d19; color: black'] * len(row)
            else:
                return ['background-color: #fcf75e; color: black'] * len(row)
        st.subheader(f" 📋  Detalle: {filtro}")

        st.caption(" 🟩  Pagó todo &nbsp;&nbsp;&nbsp;&nbsp;  🟨  Abonó &nbsp;&nbsp;&nbsp;&nbsp;  🟥  No ha abonado")

        st.dataframe(
            df_pagos.style.apply(resaltar_estatus, axis=1).format({
                "Pactado": "{:.2f} COP",
                "Abonado": "{:.2f} COP",
                "Pendiente": "{:.2f} COP"
            }),
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.error(f"Error visualizando los colores: {e}")
        
    st.subheader(" 📊  Detalle de Egresos")
    try:
        df_gastos_tabla = pd.read_sql("SELECT `fecha del gasto` as Fecha, concepto as Concepto, monto as `Monto (COP)` FROM gastos ORDER BY `fecha del gasto` DESC", db)
        if not df_gastos_tabla.empty:
            st.dataframe(df_gastos_tabla, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay gastos registrados.")
    except Exception as e:
        st.error(f"No se pudo cargar la tabla de gastos: {e}")

# --- TAB 2: INVENTARIO ---
with tabs[2]:
    cv, cu = st.columns(2)
    with cv:
        st.subheader(" 👕  Vestuario")
        query_v = """
        SELECT v.piezas, v.descripcion, pa.`Nombre Parroquia`
        FROM vestuario_final v
        JOIN parroquia pa ON v.id_parroquia = pa.id_parroquia
        """
        st.dataframe(pd.read_sql(query_v, db), hide_index=True)
    with cu:
        st.subheader(" 🛠 ️ Utilería")
        st.dataframe(pd.read_sql("SELECT objeto, cantidad, descripcion FROM utileria", db), hide_index=True)

# --- TAB 3: DATA (PANEL CRÍTICO REESTRUCTURADO) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        st.header(" 📝  Registro de Datos")
        opc = st.radio("¿Qué deseas registrar?",
            ["Gasto Nuevo", "Abono de Patrocinante", "Nuevo Patrocinante", "Nuevo Participante", "Nuevo Personaje"],
            horizontal=True, key="radio_registro_datos")

        if opc == "Gasto Nuevo":
            with st.form("nuevo_gasto"):
                con = st.text_input("Concepto")
                mon = st.number_input("Monto ($)", min_value=0.0)
                fec = st.date_input("Fecha")
                if st.form_submit_button("Guardar Gasto"):
                    cur = db.cursor()
                    cur.execute("INSERT INTO gastos (concepto, monto, `fecha del gasto`) VALUES (%s, %s, %s)", (con, mon, fec))
                    db.commit()
                    cur.close()
                    st.success(" ✅  Gasto guardado con éxito.")
                    st.rerun()

        elif opc == "Abono de Patrocinante":
            df_pats = pd.read_sql("SELECT id_patrocinante, negocio FROM patrocinantes", db)
            with st.form("nuevo_abono"):
                p_id = st.selectbox("Negocio", options=df_pats['id_patrocinante'],
                    format_func=lambda x: df_pats[df_pats['id_patrocinante']==x]['negocio'].iloc[0])
                fecha_pago = st.date_input("Fecha del Abono")
                abo = st.number_input("Monto Abono ($)", min_value=0.0)

                if st.form_submit_button("Registrar Abono"):
                    try:
                        cur = db.cursor()
                        sql = "INSERT INTO pago_patrocinantes (id_patrocinante, abono, `fecha de abono`) VALUES (%s, %s, %s)"
                        valores = (int(p_id) if p_id else None, float(abo), fecha_pago)
                        cur.execute(sql, valores)
                        db.commit()
                        cur.close()
                        st.success(f" ✅  Abono de ${abo} registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f" ❌  Error: {e}")
                        
        elif opc == "Nuevo Patrocinante":
            with st.form("form_nuevo_patro"):
                nombre_negocio = st.text_input("Nombre del Negocio o Persona")
                telf = st.text_input("Teléfono de contacto")
                monto_pactado = st.number_input("Monto a Pagar (Pacto en $)", min_value=0.0)
                if st.form_submit_button("Registrar Nuevo Patrocinante"):
                    if nombre_negocio:
                        cur = db.cursor()
                        sql = "INSERT INTO patrocinantes (negocio, teléfono, `monto a pagar`) VALUES (%s, %s, %s)"
                        cur.execute(sql, (nombre_negocio, telf, monto_pactado))
                        db.commit()
                        cur.close()
                        st.success(f" ✅   ¡ {nombre_negocio} agregado!")
                        st.rerun()
                    else:
                        st.error("Mano, ponle el nombre al negocio por lo menos.")

        elif opc == "Nuevo Participante":
            df_com = pd.read_sql("SELECT id_comsion, Descripción FROM comisiones", db)
            df_par = pd.read_sql("SELECT id_parroquia, `Nombre Parroquia` FROM parroquia", db)
            df_rol = pd.read_sql("SELECT id_rol, Descripción FROM roles", db)
            with st.form("form_nuevo_participante"):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nombre")
                    ape = st.text_input("Apellido")
                    eda = st.number_input("Edad", min_value=0)
                with col2:
                    telf_p = st.text_input("Teléfono")
                    par_id = st.selectbox("Parroquia", options=df_par['id_parroquia'],
                        format_func=lambda x: df_par[df_par['id_parroquia']==x]['Nombre Parroquia'].iloc[0])
                    com_id = st.selectbox("Comisión", options=df_com['id_comsion'],
                        format_func=lambda x: df_com[df_com['id_comsion']==x]['Descripción'].iloc[0])

                rol_id = st.selectbox("Rol/Personaje", options=df_rol['id_rol'],
                    format_func=lambda x: df_rol[df_rol['id_rol']==x]['Descripción'].iloc[0])
                if st.form_submit_button("Registrar Participante"):
                    try:
                        cur = db.cursor()
                        sql = """INSERT INTO participantes (Nombre, Apellido, Edad, teléfono, id_comision, id_parroquia, id_rol)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                        cur.execute(sql, (nom, ape, int(eda) if eda else 0, telf_p,
                            int(com_id) if com_id else None,
                            int(par_id) if par_id else None,
                            int(rol_id) if rol_id else None))
                        db.commit()
                        cur.close()
                        st.success(f" ✅  {nom} {ape} ha sido registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f" ❌  Error en base de datos: {e}")

        elif opc == "Nuevo Personaje":
            try:
                df_participantes = pd.read_sql("SELECT id_participante, Nombre, Apellido FROM participantes", db)
                df_participantes['Nombre Completo'] = df_participantes['Nombre'] + " " + df_participantes['Apellido']
                st.subheader(" 🎭  Asignar Papel del Elenco")
                with st.form("form_personaje"):
                    p_id = st.selectbox("Seleccionar Participante", options=df_participantes['id_participante'],
                        format_func=lambda x: df_participantes[df_participantes['id_participante']==x]['Nombre Completo'].iloc[0])
                    nombre_papel = st.text_input("Nombre del Personaje")
                    if st.form_submit_button("Guardar Personaje"):
                        cur = db.cursor()
                        sql = "INSERT INTO personajes (Descripción, id_participante) VALUES (%s, %s)"
                        cur.execute(sql, (nombre_papel, int(p_id) if p_id else None))
                        db.commit()
                        cur.close()
                        st.success(f" ✅   ¡ {nombre_papel} asignado correctamente!")
                        st.rerun()
            except Exception as e:
                st.error(f" ⚠ ️ Hubo un detalle: {e}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#e5b82b;'>Panel de Control de Datos  ⚙ ️</h2>", unsafe_allow_html=True)

        tabla_maestra = st.selectbox("Selecciona la tabla a editar:", ["Participantes", "Gastos", "Vestuario", "Patrocinantes"], key="selector_tabla_critica")
        mapping = {"Participantes": "participantes", "Gastos": "gastos", "Vestuario": "vestuario_final", "Patrocinantes": "patrocinantes"}
        nombre_tabla_db = mapping[tabla_maestra]

        if "tabla_actual" not in st.session_state or st.session_state.get("nombre_tabla_anterior") != nombre_tabla_db:
            df_original = pd.read_sql(f"SELECT * FROM {nombre_tabla_db}", db)
            st.session_state.tabla_actual = df_original.copy()
            st.session_state.backup_data = df_original.copy()
            st.session_state.nombre_tabla_anterior = nombre_tabla_db
            st.session_state.bloqueo_advertencia = False

        if st.session_state.get("guardado_exitoso"):
            st.success(" 🎉  ¡Información sincronizada en la Base de Datos!")
            del st.session_state["guardado_exitoso"]

        if st.session_state.get("cambios_revertidos"):
            st.warning(" 🔄  Cambios revocados. Se restauró la información original de manera segura.")
            del st.session_state["cambios_revertidos"]

        if not st.session_state.get("bloqueo_advertencia", False):
            version_actual = st.session_state.editor_version
            key_dinamica = f"editor_{nombre_tabla_db}_{version_actual}"
            config_columnas = {}

            if nombre_tabla_db == "participantes":
                df_par_map = pd.read_sql("SELECT id_parroquia, `Nombre Parroquia` FROM parroquia", db)
                df_rol_map = pd.read_sql("SELECT id_rol, Descripción FROM roles", db)
                df_com_map = pd.read_sql("SELECT id_comsion, Descripción FROM comisiones", db)
                config_columnas = {
                    "id_participante": st.column_config.NumberColumn("ID", disabled=True),
                    "Nombre": st.column_config.TextColumn("Nombre"),
                    "Apellido": st.column_config.TextColumn("Apellido"),
                    "Edad": st.column_config.NumberColumn("Edad"),
                    "id_parroquia": st.column_config.SelectboxColumn("Parroquia", options=df_par_map["id_parroquia"].tolist(),
                        format_func=lambda x: df_par_map[df_par_map["id_parroquia"] == x]["Nombre Parroquia"].iloc[0] if x in df_par_map["id_parroquia"].values else f"ID: {x}"),
                    "id_rol": st.column_config.SelectboxColumn("Rol", options=df_rol_map["id_rol"].tolist(),
                        format_func=lambda x: df_rol_map[df_rol_map["id_rol"] == x]["Descripción"].iloc[0] if x in df_rol_map["id_rol"].values else f"ID: {x}"),
                    "id_comision": st.column_config.SelectboxColumn("Comisión", options=df_com_map["id_comsion"].tolist(),
                        format_func=lambda x: df_com_map[df_com_map["id_comsion"] == x]["Descripción"].iloc[0] if x in df_com_map["id_comsion"].values else f"ID: {x}"),
                    "teléfono": st.column_config.TextColumn("Teléfono")
                }

            elif nombre_tabla_db == "vestuario_final":
                df_per_map = pd.read_sql("SELECT id_personaje, Descripción FROM personajes", db)
                df_par_map = pd.read_sql("SELECT id_parroquia, `Nombre Parroquia` FROM parroquia", db)
                config_columnas = {
                    "id_vestuario": st.column_config.NumberColumn("ID", disabled=True),
                    "id_personaje": st.column_config.SelectboxColumn("Personaje / Papel", options=df_per_map["id_personaje"].tolist(),
                        format_func=lambda x: df_per_map[df_per_map["id_personaje"] == x]["Descripción"].iloc[0] if x in df_per_map["id_personaje"].values else f"ID: {x}"),
                    "piezas": st.column_config.NumberColumn("Piezas", min_value=1),
                    "descripcion": st.column_config.TextColumn("Descripción Vestuario"),
                    "id_parroquia": st.column_config.SelectboxColumn("Parroquia Dueña", options=df_par_map["id_parroquia"].tolist(),
                        format_func=lambda x: df_par_map[df_par_map["id_parroquia"] == x]["Nombre Parroquia"].iloc[0] if x in df_par_map["id_parroquia"].values else f"ID: {x}")
                }

            df_editado = st.data_editor(st.session_state.tabla_actual, num_rows="dynamic", use_container_width=True, hide_index=True, column_config=config_columnas, key=key_dinamica)
            cambios = st.session_state.get(key_dinamica, {})
            hubo_eliminacion = len(cambios.get("deleted_rows", [])) > 0
            hubo_modificacion = len(cambios.get("edited_rows", {})) > 0
            hubo_adicion = len(cambios.get("added_rows", [])) > 0

            if hubo_eliminacion or hubo_modificacion:
                if nombre_tabla_db == "participantes": col_critica = "Nombre"
                elif nombre_tabla_db == "vestuario_final": col_critica = "descripcion"
                elif nombre_tabla_db == "gastos": col_critica = "concepto"
                elif nombre_tabla_db == "patrocinantes": col_critica = "negocio"
                else: col_critica = df_editado.columns[1] if len(df_editado.columns) > 1 else df_editado.columns[0]

                df_limpio = df_editado.dropna(subset=[col_critica])
                df_limpio = df_limpio[df_limpio[col_critica].astype(str).str.strip() != ""]
                st.session_state.df_congelado_cambios = df_limpio.copy()
                st.session_state.bloqueo_advertencia = True
                st.rerun()

            elif hubo_adicion:
                st.session_state.tabla_actual = df_editado.copy()

        else:
            st.markdown(f"""
            <div style="background-color: #ffeaa7; padding: 20px; border-radius: 10px; border-left: 8px solid #e17055; margin-bottom: 20px;">
                <p style="color: #d63031; font-weight: bold; font-size: 14px; text-align: center; margin: 0; letter-spacing: 2px;"> ⚠ ️ AVISO DE SEGURIDAD CRÍTICO  ⚠ ️</p>
                <h2 style="color: #000000; font-size: 28px; font-weight: 800; text-align: center; margin-top: 5px; margin-bottom: 10px;">¿Confirmar alteración de datos?</h2>
                <p style="color: #2f3542; font-size: 16px; text-align: center; font-weight: bold; margin-bottom: 10px;">
                    Has editado o eliminado registros existentes en la tabla '{tabla_maestra}'.<br>El sistema mantendrá bloqueada la pantalla hasta que decidas:
                </p>
            </div>
            """, unsafe_allow_html=True)

            col_si, col_no = st.columns(2)
            datos_nuevos = st.session_state.get("df_congelado_cambios")

            with col_si:
                if st.button(" 🟢  SÍ, CONFIRMAR Y APLICAR CAMBIOS", use_container_width=True):
                    if datos_nuevos is not None:
                        cur = db.cursor()
                        try:
                            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
                            columna_id = datos_nuevos.columns[0]

                            if nombre_tabla_db == "participantes": col_critica = "Nombre"
                            elif nombre_tabla_db == "vestuario_final": col_critica = "descripcion"
                            elif nombre_tabla_db == "gastos": col_critica = "concepto"
                            elif nombre_tabla_db == "patrocinantes": col_critica = "negocio"
                            else: col_critica = datos_nuevos.columns[1] if len(datos_nuevos.columns) > 1 else datos_nuevos.columns[0]

                            datos_filtrados = datos_nuevos.dropna(subset=[col_critica])
                            datos_filtrados = datos_filtrados[datos_filtrados[col_critica].astype(str).str.strip() != ""]

                            cur.execute(f"SELECT `{columna_id}` FROM {nombre_tabla_db}")
                            ids_en_db = [row[0] for row in cur.fetchall()]
                            ids_en_editor = datos_filtrados[columna_id].dropna().tolist()

                            ids_a_borrar = [id_db for id_db in ids_en_db if id_db not in ids_en_editor]
                            if ids_a_borrar:
                                format_strings = ','.join(['%s'] * len(ids_a_borrar))
                                cur.execute(f"DELETE FROM {nombre_tabla_db} WHERE `{columna_id}` IN ({format_strings})", tuple(ids_a_borrar))

                            cols = ", ".join([f"`{c}`" for c in datos_filtrados.columns])
                            placeholders = ", ".join(["%s"] * len(datos_filtrados.columns))
                            updates = ", ".join([f"`{c}` = VALUES(`{c}`)" for c in datos_filtrados.columns if c != columna_id])
                            sql_save = f"INSERT INTO {nombre_tabla_db} ({cols}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"

                            lote_valores = []
                            for _, row in datos_filtrados.iterrows():
                                valores_fila = tuple(None if pd.isna(v) else v for v in row)
                                lote_valores.append(valores_fila)

                            if lote_valores:
                                cur.executemany(sql_save, lote_valores)

                            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            db.commit()

                            st.session_state.tabla_actual = datos_filtrados.copy()
                            st.session_state.backup_data = datos_filtrados.copy()
                            if "df_congelado_cambios" in st.session_state:
                                del st.session_state["df_congelado_cambios"]

                            st.session_state.editor_version += 1
                            st.session_state.guardado_exitoso = True
                            st.session_state.bloqueo_advertencia = False

                        except Exception as err:
                            db.rollback()
                            try: cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            except: pass
                            st.error(f" ❌  Error crítico al procesar la actualización: {err}")
                        finally:
                            cur.close()
                        st.rerun()

            with col_no:
                if st.button(" 🔴  NO, REVERTIR ANOMALÍAS", use_container_width=True):
                    st.session_state.tabla_actual = st.session_state.backup_data.copy()
                    if "df_congelado_cambios" in st.session_state:
                        del st.session_state["df_congelado_cambios"]
                    st.session_state.editor_version += 1
                    st.session_state.cambios_revertidos = True
                    st.session_state.bloqueo_advertencia = False
                    st.rerun()

# --- CIERRE DE CONEXIÓN GLOBAL ---
if 'db' in locals() and db.is_connected():
    db.close()

import streamlit as st
import pandas as pd
import mysql.connector
from fpdf import FPDF 
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# --- CONTROLADORES DE ESTILO CSS PARA CALCAR TU MAQUETA ---
st.markdown("""
    <style>
    /* Importación de la fuente League Spartan de tus imágenes */
    @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;700;800;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, label {
        font-family: 'League Spartan', sans-serif !important;
    }

    /* Fondo degradado púrpura envolvente basado en tu flyer */
    .stApp {
        background: linear-gradient(180deg, #321354 0%, #1c0933 50%, #0d021a 100%) !important;
    }

    /* ENCABEZADO: Título en bloque oscuro con tipografía en blanco limpio */
    .header-sistema {
        background-color: #150324;
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 4px solid #b58c24;
    }
    .header-titulo {
        color: #ffffff !important;
        font-size: 45px !important;
        font-weight: 900 !important;
        line-height: 1.1;
        margin: 0 !important;
        letter-spacing: -1px;
    }

    /* SECCIÓN DE ACCESO: Franja pincelada oscura con letras amarillas intensas */
    .banner-acceso {
        background-color: #2b203a;
        padding: 15px;
        text-align: center;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 30px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
    }
    .texto-acceso {
        color: #e5b82b !important;
        font-size: 44px !important;
        font-weight: 900 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }

    /* INPUTS DEL LOGIN: Cajas ovaladas blancas con texto interior oscuro */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #150324 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 35px !important;
        padding: 14px 25px !important;
        border: 2px solid transparent !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #e5b82b !important;
    }
    
    /* PESTAÑAS (TABS): Menú horizontal gris oscuro con fuentes amarillas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #312d38 !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e5b82b !important;
        font-weight: 800 !important;
        font-size: 19px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1c0933 !important;
        border-bottom: 4px solid #e5b82b !important;
    }

    /* ARREGLO DE VISIBILIDAD DE TABLAS: Mantiene el fondo oscuro pero fuerza las fuentes a blanco legible */
    div[data-testid="stDataFrame"] div, div[data-testid="stDataEditor"] div {
        color: #ffffff !important;
    }
    
    /* CAJA EMERGENTE DE SEGURIDAD CALCADA */
    .aviso-seguridad-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px;
        padding: 25px;
        border-top: 15px solid #e5b82b; /* Barra superior amarilla */
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO DEL SISTEMA
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

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- LÓGICA DE LOGIN ---
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

# --- MENÚ DE NAVEGACIÓN ---
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
        filtro = st.selectbox("🔍 Estatus de pago:", ["Todos", "Sin abonos", "Abonos", "Cancelado"])

        if filtro == "Sin abonos": df_pagos = df_pagos[df_pagos['Abonado'] == 0]
        elif filtro == "Abonos": df_pagos = df_pagos[(df_pagos['Abonado'] > 0) & (df_pagos['Pendiente'] > 0)]
        elif filtro == "Cancelado": df_pagos = df_pagos[df_pagos['Pendiente'] <= 0]

        st.dataframe(df_pagos, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

    st.subheader("📊 Tabla Detallada de Egresos")
    df_gastos_tabla = pd.read_sql("SELECT `fecha del gasto` as Fecha, concepto as Concepto, monto as `Monto (COP)` FROM gastos ORDER BY `fecha del gasto` DESC", db)
    st.dataframe(df_gastos_tabla, use_container_width=True, hide_index=True)

# --- TAB 2: INVENTARIO ---
with tabs[2]:
    cv, cu = st.columns(2)
    with cv:
        st.subheader("👕 Vestuario")
        query_v = """
        SELECT v.piezas, v.descripcion, pa.`Nombre Parroquia` 
        FROM vestuario_final v 
        JOIN parroquia pa ON v.id_parroquia = pa.id_parroquia
        """
        st.dataframe(pd.read_sql(query_v, db), hide_index=True)
    with cu:
        st.subheader("🛠️ Utilería")
        st.dataframe(pd.read_sql("SELECT objeto, cantidad, descripcion FROM utileria", db), hide_index=True)

# --- TAB 3: DATA (EDICIÓN MASIVA + LOGICA DE ALERTA CORREGIDA) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        st.markdown("<h2 style='color:#e5b82b;'>Panel de Control de Datos ⚙️</h2>", unsafe_allow_html=True)
        
        tabla_maestra = st.selectbox(
            "Selecciona la tabla a editar:",
            ["Participantes", "Gastos", "Vestuario", "Patrocinantes"]
        )
        
        mapping = {"Participantes": "participantes", "Gastos": "gastos", "Vestuario": "vestuario_final", "Patrocinantes": "patrocinantes"}
        nombre_tabla_db = mapping[tabla_maestra]
        
        try:
            query = f"SELECT * FROM {nombre_tabla_db}"
            df_maestro = pd.read_sql(query, db)
            
            # Editor interactivo: Almacenamos los cambios realizados en el componente
            df_editado = st.data_editor(df_maestro, num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_maestro")

            # --- CONTROL DE ESTADO: DETERMINAR SI HUBO MODIFICACIONES REALES ---
            cambios = st.session_state.editor_maestro
            hubo_cambios = len(cambios.get("edited_rows", {})) > 0 or len(cambios.get("added_rows", {})) > 0 or len(cambios.get("deleted_rows", {})) > 0

            # SI HUBO CAMBIOS, ENTONCES Y SOLO ENTONCES SE DESPLIEGA EL POP-UP DE SEGURIDAD
            if hubo_cambios:
                st.markdown(f"""
                <div class="aviso-seguridad-box">
                    <p style="color: #ea2027; font-weight: bold; font-size: 14px; text-align: center; margin: 0; letter-spacing: 2px;">⚠️ AVISO DE SEGURIDAD ⚠️</p>
                    <h2 style="color: #000000; font-size: 34px; font-weight: 800; text-align: center; margin-top: 5px; margin-bottom: 10px;">¿Confirmar cambios?</h2>
                    <p style="color: #2f3542; font-size: 17px; text-align: center; font-weight: bold; margin-bottom: 20px;">
                        Has editado datos sensibles en la tabla '{tabla_maestra}'.<br>¿Deseas aplicar los cambios o revertir?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Pasarela de botones funcionales de confirmación
                col_si, col_no = st.columns(2)
                with col_si:
                    proceder = st.button("🟢 SÍ, CONFIRMAR CAMBIOS", use_container_width=True)
                with col_no:
                    revertir = st.button("🔴 NO, REVERTIR", use_container_width=True)

                if proceder:
                    cur = db.cursor()
                    try:
                        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
                        cur.execute(f"DELETE FROM {nombre_tabla_db}") 
                        
                        cols = ", ".join([f"`{c}`" for c in df_editado.columns])
                        placeholders = ", ".join(["%s"] * len(df_editado.columns))
                        sql_insert = f"INSERT INTO {nombre_tabla_db} ({cols}) VALUES ({placeholders})"
                        
                        for _, row in df_editado.iterrows():
                            valores = tuple(None if pd.isna(v) else v for v in row)
                            cur.execute(sql_insert, valores)
                        
                        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                        db.commit()
                        st.success("🎉 ¡Cambios guardados con éxito!")
                        st.rerun()
                    except Exception as err:
                        db.rollback()
                        st.error(f"Error al guardar: {err}")
                    finally:
                        cur.close()
                        
                if revertir:
                    st.info("Acción cancelada de forma segura.")
                    st.rerun()

        except Exception as e:
            st.error(f"Error al procesar el panel: {e}")

        st.divider()

        # --- SECCIÓN 2: GENERACIÓN DE PDF ---
        st.subheader("📄 Reporte Oficial Viacrucis 2026")
        
        def generar_reporte_final(df_p, df_v, df_g, df_pat):
            class PDF(FPDF):
                def header(self):
                    self.set_fill_color(30, 41, 59) 
                    self.rect(0, 0, 210, 35, 'F')
                    self.set_text_color(255, 255, 255)
                    self.set_font('Arial', 'B', 16)
                    self.cell(0, 10, 'SISTEMA DE GESTIÓN VIACRUCIS 2026', 0, 1, 'C')
                    self.ln(15)

            pdf = PDF()
            pdf.add_page()
            
            pdf.set_text_color(0)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'LISTADO DE PARTICIPANTES', 0, 1)
            
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(60, 8, 'Nombre Completo', 1, 0, 'C', 1)
            pdf.cell(40, 8, 'Teléfono', 1, 0, 'C', 1)
            pdf.cell(90, 8, 'Parroquia', 1, 1, 'C', 1)

            pdf.set_font('Arial', '', 8)
            for _, row in df_p.iterrows():
                nombre_completo = f"{row.get('Nombre', '')} {row.get('Apellido', '')}"
                telefono = str(row.get('teléfono', row.get('teléfono', 'S/N')))
                parroquia = str(row.get('id_parroquia', 'N/A'))

                pdf.cell(60, 7, nombre_completo[:35], 1)
                pdf.cell(40, 7, telefono, 1, 0, 'C')
                pdf.cell(90, 7, parroquia[:50], 1, 1)

            pdf.ln(10)
            return pdf.output(dest='S')

        if st.button("🚀 Preparar Reporte Maestro"):
            try:
                with st.spinner("Compilando toda la información..."):
                    df_p_raw = pd.read_sql("SELECT * FROM participantes", db)
                    df_v_raw = pd.read_sql("SELECT * FROM vestuario_final", db)
                    df_g_raw = pd.read_sql("SELECT * FROM gastos", db)
                    df_pat_raw = pd.read_sql("SELECT * FROM patrocinantes", db)
                    
                    pdf_raw = generar_reporte_final(df_p_raw, df_v_raw, df_g_raw, df_pat_raw)
                    st.success("✅ ¡Reporte completo generado!")
                    st.download_button(
                        label="⬇️ Descargar Reporte PDF",
                        data=bytes(pdf_raw),
                        file_name=f"Reporte_Viacrucis_Final_{datetime.now().strftime('%d_%m')}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error al compilar el reporte: {e}")

# CIERRE DE CONEXIÓN
if db.is_connected():
    db.close()

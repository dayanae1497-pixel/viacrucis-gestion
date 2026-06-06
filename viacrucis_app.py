import streamlit as st
import pandas as pd
import mysql.connector
from fpdf import FPDF 
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS PARA ADAPTARLO A LAS IMÁGENES ---
st.markdown("""
    <style>
    /* Fondo general de la app con un sutil degradado púrpura claro */
    .stApp {
        background: linear-gradient(180deg, #eae2f8 0%, #ffffff 100%);
    }
    
    /* Encabezado Principal (Banner Púrpura de las imágenes) */
    .banner-principal {
        background-color: #2b084b;
        padding: 25px;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        border-bottom: 5px solid #ffd700;
    }
    .banner-titulo {
        color: #ffffff !important;
        font-family: 'Arial Black', Gadget, sans-serif;
        font-size: 32px !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .banner-subtitulo {
        color: #ffd700 !important;
        font-size: 18px !important;
        margin-top: 5px !important;
        font-weight: bold;
    }
    
    /* Títulos de secciones estilo "Acceso al sistema" */
    .seccion-titulo {
        background: #4a3b63;
        color: #ffd700 !important;
        padding: 12px;
        border-radius: 4px;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Inputs del login adaptados al estilo visual */
    .stTextInput>div>div>input {
        background-color: #5c3b91 !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 10px 20px !important;
        border: 1px solid #ffd700 !important;
    }
    .stTextInput>div>div>input::placeholder {
        color: #ddd !important;
    }
    
    /* Estilo de los Tabs para que parezcan el menú de la imagen */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #38343c;
        padding: 5px;
        border-radius: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ffd700 !important;
        font-weight: bold !important;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #5c3b91 !important;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# BANNER SUPERIOR PERMANENTE (Reemplaza el cuadro marrón anterior)
st.markdown("""
    <div class="banner-principal">
        <h1 class="banner-titulo">✝️ Sistema de gestión de Patrimonio</h1>
        <p class="banner-subtitulo">VIACRUCIS VIVIENTE 2026</p>
    </div>
    <br>
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

# --- LOGICA DE LOGIN ESTILIZADA ---
if not st.session_state['autenticado']:
    st.markdown('<div class="seccion-titulo">Acceso al sistema 🔒🔑</div>', unsafe_allow_html=True)
    
    # Contenedor centrado para el formulario
    col_login, _ = st.columns([2, 1])
    with col_login:
        with st.form("login"):
            user_input = st.text_input("Usuario 👤", placeholder="Introduce tu usuario")
            pass_input = st.text_input("Contraseña 🔑", type="password", placeholder="••••••••")
            
            if st.form_submit_button("Ingresar"):
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

# --- INTERFAZ DEL SISTEMA AUTENTICADO ---
st.sidebar.markdown(f"👤 **Usuario:** {st.session_state['usuario_nom']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

nombres_tabs = ["👥 Personal", "💰 Economía", "📦 Inventario"]
if st.session_state['usuario_rol'] == 1:
    nombres_tabs.append("✍️ Data") # Renombrado a 'Data' como en tu mockup

tabs = st.tabs(nombres_tabs)
db = conectar()

# --- TAB 0: PERSONAL ---
with tabs[0]:
    st.header("Lista de Participantes")
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

    st.sidebar.header("🔍 Filtros de Lista")
    f_parroquia = st.sidebar.multiselect("Filtrar por Parroquia", options=df_p["Parroquia"].unique())
    f_rol = st.sidebar.multiselect("Filtrar por Rol/Personaje", options=df_p["Rol"].unique())
    f_comision = st.sidebar.multiselect("Filtrar por Comisión", options=df_p["Comisión"].unique())

    df_f = df_p.copy()
    if f_parroquia: df_f = df_f[df_f["Parroquia"].isin(f_parroquia)]
    if f_rol: df_f = df_f[df_f["Rol"].isin(f_rol)]
    if f_comision: df_f = df_f[df_f["Comisión"].isin(f_comision)]

    st.metric("Total Personas en esta lista", len(df_f))
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
            "🔍 Filtrar por estatus de pago:",
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

        st.subheader(f"📋 Detalle: {filtro}")
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

    st.subheader("📊 Detalle de Egresos")
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

# --- TAB 3: DATA (PANEL DE CONTROL CON PASARELA DE SEGURIDAD) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        st.header("🎛️ Panel de Control Total")
        
        # --- SECCIÓN 1: EDICIÓN DE TABLAS ---
        tabla_maestra = st.selectbox(
            "Selecciona la base de datos que deseas gestionar:",
            ["Participantes", "Gastos", "Vestuario", "Patrocinantes"]
        )
        
        mapping = {
            "Participantes": "participantes",
            "Gastos": "gastos",
            "Vestuario": "vestuario_final",
            "Patrocinantes": "patrocinantes"
        }
        
        nombre_tabla_db = mapping[tabla_maestra]
        
        try:
            query = f"SELECT * FROM {nombre_tabla_db}"
            df_maestro = pd.read_sql(query, db)
            
            st.subheader(f"Edición Masiva: {tabla_maestra}")
            st.info("💡 Haz doble clic para editar. Para eliminar, selecciona la fila y pulsa 'Delete'.")

            df_editado = st.data_editor(
                df_maestro, 
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=f"editor_{nombre_tabla_db}"
            )

            # --- CORRESPONDIENTE AVISO DE SEGURIDAD SOLICITADO ---
            st.markdown("---")
            st.warning(f"⚠️ **Atención:** Guardar cambios ejecutará una sobrescritura completa en la tabla `{nombre_tabla_db}`. Asegúrate de verificar los datos antes de proceder.")
            
            # Double check interactivo obligatorio para habilitar el botón de guardado
            confirmacion = st.toggle(f"Entiendo los riesgos y confirmo que deseo modificar la tabla {tabla_maestra}")

            if st.button(f"💾 Guardar Cambios en {tabla_maestra}", disabled=not confirmacion):
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
                    st.success(f"✅ ¡{tabla_maestra} actualizada con éxito!")
                    st.rerun()
                except Exception as err:
                    db.rollback()
                    st.error(f"Error al guardar: {err}")
                finally:
                    cur.close()

        except Exception as e:
            st.error(f"Error al cargar datos: {e}")

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
            
            # --- SECCIÓN: ELENCO ---
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

            # --- SECCIÓN: VESTUARIO ---
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'CONTROL DE VESTUARIO', 0, 1)
            
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(255, 235, 235)
            pdf.cell(25, 4, 'Personaje', 1, 0, 'C', 1)
            pdf.cell(25, 4, 'Piezas', 1, 0, 'C', 1)
            pdf.cell(120, 4, 'Descripción', 1, 0, 'C', 1)
            pdf.cell(25, 4, 'Parroquia', 1, 1, 'C', 1)
            
            pdf.set_font('Arial', '', 8)
            for _, row in df_v.iterrows():
                Personaje = str(row.get('id_personaje', 'N/A'))
                Piezas = str(row.get('piezas', 'N/A'))
                Descripción = str(row.get('descripcion', 'N/A'))
                Parroquia = str(row.get('id_parroquia', 'N/A'))
                
                pdf.cell(25, 3, Personaje, 1, 0, 'C', 1)
                pdf.cell(25, 3, Piezas, 1, 0, 'C', 1)
                pdf.cell(120, 3, Descripción, 1, 0, 'C', 1)
                pdf.cell(25, 3, Parroquia, 1, 1, 'C', 1)

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

# CIERRE SEGURO DE CONEXIONES
if db.is_connected():
    db.close()

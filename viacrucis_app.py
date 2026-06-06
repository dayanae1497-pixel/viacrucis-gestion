import streamlit as st
import pandas as pd
import mysql.connector
from fpdf import FPDF 
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA (Fondo oscuro general para simular tus capturas)
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# --- ESTILOS CSS AVANZADOS: CALCADO DE LAS IMÁGENES ---
st.markdown("""
    <style>
    /* Importar la fuente exacta de tu diseño */
    @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;700;800;900&display=swap');
    
    /* Configuración de fuentes globales */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span {
        font-family: 'League Spartan', sans-serif !important;
    }

    /* Fondo de la aplicación basado en el degradado morado/púrpura de tu flyer */
    .stApp {
        background: linear-gradient(180deg, #3d1c73 0%, #200b45 60%, #12032b 100%) !important;
    }
    
    /* BANNER PRINCIPAL: Combinación exacta del fondo oscuro y textos en blanco */
    .banner-patrimonio {
        background-color: #1a053a;
        padding: 20px;
        text-align: center;
        border-bottom: 2px solid #2d1454;
    }
    .titulo-patrimonio {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 42px !important;
        line-height: 1.1;
        margin: 0 !important;
        letter-spacing: -1px;
    }

    /* TÍTULO DE ACCESO AL SISTEMA (Letras amarillas grandes sobre franja pincelada oscura) */
    .acceso-sistema-container {
        background-color: #2b233c;
        padding: 15px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 25px;
        border-radius: 4px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }
    .acceso-sistema-texto {
        color: #e1b12c !important; /* Amarillo exacto de tu flyer */
        font-weight: 900 !important;
        font-size: 48px !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }

    /* FORMULARIO DE LOGIN (Cajas blancas redondeadas con texto oscuro) */
    .stTextInput > label {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #12032b !important;
        font-size: 18px !important;
        border-radius: 30px !important; /* Bordes ovalados como en tu imagen */
        padding: 12px 25px !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }

    /* MENÚ DE PESTAÑAS (Simula la barra gris con iconos de tu captura) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #383541 !important; /* Gris oscuro del menú */
        padding: 8px 15px !important;
        border-bottom: 1px solid #4f4b5c !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e1b12c !important; /* Texto amarillo */
        font-weight: 800 !important;
        font-size: 18px !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #251442 !important;
        border-radius: 4px !important;
        border-bottom: 3px solid #e1b12c !important;
    }

    /* TABLAS DE DATOS (Fondo completamente negro con letras blancas como tu segunda foto) */
    div[data-testid="stDataFrame"] div {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #111111 !important;
        color: #e1b12c !important; /* Encabezados resaltados */
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# LOGO SUPERIOR CENTRAL (Cargado dinámicamente desde el archivo que subiste)
col_logo, col_tit = st.columns([1, 3])
with col_logo:
    # Mostramos el escudo oficial del Viacrucis Viviente
    st.image("image_d535e2.png", width=180)
with col_tit:
    st.markdown("""
        <div class="banner-patrimonio">
            <h1 class="titulo-patrimonio">Sistema de gestión<br>de Patrimonio</h1>
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

# --- PANTALLA DE ACCESO (LOGIN) ---
if not st.session_state['autenticado']:
    st.markdown("""
        <div class="acceso-sistema-container">
            <h2 class="acceso-sistema-texto">Acceso al sistema 🔒🔑</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col_cen, _ = st.columns([2, 1])
    with col_cen:
        with st.form("login"):
            user_input = st.text_input("Usuario 👤")
            pass_input = st.text_input("Contraseña 🔑", type="password")
            
            # Botón estilizado tipo Canva
            if st.form_submit_button("💥 INGRESAR AL SISTEMA"):
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

# --- INTERFAZ POST-LOGIN (MENÚ HORIZONTAL) ---
st.sidebar.markdown(f"👤 **Usuario Activo:**\n### {st.session_state['usuario_nom']}")
if st.sidebar.button("Cerrar Sesión 🚪"):
    st.session_state['autenticado'] = False
    st.rerun()

nombres_tabs = ["Personal 👥", "Economía 💵", "Inventario 📦"]
if st.session_state['usuario_rol'] == 1:
    nombres_tabs.append("Data 📝")

tabs = st.tabs(nombres_tabs)
db = conectar()

# --- TAB 0: PERSONAL (VISTA OSCURA) ---
with tabs[0]:
    st.markdown("<h2 style='color:#e1b12c;'>Personal 👥</h2>", unsafe_allow_html=True)
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

# --- TAB 3: DATA (CON EL AVISO DE CONFIRMACIÓN DE TU SEGUNDA IMAGEN) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        st.markdown("<h2 style='color:#e1b12c;'>Panel de Control de Datos ⚙️</h2>", unsafe_allow_html=True)
        
        tabla_maestra = st.selectbox(
            "Selecciona la tabla a editar:",
            ["Participantes", "Gastos", "Vestuario", "Patrocinantes"]
        )
        
        mapping = {"Participantes": "participantes", "Gastos": "gastos", "Vestuario": "vestuario_final", "Patrocinantes": "patrocinantes"}
        nombre_tabla_db = mapping[tabla_maestra]
        
        try:
            query = f"SELECT * FROM {nombre_tabla_db}"
            df_maestro = pd.read_sql(query, db)
            
            # Editor masivo en vivo
            df_editado = st.data_editor(df_maestro, num_rows="dynamic", use_container_width=True, hide_index=True)

            # --- IMPLEMENTACIÓN DE TU VENTANA DE AVISO DE SEGURIDAD REQUERIDA ---
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.status("⚠️ AVISO DE SEGURIDAD DETECTADO", expanded=True):
                st.markdown(f"""
                <div style='text-align:center; padding:10px;'>
                    <h2 style='color:#000000; margin:0;'>¿Confirmar cambios?</h2>
                    <p style='color:#333333; font-size:16px;'>Has editado datos sensibles en la tabla <b>'{tabla_maestra}'</b>.<br>¿Deseas aplicar los cambios de manera irreversible en la base de datos o revertir la acción?</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones de acción del cuadro de diálogo
                c_si, c_no = st.columns(2)
                
                with c_si:
                    proceder = st.button("SÍ, CONFIRMAR CAMBIOS ✔️", use_container_width=True, type="primary")
                with c_no:
                    revertir = st.button("NO, REVERTIR ❌", use_container_width=True)

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
                    st.error(f"Error crítico al guardar: {err}")
                finally:
                    cur.close()
                    
            if revertir:
                st.info("Acción cancelada. Recargando la tabla original...")
                st.rerun()

        except Exception as e:
            st.error(f"Error al procesar el panel: {e}")

# Cierre automático de conexiones a la base de datos
if db.is_connected():
    db.close()

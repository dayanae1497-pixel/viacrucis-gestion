import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS VISUALES (CSS)
# ==============================================================================
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;700;800;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, label {
        font-family: 'League Spartan', sans-serif !important;
    }

    /* Fondo degradado envolvente (Calco de tus maquetas) */
    .stApp {
        background: linear-gradient(180deg, #321354 0%, #1c0933 50%, #0d021a 100%) !important;
    }

    /* ENCABEZADO PRINCIPAL REPLICADO DE TUS MAQUETAS */
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

    /* SECCIÓN DE ACCESO: Franja pincelada */
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
    }

    /* DISEÑO DE ENTRADAS DEL LOGIN (Bordes redondeados como tus imágenes) */
    .stTextInput > div > div > input {
        background-color: #79579e !important;
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 35px !important;
        padding: 14px 25px !important;
        border: 2px solid #b58c24 !important;
    }
    .stTextInput label {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    
    /* PESTAÑAS (TABS NAV) */
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

    /* TEXTO VISIBLE EN TABLAS: Forzar color blanco sobre el fondo oscuro */
    div[data-testid="stDataFrame"] div, div[data-testid="stDataEditor"] div {
        color: #ffffff !important;
    }
    
    /* CAJA INTERNA DEL DIÁLOGO / POP-UP DE SEGURIDAD */
    .aviso-seguridad-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO DEL SISTEMA FIJO EN LA PARTE SUPERIOR
st.markdown("""
    <div class="header-sistema">
        <h1 class="header-titulo">Sistema de gestión<br>de Patrimonio</h1>
    </div>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. LÓGICA DE CONEXIÓN A LA BASE DE DATOS (INTACTA)
# ==============================================================================
def conectar():
    password_db = st.secrets.get("password", "AVNS_ytphqSAjobNIHWjlbex")
    return mysql.connector.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com", 
        user="avnadmin", 
        password=password_db, 
        port=18358, 
        database="viacrucis_2026"
    )


# ==============================================================================
# 3. CONTROL DE SESIÓN Y LOGIN
# ==============================================================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

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


# ==============================================================================
# 4. INTERFAZ OPERATIVA DEL SISTEMA (MENÚS Y PESTAÑAS)
# ==============================================================================
# CORRECCIÓN DE SINTAXIS AQUÍ: Se cerró correctamente la llave del f-string
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
    except Exception as e:
        st.error(f"Error: {e}")


# --- TAB 2: INVENTARIO ---
with tabs[2]:
    cv, cu = st.columns(2)
    with cv:
        st.subheader("👕 Vestuario")
        query_v = "SELECT v.piezas, v.descripcion, pa.`Nombre Parroquia` FROM vestuario_final v JOIN parroquia pa ON v.id_parroquia = pa.id_parroquia"
        st.dataframe(pd.read_sql(query_v, db), hide_index=True)
    with cu:
        st.subheader("🛠️ Utilería")
        st.dataframe(pd.read_sql("SELECT objeto, cantidad, descripcion FROM utileria", db), hide_index=True)


# --- TAB 3: DATA (PANEL DE CONTROL EXCLUSIVO CON BLOQUEO MÁXIMO Y RESPALDO) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        st.markdown("<h2 style='color:#e5b82b;'>Panel de Control de Datos ⚙️</h2>", unsafe_allow_html=True)
        
        tabla_maestra = st.selectbox(
            "Selecciona la tabla a editar:",
            ["Participantes", "Gastos", "Vestuario", "Patrocinantes"],
            key="selector_tabla_critica"
        )
        
        mapping = {
            "Participantes": "participantes", 
            "Gastos": "gastos", 
            "Vestuario": "vestuario_final", 
            "Patrocinantes": "patrocinantes"
        }
        nombre_tabla_db = mapping[tabla_maestra]
        
        # LOGICA DE RESPALDO: Sincronización inmutable del buffer original
        if "tabla_actual" not in st.session_state or st.session_state.get("nombre_tabla_anterior") != nombre_tabla_db:
            df_original = pd.read_sql(f"SELECT * FROM {nombre_tabla_db}", db)
            st.session_state.tabla_actual = df_original.copy()
            st.session_state.backup_data = df_original.copy() 
            st.session_state.nombre_tabla_anterior = nombre_tabla_db

        # FUNCIÓN DE LA VENTANA EMERGENTE (MODAL DIALOG - BLOQUEA TODO EL FONDO)
        @st.dialog("⚠️ CONTROL DE SEGURIDAD")
        def mostrar_popup_seguridad(datos_nuevos, tabla_nombre_legible, tabla_db_real):
            
            # Carga limpia y centrada del logo oficial desde GitHub assets/
            col_logo_izq, col_logo_cen, col_logo_der = st.columns([1, 2, 1])
            with col_logo_cen:
                try:
                    st.image("assets/image.png", use_container_width=True)
                except Exception:
                    st.caption("ℹ️ Logo del Sistema de Gestión")

            st.markdown(f"""
            <div class="aviso-seguridad-box" style="border-top: 10px solid #e5b82b; text-align: center;">
                <h2 style="color: #000000; font-size: 26px; font-weight: 900; margin-top: 5px;">¿Confirmar cambios?</h2>
                <p style="color: #2f3542; font-size: 15px; font-weight: bold; margin-bottom: 20px;">
                    Has realizado modificaciones o eliminaciones en la tabla '<strong>{tabla_nombre_legible}</strong>'.<br>
                    ¿Deseas aplicar estos cambios en la Base de Datos o restaurar la información?
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("🟢 SÍ, CONFIRMAR CAMBIOS", use_container_width=True):
                    db_popup = conectar()
                    cur = db_popup.cursor()
                    try:
                        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
                        cur.execute(f"DELETE FROM {tabla_db_real}") 
                        
                        cols = ", ".join([f"`{c}`" for c in datos_nuevos.columns])
                        placeholders = ", ".join(["%s"] * len(datos_nuevos.columns))
                        sql_insert = f"INSERT INTO {tabla_db_real} ({cols}) VALUES ({placeholders})"
                        
                        for _, row in datos_nuevos.iterrows():
                            valores = tuple(None if pd.isna(v) else v for v in row)
                            cur.execute(sql_insert, valores)
                        
                        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                        db_popup.commit()
                        
                        # Guardamos con éxito el nuevo estado de datos en el buffer de respaldo
                        st.session_state.tabla_actual = datos_nuevos.copy()
                        st.session_state.backup_data = datos_nuevos.copy()
                        st.toast("🎉 ¡Base de datos sincronizada con éxito!", icon="✅")
                        st.rerun()
                    except Exception as err:
                        db_popup.rollback()
                        st.error(f"Error crítico al guardar: {err}")
                    finally:
                        cur.close()
                        db_popup.close()
                        
            with col_no:
                if st.button("🔴 NO, REVERTIR ANOMALÍAS", use_container_width=True):
                    # DESCARTE SEGURO: Borramos los datos alterados y restauramos el backup estático
                    st.session_state.tabla_actual = st.session_state.backup_data.copy()
                    st.toast("🔄 Cambios revocados de manera segura.", icon="↩️")
                    st.rerun()

        try:
            # Editor masivo interactivo
            df_editado = st.data_editor(
                st.session_state.tabla_actual, 
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True, 
                key="editor_maestro_final"
            )

            # Monitoreo inteligente de cambios en el editor
            cambios = st.session_state.editor_maestro_final
            hubo_cambios = len(cambios.get("edited_rows", {})) > 0 or \
                           len(cambios.get("added_rows", {})) > 0 or \
                           len(cambios.get("deleted_rows", {})) > 0

            # Si el usuario edita, añade o borra filas, salta el pop-up bloqueando el sistema
            if hubo_cambios:
                mostrar_popup_seguridad(df_editado, tabla_maestra, nombre_tabla_db)

        except Exception as e:
            st.error(f"Error al procesar el panel: {e}")

# CIERRE AUTOMÁTICO DE CONEXIONES SEGURO
if db.is_connected():
    db.close()

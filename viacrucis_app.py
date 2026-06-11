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

    /* =========================================================
       🔥 SOLUCIÓN OCULTAR BOTÓN "+" MANTENIENDO EL BORRADO 
       ========================================================= */
    /* Oculta la última fila fantasma de agregación */
    [data-testid="stDataEditor"] div[role="row"]:last-child button[title="Add row"],
    [data-testid="stDataEditor"] button[title="Add row"] {
        display: none !important;
    }
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
    except Exception as e:
        st.error(f"Error: {e}")

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

# --- TAB 3: DATA (PANEL CRÍTICO REESTRUCTURADO) ---
if st.session_state.get('usuario_rol') == 1:
    with tabs[3]:
        
        # ==========================================
        # SECTION 1: REGISTRO DE DATOS NUEVOS
        # ==========================================
        st.header("📝 Registro de Datos")
        
        opc = st.radio("¿Qué deseas registrar?", 
                       ["Gasto Nuevo", "Abono de Patrocinante", "Nuevo Patrocinante", "Nuevo Participante", "Nuevo Personaje"], 
                       horizontal=True,
                       key="radio_registro_datos")
        
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
                    st.success("✅ Gasto guardado con éxito.")
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
                        valores = (int(p_id), float(abo), fecha_pago)
                        cur.execute(sql, valores)
                        db.commit()
                        cur.close()
                        st.success(f"✅ Abono de ${abo} registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

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
                        st.success(f"✅ ¡{nombre_negocio} agregado!")
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
                        cur.execute(sql, (nom, ape, eda, telf_p, com_id, par_id, rol_id))
                        db.commit()
                        cur.close()
                        st.success(f"✅ {nom} {ape} ha sido registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error en base de datos: {e}")
        
        elif opc == "Nuevo Personaje":
            try:
                df_participantes = pd.read_sql("SELECT id_participante, Nombre, Apellido FROM participantes", db)
                df_participantes['Nombre Completo'] = df_participantes['Nombre'] + " " + df_participantes['Apellido']

                st.subheader("🎭 Asignar Papel del Elenco")
                with st.form("form_personaje"):
                    p_id = st.selectbox("Seleccionar Participante", options=df_participantes['id_participante'], 
                                       format_func=lambda x: df_participantes[df_participantes['id_participante']==x]['Nombre Completo'].iloc[0])
                  
                    nombre_papel = st.text_input("Nombre del Personaje")

                    if st.form_submit_button("Guardar Personaje"):
                        cur = db.cursor()
                        sql = "INSERT INTO personajes (Descripción, id_participante) VALUES (%s, %s)"
                        cur.execute(sql, (nombre_papel, int(p_id)))
                        db.commit()
                        cur.close()
                        st.success(f"✅ ¡{nombre_papel} asignado correctamente!")
                        st.rerun()
            except Exception as e:
                st.error(f"⚠️ Hubo un detalle: {e}")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ==========================================
        # SECTION 2: PANEL DE EDICIÓN Y ELIMINACIÓN
        # ==========================================
        st.markdown("<h2 style='color:#e5b82b;'>Panel de Control de Datos ⚙️</h2>", unsafe_allow_html=True)
        
        tabla_maestra = st.selectbox(
            "Selecciona la tabla a editar:",
            ["Participantes", "Gastos", "Vestuario", "Patrocinantes"],
            key="selector_tabla_critica"
        )
        
        mapping = {"Participantes": "participantes", "Gastos": "gastos", "Vestuario": "vestuario_final", "Patrocinantes": "patrocinantes"}
        nombre_tabla_db = mapping[tabla_maestra]
        
        # Inicialización de variables de estado
        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0
 
        if "tabla_actual" not in st.session_state or st.session_state.get("nombre_tabla_anterior") != nombre_tabla_db:
            df_original = pd.read_sql(f"SELECT * FROM {nombre_tabla_db}", db)
            st.session_state.tabla_actual = df_original.copy()
            st.session_state.backup_data = df_original.copy()
            st.session_state.nombre_tabla_anterior = nombre_tabla_db
            st.session_state.bloqueo_advertencia = False
 
        # Mensajes de estado
        if st.session_state.get("guardado_exitoso"):
            st.success("🎉 ¡Información sincronizada en la Base de Datos!")
            del st.session_state["guardado_exitoso"]
        
        if st.session_state.get("cambios_revertidos"):
            st.warning("🔄 Cambios revocados. Se restauró la información original de manera segura.")
            del st.session_state["cambios_revertidos"]
 
        # --- ESCENARIO A: MODO VISUALIZACIÓN / EDICIÓN ---
        if not st.session_state.get("bloqueo_advertencia", False):
            version_actual = st.session_state.editor_version
            key_dinamica = f"editor_{nombre_tabla_db}_{version_actual}"
            
            # Mantenemos num_rows="dynamic" para permitir la eliminación (CRUD completo)
            df_editado = st.data_editor(
                st.session_state.tabla_actual, 
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True, 
                key=key_dinamica
            )
 
            # Inspección de cambios en el diccionario de Streamlit
            cambios = st.session_state.get(key_dinamica, {})
            hubo_eliminacion = len(cambios.get("deleted_rows", [])) > 0
            hubo_modificacion = len(cambios.get("edited_rows", {})) > 0
 
            # Si el usuario editó o eliminó registros legítimos, congelamos pantalla y pedimos confirmación
            if hubo_eliminacion or hubo_modificacion:
                st.session_state.df_congelado_cambios = df_editado.copy()
                st.session_state.bloqueo_advertencia = True
                st.rerun()
 
        # --- ESCENARIO B: PANTALLA DE ADVERTENCIA PARA CONFIRMAR CAMBIOS ---
        else:
            st.markdown(f"""
                <div style="background-color: #ffeaa7; padding: 20px; border-radius: 10px; border-left: 8px solid #e17055; margin-bottom: 20px;">
                    <p style="color: #d63031; font-weight: bold; font-size: 14px; text-align: center; margin: 0; letter-spacing: 2px;">⚠️ AVISO DE SEGURIDAD CRÍTICO ⚠️</p>
                    <h2 style="color: #000000; font-size: 28px; font-weight: 800; text-align: center; margin-top: 5px; margin-bottom: 10px;">¿Confirmar alteración de datos?</h2>
                    <p style="color: #2f3542; font-size: 16px; text-align: center; font-weight: bold; margin-bottom: 10px;">
                        Has editado o eliminado registros existentes en la tabla '{tabla_maestra}'.<br>El sistema mantendrá bloqueada la pantalla hasta que decidas:
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            col_si, col_no = st.columns(2)
            datos_nuevos = st.session_state.get("df_congelado_cambios")
            
            with col_si:
                if st.button("🟢 SÍ, CONFIRMAR Y APLICAR CAMBIOS", use_container_width=True):
                    if datos_nuevos is not None:
                        cur = db.cursor()
                        try:
                            # 1. Desactivar restricciones temporalmente
                            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
                            
                            # 2. Identificar la columna ID 
                            columna_id = datos_nuevos.columns[0]
                            
                            # 3. Limpiar celdas vacías
                            col_critica = 'Nombre' if 'Nombre' in datos_nuevos.columns else datos_nuevos.columns[0]
                            datos_filtrados = datos_nuevos.dropna(subset=[col_critica])
                            datos_filtrados = datos_filtrados[datos_filtrados[col_critica].astype(str).str.strip() != ""]
                            
                            # 4. OBTENER IDs ACTUALES DE LA BASE DE DATOS
                            cur.execute(f"SELECT `{columna_id}` FROM {nombre_tabla_db}")
                            ids_en_db = [row[0] for row in cur.fetchall()]
                            
                            # IDs que quedaron en el editor visual
                            ids_en_editor = datos_filtrados[columna_id].dropna().tolist()
                            
                            # 5. ELIMINACIÓN QUIRÚRGICA: Si el ID estaba en la DB pero ya no está en el editor, SE BORRA
                            for id_db in ids_en_db:
                                if id_db not in ids_en_editor:
                                    cur.execute(f"DELETE FROM {nombre_tabla_db} WHERE `{columna_id}` = %s", (id_db,))
                            
                            # 6. GUARDAR O ACTUALIZAR LAS FILAS QUE SÍ QUEDARON
                            cols = ", ".join([f"`{c}`" for c in datos_filtrados.columns])
                            placeholders = ", ".join(["%s"] * len(datos_filtrados.columns))
                            
                            updates = ", ".join([f"`{c}` = VALUES(`{c}`)" for c in datos_filtrados.columns if c != columna_id])
                            sql_save = f"INSERT INTO {nombre_tabla_db} ({cols}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
                            
                            for _, row in datos_filtrados.iterrows():
                                valores = tuple(None if pd.isna(v) else v for v in row)
                                cur.execute(sql_save, valores)
                            
                            # 7. Reactivar restricciones de seguridad
                            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            db.commit()
                            
                            # Sincronizar estados de Streamlit
                            st.session_state.tabla_actual = datos_filtrados.copy()
                            st.session_state.backup_data = datos_filtrados.copy()
                            
                            if 'editor_version' not in st.session_state:
                                st.session_state.editor_version = 0
                            st.session_state.editor_version += 1
                            
                            st.session_state.guardado_exitoso = True
                            st.session_state.bloqueo_advertencia = False
                            
                        except Exception as err:
                            db.rollback()
                            try:
                                cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            except:
                                pass
                            st.error(f"❌ Error crítico al procesar la actualización: {err}")
                        finally:
                            cur.close()
                    
                    st.rerun()
                    
            with col_no:
                if st.button("🔴 NO, REVERTIR ANOMALÍAS", use_container_width=True):
                    st.session_state.tabla_actual = st.session_state.backup_data.copy()
                    st.session_state.editor_version += 1
                    st.session_state.cambios_revertidos = True
                    st.session_state.bloqueo_advertencia = False
                    st.rerun()

# ==========================================
# SECTION 3: CIERRE DE CONEXIÓN GLOBAL
# ==========================================
if 'db' in locals() and db.is_connected():
    db.close()

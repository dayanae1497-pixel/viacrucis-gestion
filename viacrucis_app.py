import streamlit as st
import pandas as pd
import mysql.connector

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# --- BANNER FIJO (Aparece en todas las páginas) ---
st.markdown("""
    <div style="background-color:#461212;padding:20px;border-radius:15px;text-align:center;border: 2px solid #fcf75e;">
        <h1 style="color:white;margin:0;font-family:serif;">⛪ Viacrucis en Vivo 2026</h1>
        <p style="color:#fcf75e;margin:5px;font-weight:bold;font-size:1.2em;">"Pasión y Fe en cada paso"</p>
    </div>
    <br>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE CONEXIÓN ---
def conectar():
    password_db = st.secrets.get("password", "AVNS_ytphqSAjobNIHWjlbex")
    return mysql.connector.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com", 
        user="avnadmin", 
        password=password_db, 
        port=18358, 
        database="viacrucis_2026"
    )

# --- LÓGICA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Sistema Viacrucis 2026")
    with st.form("login"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            try:
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
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    st.stop()

# --- BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2618/2618245.png", width=100)
st.sidebar.title(f"Hola, {st.session_state['usuario_nom']}")
menu = st.sidebar.radio("Navegación", ["🏠 Inicio", "👥 Personal", "💰 Economía", "📦 Inventario y Vestuario", "✍️ Cargar Data"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

db = conectar()

# ---------------------------------------------------------
# 1. PÁGINA DE INICIO
# ---------------------------------------------------------
if menu == "🏠 Inicio":
    st.subheader("¡De pinga tenerte de vuelta!")
    st.write("Bienvenido al panel central de control. Desde aquí puedes supervisar todo el despliegue para el Viacrucis 2026.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("👥 **Personal:** Revisa quiénes participan y sus roles.")
    with col2:
        st.success("💰 **Economía:** Controla los cobres del evento.")
    with col3:
        st.warning("📦 **Logística:** Gestiona ropa y utilería.")

# ---------------------------------------------------------
# 2. SECCIÓN DE PERSONAL (CON EDITAR/ELIMINAR)
# ---------------------------------------------------------
elif menu == "👥 Personal":
    st.header("👥 Gestión de Personal")
    query_p = """
    SELECT p.id_participante, p.Nombre, p.Apellido, p.Edad, per.Descripción AS Personaje, 
           r.Descripción AS Rol, pa.`Nombre Parroquia` AS Parroquia, 
           c.Descripción AS Comisión, p.teléfono AS Teléfono
    FROM participantes p
    JOIN parroquia pa ON p.id_parroquia = pa.id_parroquia
    JOIN comisiones c ON p.id_comision = c.id_comsion
    JOIN roles r ON p.id_rol = r.id_rol
    LEFT JOIN personajes per ON p.id_participante = per.id_participante
    """
    df_p = pd.read_sql(query_p, db)
    st.dataframe(df_p, use_container_width=True, hide_index=True)

    if st.session_state['usuario_rol'] == 1:
        with st.expander("⚙️ Modificar o Eliminar Participante"):
            id_sel = st.selectbox("Selecciona ID del Participante", options=df_p['id_participante'])
            col1, col2 = st.columns(2)
            with col1:
                nuevo_t = st.text_input("Actualizar Teléfono")
                if st.button("Guardar Cambios"):
                    cur = db.cursor()
                    cur.execute("UPDATE participantes SET teléfono=%s WHERE id_participante=%s", (nuevo_t, id_sel))
                    db.commit()
                    st.success("¡Cambiado!")
                    st.rerun()
            with col2:
                if st.button("❌ Eliminar Permanentemente"):
                    cur = db.cursor()
                    cur.execute("DELETE FROM personajes WHERE id_participante=%s", (id_sel,))
                    cur.execute("DELETE FROM participantes WHERE id_participante=%s", (id_sel,))
                    db.commit()
                    st.error("Participante borrado.")
                    st.rerun()

# ---------------------------------------------------------
# 3. SECCIÓN ECONOMÍA (CON EDITAR/ELIMINAR)
# ---------------------------------------------------------
elif menu == "💰 Economía":
    st.header("💰 Gestión Financiera")
    
    t1, t2 = st.tabs(["📊 Resumen de Gastos", "💎 Patrocinantes"])
    
    with t1:
        df_g = pd.read_sql("SELECT id_gasto, concepto, monto, `fecha del gasto` FROM gastos", db)
        st.dataframe(df_g, use_container_width=True, hide_index=True)
        if st.session_state['usuario_rol'] == 1:
            with st.expander("🗑️ Borrar Gasto"):
                id_g = st.selectbox("ID del Gasto a eliminar", options=df_g['id_gasto'])
                if st.button("Confirmar Borrado de Gasto"):
                    cur = db.cursor()
                    cur.execute("DELETE FROM gastos WHERE id_gasto=%s", (id_g,))
                    db.commit()
                    st.rerun()

    with t2:
        df_a = pd.read_sql("""SELECT pg.id_pago, p.negocio, pg.abono, pg.`fecha de abono` 
                              FROM pago_patrocinantes pg 
                              JOIN patrocinantes p ON pg.id_patrocinante = p.id_patrocinante""", db)
        st.dataframe(df_a, use_container_width=True, hide_index=True)
        if st.session_state['usuario_rol'] == 1:
            with st.expander("🗑️ Anular Abono"):
                id_ab = st.selectbox("ID del Abono a anular", options=df_a['id_pago'])
                if st.button("Confirmar Anulación"):
                    cur = db.cursor()
                    cur.execute("DELETE FROM pago_patrocinantes WHERE id_pago=%s", (id_ab,))
                    db.commit()
                    st.rerun()

# ---------------------------------------------------------
# 4. INVENTARIO Y VESTUARIO (CON EDITAR/ELIMINAR)
# ---------------------------------------------------------
elif menu == "📦 Inventario y Vestuario":
    st.header("📦 Control de Logística")
    col_v, col_u = st.columns(2)
    
    with col_v:
        st.subheader("👕 Vestuario")
        df_v = pd.read_sql("SELECT id_vestuario, piezas, descripcion FROM vestuario_final", db)
        st.dataframe(df_v, use_container_width=True, hide_index=True)
        if st.session_state['usuario_rol'] == 1:
            id_v_del = st.selectbox("Borrar Vestuario (ID)", options=df_v['id_vestuario'])
            if st.button("Eliminar Prenda"):
                cur = db.cursor()
                cur.execute("DELETE FROM vestuario_final WHERE id_vestuario=%s", (id_v_del,))
                db.commit()
                st.rerun()

    with col_u:
        st.subheader("🛠️ Utilería")
        df_u = pd.read_sql("SELECT id_utileria, objeto, cantidad, descripcion FROM utileria", db)
        st.dataframe(df_u, use_container_width=True, hide_index=True)
        if st.session_state['usuario_rol'] == 1:
            id_u_del = st.selectbox("Borrar Objeto (ID)", options=df_u['id_utileria'])
            if st.button("Eliminar Objeto"):
                cur = db.cursor()
                cur.execute("DELETE FROM utileria WHERE id_utileria=%s", (id_u_del,))
                db.commit()
                st.rerun()

# ---------------------------------------------------------
# 5. CARGAR DATA (CREAR REGISTROS)
# ---------------------------------------------------------
elif menu == "✍️ Cargar Data":
    if st.session_state['usuario_rol'] != 1:
        st.error("No tienes rango para esto, mano.")
    else:
        st.header("📝 Registro de Nueva Información")
        opc = st.radio("¿Qué vas a registrar?", ["Nuevo Participante", "Nuevo Gasto", "Nuevo Vestuario"], horizontal=True)
        
        if opc == "Nuevo Gasto":
            with st.form("fg"):
                con = st.text_input("Concepto")
                mon = st.number_input("Monto", min_value=0.0)
                fec = st.date_input("Fecha")
                if st.form_submit_button("Guardar"):
                    cur = db.cursor()
                    cur.execute("INSERT INTO gastos (concepto, monto, `fecha del gasto`) VALUES (%s, %s, %s)", (con, mon, fec))
                    db.commit()
                    st.success("Gasto anotado.")
        
        # ... (Aquí puedes añadir los otros formularios de registro que ya tenías)

# CERRAR CONEXIÓN AL FINAL
if db.is_connected():
    db.close()

























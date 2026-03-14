import streamlit as st
import pandas as pd
import mysql.connector

# Configuración inicial
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

# --- BANNER FIJO ---
st.markdown("""
    <div style="background-color:#461212;padding:15px;border-radius:10px;text-align:center;">
        <h1 style="color:white;margin:0;">⛪ Viacrucis en Vivo 2026</h1>
        <p style="color:white;opacity:0.8;">Sistema de Gestión de Patrimonio y Elenco</p>
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

# --- MANEJO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso al Sistema")
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

# --- NAVEGACIÓN ---
st.sidebar.title(f"Bienvenido, {st.session_state['usuario_nom']}")
menu = st.sidebar.radio("Ir a:", ["🏠 Inicio", "👥 Personal", "💰 Economía", "📦 Inventario y Vestuario", "✍️ Gestión de Datos"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

db = conectar()

# --- 🏠 PÁGINA DE INICIO ---
if menu == "🏠 Inicio":
    st.subheader("¡Saludos, mano!")
    st.write(f"Estás en el panel central del **Viacrucis 2026**. Aquí puedes gestionar todo lo referente al elenco, los gastos y el inventario de la pasión de Cristo.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Dato:** Recuerda siempre cerrar sesión si compartes la PC.")
    with col2:
        st.success("✅ El sistema está conectado a la base de datos en la nube.")

# --- 👥 PERSONAL ---
elif menu == "👥 Personal":
    st.header("Lista de Participantes")
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
    st.dataframe(df_p.drop(columns=['id_participante']), use_container_width=True)

# --- 📦 INVENTARIO Y VESTUARIO (Con Editar/Eliminar) ---
elif menu == "📦 Inventario y Vestuario":
    tab_v, tab_u = st.tabs(["👕 Vestuario", "🛠️ Utilería"])
    
    with tab_v:
        st.subheader("Control de Vestuario")
        query_v = "SELECT id_vestuario, piezas, descripcion FROM vestuario_final"
        df_v = pd.read_sql(query_v, db)
        
        # Mostrar tabla
        st.dataframe(df_v, use_container_width=True, hide_index=True)
        
        # Editar / Eliminar
        if st.session_state['usuario_rol'] == 1:
            with st.expander("⚙️ Modificar Vestuario"):
                id_edit = st.selectbox("Selecciona ID para editar/eliminar", options=df_v['id_vestuario'])
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nueva_p = st.text_input("Nuevas Piezas")
                    if st.button("Actualizar Vestuario"):
                        cur = db.cursor()
                        cur.execute("UPDATE vestuario_final SET piezas=%s WHERE id_vestuario=%s", (nueva_p, id_edit))
                        db.commit()
                        st.success("¡Actualizado!")
                        st.rerun()
                with col_e2:
                    if st.button("❌ Eliminar Vestuario"):
                        cur = db.cursor()
                        cur.execute("DELETE FROM vestuario_final WHERE id_vestuario=%s", (id_edit,))
                        db.commit()
                        st.warning("Registro eliminado.")
                        st.rerun()

    with tab_u:
        st.subheader("Inventario de Utilería")
        df_u = pd.read_sql("SELECT id_utileria, objeto, cantidad, descripcion FROM utileria", db)
        st.dataframe(df_u, use_container_width=True, hide_index=True)
        
        if st.session_state['usuario_rol'] == 1:
            with st.expander("⚙️ Modificar Utilería"):
                id_u = st.selectbox("Selecciona ID de objeto", options=df_u['id_utileria'])
                if st.button("❌ Eliminar Objeto"):
                    cur = db.cursor()
                    cur.execute("DELETE FROM utileria WHERE id_utileria=%s", (id_u,))
                    db.commit()
                    st.rerun()

# --- ✍️ CARGAR DATA (CRUD Nuevo) ---
elif menu == "✍️ Gestión de Datos":
    if st.session_state['usuario_rol'] != 1:
        st.warning("No tienes permiso para estar aquí.")
    else:
        opc = st.selectbox("Selecciona acción:", ["Añadir Gasto", "Añadir Vestuario", "Añadir Utilería", "Nuevo Participante"])
        
        if opc == "Añadir Vestuario":
            with st.form("add_v"):
                piezas = st.text_input("Piezas (ej. Túnica, Manto)")
                desc = st.text_area("Descripción")
                id_parr = st.number_input("ID Parroquia", min_value=1, step=1)
                if st.form_submit_button("Guardar en Vestuario"):
                    cur = db.cursor()
                    cur.execute("INSERT INTO vestuario_final (piezas, descripcion, id_parroquia) VALUES (%s,%s,%s)", (piezas, desc, id_parr))
                    db.commit()
                    st.success("¡Listo!")

        elif opc == "Añadir Utilería":
            with st.form("add_u"):
                obj = st.text_input("Objeto")
                cant = st.number_input("Cantidad", min_value=1)
                desc_u = st.text_input("Estado/Descripción")
                if st.form_submit_button("Guardar en Inventario"):
                    cur = db.cursor()
                    cur.execute("INSERT INTO utileria (objeto, cantidad, descripcion) VALUES (%s,%s,%s)", (obj, cant, desc_u))
                    db.commit()
                    st.success("Objeto agregado.")

# --- SECCIÓN ECONOMÍA (Simplificada para el ejemplo) ---
elif menu == "💰 Economía":
    st.header("Estado Financiero")
    # ... (Aquí va tu código de economía que ya tenías)
    st.info("Sección de reportes de patrocinio y gastos.")

if db.is_connected():
    db.close()








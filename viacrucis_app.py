import streamlit as st
import pandas as pd
import mysql.connector

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

def conectar():
    # Intenta sacar la clave de los Secrets de Streamlit
    # Si no existe (en local), usa una cadena vacía o tu clave de prueba
    password_db = st.secrets.get("password", "AVNS_ytphqSAjobNIHWjlbex")
    
    return mysql.connector.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com", 
        user="avnadmin", 
        password=password_db, 
        port=18358, 
        database="viacrucis_2026"
    )

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Sistema Viacrucis 2026")
    with st.form("login"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            db = conectar()
            cursor = db.cursor()
            # Traemos el nombre y el id_rol para saber qué permisos tiene
            query = "SELECT nombre_usuario, id_rol FROM usuarios WHERE nombre_usuario=%s AND clave=%s"
            cursor.execute(query, (user_input, pass_input))
            resultado = cursor.fetchone()
            db.close()
            
            if resultado:
                st.session_state['autenticado'] = True
                st.session_state['usuario_nom'] = resultado[0]
                st.session_state['usuario_rol'] = resultado[1] # Guardamos el nivel de permiso
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.sidebar.markdown(f"👤 **Usuario:** {st.session_state['usuario_nom']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

# Definimos las pestañas dinámicamente según el rol
# Si id_rol es 1, mostramos la pestaña de carga. Si no, solo las de consulta.
nombres_tabs = ["👥 Personal", "💰 Economía", "📦 Inventario"]
if st.session_state['usuario_rol'] == 1:
    nombres_tabs.append("✍️ Cargar Data")

tabs = st.tabs(nombres_tabs)

db = conectar()

# --- PESTAÑA: PERSONAL ---
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

    # Filtros en el Sidebar
    st.sidebar.header("🔍 Filtros de Lista")
    f_parroquia = st.sidebar.multiselect("Filtrar por Parroquia", options=df_p["Parroquia"].unique())
    f_rol = st.sidebar.multiselect("Filtrar por Rol/Personaje", options=df_p["Rol"].unique())
    f_comision = st.sidebar.multiselect("Filtrar por Comisión", options=df_p["Comisión"].unique())

    # Aplicar filtros
    df_f = df_p.copy()
    if f_parroquia: df_f = df_f[df_f["Parroquia"].isin(f_parroquia)]
    if f_rol: df_f = df_f[df_f["Rol"].isin(f_rol)]
    if f_comision: df_f = df_f[df_f["Comisión"].isin(f_comision)]

    # Métrica de cantidad de personas
    st.metric("Total Personas en esta lista", len(df_f))
    
    st.dataframe(df_f, use_container_width=True, hide_index=True)

# --- PESTAÑA: ECONOMÍA ---
with tabs[1]:
    res_in = pd.read_sql("SELECT SUM(abono) as total FROM pago_patrocinantes", db)
    total_in = res_in['total'].iloc[0] or 0
    res_out = pd.read_sql("SELECT SUM(monto) as total FROM gastos", db)
    total_out = res_out['total'].iloc[0] or 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"{total_in} $")
    c2.metric("Gastos", f"{total_out} $")
    c3.metric("Saldo", f"{total_in - total_out} $")
    
    st.divider()
    col_pat, col_gas = st.columns(2)
    with col_pat:
        st.subheader("Patrocinantes")
        q_pat = """
        SELECT p.negocio, p.`monto a pagar` AS Pactado, 
                IFNULL(SUM(pg.abono), 0) AS Abonado,
                (p.`monto a pagar` - IFNULL(SUM(pg.abono), 0)) AS Pendiente
        FROM patrocinantes p
        LEFT JOIN pago_patrocinantes pg ON p.id_patrocinante = pg.id_patrocinante
        GROUP BY p.id_patrocinante
        """
        st.dataframe(pd.read_sql(q_pat, db), hide_index=True)
    with col_gas:
        st.subheader("Gastos")
        # id_gastos, concepto, monto, fecha del gasto
        st.dataframe(pd.read_sql("SELECT concepto, monto, `fecha del gasto` FROM gastos", db), hide_index=True)

# --- PESTAÑA: INVENTARIO ---
with tabs[2]:
    cv, cu = st.columns(2)
    with cv:
        st.subheader("👕 Vestuario")
        # piezas, descripcion, Nombre Parroquia
        query_v = """
        SELECT v.piezas, v.descripcion, pa.`Nombre Parroquia` 
        FROM vestuario_final v 
        JOIN parroquia pa ON v.id_parroquia = pa.id_parroquia
        """
        st.dataframe(pd.read_sql(query_v, db), hide_index=True)
    with cu:
        st.subheader("🛠️ Utilería")
        # objeto, cantidad, descripcion
        st.dataframe(pd.read_sql("SELECT objeto, cantidad, descripcion FROM utileria", db), hide_index=True)

# --- PESTAÑA: CARGAR DATA (Solo visible para id_rol == 1) ---
if st.session_state['usuario_rol'] == 1:
    with tabs[3]:
        st.header("📝 Registro de Datos")
        # Agregamos las opciones solicitadas al radio button
        opc = st.radio("¿Qué deseas registrar?", 
                        ["Gasto Nuevo", "Abono de Patrocinante", "Nuevo Patrocinante", "Nuevo Participante", "Nuevo Personaje"], 
                        horizontal=True)
        
        if opc == "Gasto Nuevo":
            with st.form("nuevo_gasto"):
                con = st.text_input("Concepto")
                mon = st.number_input("Monto ($)", min_value=0.0)
                fec = st.date_input("Fecha")
                if st.form_submit_button("Guardar Gasto"):
                    cur = db.cursor()
                    cur.execute("INSERT INTO gastos (concepto, monto, `fecha del gasto`) VALUES (%s, %s, %s)", (con, mon, fec))
                    db.commit()
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
                      # Usamos comillas invertidas `` porque tu columna tiene espacios
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
                        st.success(f"✅ ¡{nombre_negocio} agregado!")
                        st.rerun()
                    else:
                        st.error("Mano, ponle el nombre al negocio por lo menos.")

        # --- SECCIÓN DE REGISTROS ---
    # --- SECCIÓN: NUEVO PARTICIPANTE ---
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

        # --- SECCIÓN: ASIGNAR PERSONAJE ---
    elif opc == "Asignar Personaje":
        try:
            # Traemos participantes (id_participante, Nombre, Apellido según image_31377c)
            df_participantes = pd.read_sql("SELECT id_participante, Nombre, Apellido FROM participantes", db)
            df_participantes['Nombre Completo'] = df_participantes['Nombre'] + " " + df_participantes['Apellido']

            st.subheader("Asignar Papel del Elenco")
            
            with st.form("form_personaje"):
                p_id = st.selectbox("Seleccionar Participante", options=df_participantes['id_participante'], 
                                   format_func=lambda x: df_participantes[df_participantes['id_participante']==x]['Nombre Completo'].iloc[0])
                
                # 'Descripción' con D mayúscula según tu HeidiSQL (image_223b63)
                nombre_papel = st.text_input("Nombre del Personaje (Ej: Barrabás, La Verónica)")

                if st.form_submit_button("Asignar Personaje"):
                    cur = db.cursor()
                    sql = "INSERT INTO personajes (Descripción, id_participante) VALUES (%s, %s)"
                    cur.execute(sql, (nombre_papel, int(p_id)))
                    db.commit()
                    cur.close()
                    st.success(f"✅ ¡Papel de '{nombre_papel}' asignado con éxito!")
                    st.rerun()
        except Exception as e:
            st.error(f"⚠️ Hubo un detalle: {e}")

# --- CIERRE DE CONEXIÓN (Al final de todo el archivo, sin espacios al inicio) ---
if 'db' in locals() and db.is_connected():
    db.close()
















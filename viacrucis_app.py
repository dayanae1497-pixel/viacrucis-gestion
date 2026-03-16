import streamlit as st

import pandas as pd

import mysql.connector



st.set_page_config(page_title="Viacrucis 2026 - Gestión", layout="wide")

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



st.sidebar.markdown(f"👤 **Usuario:** {st.session_state['usuario_nom']}")

if st.sidebar.button("Cerrar Sesión"):

    st.session_state['autenticado'] = False

    st.rerun()



nombres_tabs = ["👥 Personal", "💰 Economía", "📦 Inventario"]

if st.session_state['usuario_rol'] == 1:
    with tabs[3]:
        st.header("📝 Registro y Gestión de Datos")
   
        opc = st.radio("¿Qué deseas hacer?", 
                        ["Registrar Nuevo", "Gestionar Existentes"], 
                        horizontal=True)
        
        if opc == "Registrar Nuevo":
            sub_opc = st.selectbox("Selecciona qué registrar:", 
                                   ["Gasto Nuevo", "Abono de Patrocinante", "Nuevo Patrocinante", "Nuevo Participante", "Nuevo Personaje"])
            
            if sub_opc == "Gasto Nuevo":
                with st.form("nuevo_gasto"):
                    con = st.text_input("Concepto")
                    mon = st.number_input("Monto ($)", min_value=0.0)
                    fec = st.date_input("Fecha")
                    if st.form_submit_button("Guardar Gasto"):
                        cur = db.cursor()
                        cur.execute("INSERT INTO gastos (concepto, monto, `fecha del gasto`) VALUES (%s, %s, %s)", (con, mon, fec))
                        db.commit()
                        st.success("✅ Gasto guardado.")
                        st.rerun()
            
            # ... (Aquí mantienes tus bloques existentes de Abono, Nuevo Patrocinante, Participante y Personaje)
            # Solo asegúrate de que el flujo de 'elif' sea coherente con sub_opc

        elif opc == "Gestionar Existentes":
            st.divider()
            modo_gestion = st.selectbox("Selecciona tabla para Editar/Eliminar:", 
                                       ["Patrocinantes", "Gastos", "Vestuario", "Participantes"])

            if modo_gestion == "Patrocinantes":
                df_edit = pd.read_sql("SELECT * FROM patrocinantes", db)
                id_sel = st.selectbox("Seleccionar Negocio", options=df_edit['id_patrocinante'], 
                                     format_func=lambda x: df_edit[df_edit['id_patrocinante']==x]['negocio'].iloc[0])
                fila = df_edit[df_edit['id_patrocinante'] == id_sel].iloc[0]
                
                with st.form("edit_patro"):
                    n_nom = st.text_input("Nombre del Negocio", value=fila['negocio'])
                    n_mon = st.number_input("Monto Pactado ($)", value=float(fila['monto a pagar']))
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Guardar"):
                        cur = db.cursor()
                        cur.execute("UPDATE patrocinantes SET negocio=%s, `monto a pagar`=%s WHERE id_patrocinante=%s", (n_nom, n_mon, id_sel))
                        db.commit()
                        st.rerun()
                    if c2.form_submit_button("🗑️ Eliminar"):
                        cur = db.cursor()
                        cur.execute("DELETE FROM pago_patrocinantes WHERE id_patrocinante=%s", (id_sel,))
                        cur.execute("DELETE FROM patrocinantes WHERE id_patrocinante=%s", (id_sel,))
                        db.commit()
                        st.rerun()

            elif modo_gestion == "Gastos":
                df_g = pd.read_sql("SELECT * FROM gastos", db)
                id_g = st.selectbox("Gasto", options=df_g['id_gasto'], 
                                   format_func=lambda x: f"{df_g[df_g['id_gasto']==x]['concepto'].iloc[0]} (${df_g[df_g['id_gasto']==x]['monto'].iloc[0]})")
                if st.button("🗑️ Eliminar Gasto"):
                    cur = db.cursor()
                    cur.execute("DELETE FROM gastos WHERE id_gasto=%s", (id_g,))
                    db.commit()
                    st.rerun()

            elif modo_gestion == "Participantes":
                df_part = pd.read_sql("SELECT id_participante, Nombre, Apellido, teléfono FROM participantes", db)
                id_p = st.selectbox("Participante", options=df_part['id_participante'], 
                                   format_func=lambda x: f"{df_part[df_part['id_participante']==x]['Nombre'].iloc[0]} {df_part[df_part['id_participante']==x]['Apellido'].iloc[0]}")
                fila_p = df_part[df_part['id_participante'] == id_p].iloc[0]
                
                with st.form("edit_part"):
                    n_tel = st.text_input("Actualizar Teléfono", value=fila_p['teléfono'])
                    if st.form_submit_button("💾 Actualizar Datos"):
                        cur = db.cursor()
                        cur.execute("UPDATE participantes SET teléfono=%s WHERE id_participante=%s", (n_tel, id_p))
                        db.commit()
                        st.success("Teléfono actualizado.")
                        st.rerun()

            elif modo_gestion == "Vestuario":
                df_v = pd.read_sql("SELECT * FROM vestuario_final", db)
                id_v = st.selectbox("Pieza", options=df_v['id_vestuario'], format_func=lambda x: df_v[df_v['id_vestuario']==x]['descripcion'].iloc[0])
                with st.form("edit_v"):
                    n_desc = st.text_input("Descripción", value=df_v[df_v['id_vestuario']==id_v]['descripcion'].iloc[0])
                    n_piz = st.number_input("Piezas", value=int(df_v[df_v['id_vestuario']==id_v]['piezas'].iloc[0]))
                    if st.form_submit_button("💾 Guardar"):
                        cur = db.cursor()
                        cur.execute("UPDATE vestuario_final SET descripcion=%s, piezas=%s WHERE id_vestuario=%s", (n_desc, n_piz, id_v))
                        db.commit()
                        st.rerun()

# Cierre de conexión al final del script
if 'db' in locals() and db.is_connected():
    db.close()





if 'db' in locals() and db.is_connected():

    db.close()

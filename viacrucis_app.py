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
# 2. LOGICA DE CONEXIÓN A LA BASE DE DATOS (INTACTA)
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
st.sidebar.markdown(f"👤 **Usuario Activo:**\n### {st.session_state

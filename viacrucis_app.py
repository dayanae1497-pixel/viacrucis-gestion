import base64
import os

# 1. Función para convertir imagen local a Base64
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# 2. Obtener las cadenas Base64
# "Presente.png" para el Banner
# "imagen.png" para el Fondo de todo el sistema
bin_banner = get_base64_img("assets/Presente.png")
bin_fondo = get_base64_img("assets/imagen.png")

# 3. Inyectar el CSS corregido
st.markdown(f"""
    <style>
    /* FONDO DE TODO EL SISTEMA (imagen.png) */
    .stApp {{
        background-image: linear-gradient(rgba(50, 19, 84, 0.85), rgba(13, 2, 26, 0.95)), 
                          url("data:image/png;base64,{bin_fondo}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* BANNER DEL SISTEMA (Presente.png) */
    .header-sistema {{
        background-image: linear-gradient(rgba(21, 3, 36, 0.4), rgba(21, 3, 36, 0.4)), 
                          url("data:image/png;base64,{bin_banner}");
        background-size: cover;
        background-position: center;
        border-radius: 8px;
        padding: 45px 30px;
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 4px solid #e5b82b;
    }}
    </style>
""", unsafe_allow_html=True)

¡Espero que este diseño institucional y el ajuste de código hagan que tu sistema luzca impecable! Avísame si necesitas cualquier otro ajuste.

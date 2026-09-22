import streamlit as st
import os
import requests
from utils.logger import setup_streamlit_logger

st.set_page_config(
    page_title="Identificación del Usuario",
    page_icon= "🔐"
)

logger = setup_streamlit_logger()

# Si ya está logueado -> Enviarlo al chat
if st.session_state.token is not None:
    st.switch_page("pages/Chat.py")

st.title("Iniciar Sesión")

username = st.text_input("Usuario")
password = st.text_input("Contraseña", type= "password")

if st.button("Ingresar"):
    raw_api_url = os.getenv("API_URL", "http://localhost:8000")
    if "/agent" in raw_api_url:
        api_base = raw_api_url.split("/agent")[0].rstrip("/")
    else:
        api_base = raw_api_url.rstrip("/")
    url = f"{api_base}/auth/token"
    data = {
        "username": username,
        "password": password
    }
    logger.info(f"Enviado POST a URL: {url}")
    logger.info(f"Payload enviado: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=10)

        logger.info(f"⬅️ Status Code: {response.status_code}")
        logger.info(f"⬅️ Response Body: {response.text}")

        if response.status_code == 200:
            st.session_state["token"] = response.json().get("access_token")
            st.success("¡Inicio de sesión exitoso! Redirigiendo...")
            st.switch_page("pages/Chat.py")
        elif response.status_code == 401:
            st.error("Credenciales inválidas: Usuario o contraseña incorrectos.")
        else:
            detail = response.json().get("detail", response.text) if response.headers.get("content-type", "").startswith("application/json") else response.text
            st.error(f"Error al iniciar sesión ({response.status_code}): {detail}")
    
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Error de conexión al endpoint: {url}")
        st.error(f"No se pudo conectar con el servidor backend en {url}. Verifica que esté en ejecución.")
    except Exception as e:
        logger.error(f"❌ Error al llamar al endpoint: {e}")
        st.error(f"Ocurrió un error inesperado al iniciar sesión: {e}")


















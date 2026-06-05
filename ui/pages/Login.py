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
    API_URL = os.getenv("API_URL")
    url = f"{API_URL}/auth/token"
    data = {
        "username": username,
        "password": password
    }
    logger.info(f"Enviado POST a URL: {url}")
    logger.info(f"Payload enviado: {data}")
    
    try:
        response = requests.post(url, json= data)

        logger.info(f"⬅️ Status Code: {response.status_code}")
        logger.info(f"⬅️ Response Body: {response.text}")
        logger.info(f"⬅️ JSON: {response.json()}")

        if response.status_code == 200:
            st.session_state["token"] = response.json()["access_token"]
            st.success("Inicio de sesión exitoso! Redirigiendo...")
            st.switch_page("pages/Chat.py")
    
    except Exception as e:
        logger.error(f"❌ Error al llamar al endpoint: {e}")
        st.error("Usuario o contraseña inválidos")


















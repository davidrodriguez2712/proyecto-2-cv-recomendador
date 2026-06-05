import streamlit as st
import requests
from streamlitui.loadui import LoadStreamlitUI
import requests
import os

ui = LoadStreamlitUI()
user_input = ui.load_streamlit_ui()

if st.session_state.token is None:
    st.switch_page("pages/Login.py")

token = st.session_state["token"]
bearer = "bearer"

headers = {"Authorization": f"Bearer {token}"}

user_message = st.chat_input("Escriba su mensaje")

if st.session_state.UploadPDF and st.session_state.InicioBusqueda:
    with st.spinner("Analizando el CV..."):
        API_URL = os.getenv("API_URL")
        #url = "http://127.0.0.1:8000/agent/cv-upload"
        url = f"{API_URL}/agent/cv-upload"
        cv_file = ui.cv
        file = {"file": (cv_file.name, cv_file, cv_file.type)}
        response = requests.post(url= url, files=file, headers= headers)
        try:
            data = response.json()
            respuesta_usuario = data.get("respuesta_empleos_recomendados")
            cv_resumen = data.get("cv_resumen")
            st.write("Hemos analizado tu CV, la cual resumimos de esta forma:\n", cv_resumen)
            st.write("En base a ello, te recomendamos las siguientes ofertas laborales:\n", respuesta_usuario)
        except Exception as e:
            st.error("Ha sucedido un problema, inténtelo más tarde")
            st.error(f"Error: {e}")




































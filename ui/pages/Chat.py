import streamlit as st
import requests
import os
from streamlitui.loadui import LoadStreamlitUI

ui = LoadStreamlitUI()
user_input = ui.load_streamlit_ui()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("pages/Login.py")

token = st.session_state["token"]
headers = {"Authorization": f"Bearer {token}"}
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Flujo 1: Búsqueda y Evaluación de CV (Barra Lateral) ---
if st.session_state.get("UploadPDF") and st.session_state.get("InicioBusqueda"):
    with st.spinner("Analizando el CV..."):
        url = f"{API_URL}/agent/cv-upload"
        cv_file = ui.cv
        file = {"file": (cv_file.name, cv_file, cv_file.type)}
        response = requests.post(url=url, files=file, headers=headers)
        try:
            data = response.json()
            respuesta_usuario = data.get("respuesta_empleos_recomendados")
            cv_resumen = data.get("cv_resumen")
            st.success("¡CV analizado con éxito!")
            st.markdown("### Resumen de tu perfil:")
            st.info(cv_resumen)
            st.markdown("### Ofertas laborales recomendadas:")
            st.markdown(respuesta_usuario, unsafe_allow_html=True)
        except Exception as e:
            st.error("Ha sucedido un problema al analizar el CV, inténtelo más tarde.")
            st.error(f"Detalle: {e}")

# --- Flujo 2: Asistente Conversacional ReAct (Cuerpo Principal) ---
st.markdown("---")
st.subheader("💬 Asistente Laboral ChambeaPe")
st.caption("Pregúntame sobre rangos salariales en Perú, tendencias laborales o cómo mejorar tu perfil.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de carrera. ¿Tienes alguna duda sobre salarios en Perú, ofertas laborales o tu CV?"}
    ]

# Renderizar historial previo
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Captura de nuevo mensaje
user_query = st.chat_input("Escribe tu consulta aquí...")
if user_query:
    st.session_state.chat_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Preparar payload para API (últimos mensajes como historial)
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages[:-1]
        if m["role"] in ["user", "assistant"]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Consultando fuentes y redactando respuesta..."):
            try:
                chat_url = f"{API_URL}/agent/general-query"
                payload = {
                    "query": user_query,
                    "history": history_payload
                }
                res = requests.post(chat_url, json=payload, headers=headers, timeout=90)
                if res.status_code == 200:
                    resp_data = res.json()
                    answer = resp_data.get("response", "Sin respuesta.")
                    tools_used = resp_data.get("tools_used", [])

                    if tools_used:
                        tool_badges = []
                        if "consultar_sueldos_peru" in tools_used:
                            tool_badges.append("💼 Base Salarial Perú")
                        if "search_tavily" in tools_used:
                            tool_badges.append("🌐 Búsqueda Web")
                        st.caption(f"Fuentes consultadas: {' | '.join(tool_badges)}")

                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = f"Error {res.status_code}: {res.text}"
                    st.error(err_msg)
            except Exception as e:
                st.error(f"Error de conexión con el asistente: {e}")

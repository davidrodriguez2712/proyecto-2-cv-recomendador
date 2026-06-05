import streamlit as st
import os
from uiconfigfile import Config


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}
    
    # Interfaz del usuario
    def load_streamlit_ui(self):
        st.set_page_config(
            page_title= self.config.get_page_title(),
            page_icon= "💼"
        )
        st.header("💼 " + self.config.get_page_title())
        st.subheader("Proyecto en Desarrollo... Por ahora la única funcionalidad es la de Subir CV en PDF --> Hacer MATCH con los mejores")
        st.session_state.timeframe = ''
        st.session_state.IsFetchButtonClicked = False
        st.session_state.UploadPDF = False
        st.session_state.InicioBusqueda = False

        with st.sidebar:
            user_options = self.config.get_user_options()

            self.user_controls["user_options"] = st.selectbox(label="Elige tu Perfil para Iniciar", options= user_options, index= 0)
            
            if self.user_controls["user_options"] == "Buscando Trabajo":
                empleado_options = self.config.get_usecase_user_options()
                self.user_controls["empleado_options"] = st.selectbox("Elige la Funcionalidad", empleado_options, index= 0)
                if self.user_controls["empleado_options"] == "Buscar Empleos":
                    cv_pdf = st.file_uploader(label="📂 Subir archivo PDF", type=[".pdf"])
                    self.cv = cv_pdf
                    if cv_pdf:
                        st.session_state.UploadPDF = True
                        print(f"Se detectó el cv_pdf")
                        boton_activar_busqueda = st.button(label="Iniciar Búsqueda", icon="🔎")
                        if boton_activar_busqueda:
                            st.session_state.InicioBusqueda = True
                            print(st.session_state.InicioBusqueda)

            if self.user_controls["user_options"] == "Reclutador":
                reclutador_options = self.config.get_usecase_reclutador_options()
                self.user_controls["reclutador_options"] = st.selectbox("Elige la Funcionalidad", reclutador_options)

        return self.user_controls    


            
































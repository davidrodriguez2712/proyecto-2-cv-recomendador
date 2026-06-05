import streamlit as st
import logging

logger = logging.getLogger("Proyecto1.display_results")

class DisplayResultStreamlit:
    def __init__(self, graph, user_message, cv_objeto = None):
        self.graph = graph
        self.user_message = user_message
        self.cv_objeto = cv_objeto

    def display_results_on_ui(self):
        graph = self.graph
        user_message = self.user_message
        cv_objeto = self.cv_objeto
        logger.debug("El graph y user_message se cargó correctamente al método 'display'")
        with st.spinner("⏳ Iniciando búsqueda de las mejores ofertas de trabajo..."):
            results = graph.invoke({"cv_object": cv_objeto})
            logger.debug("Se hizo correctamente el invoke en 'display'...")
            logger.debug(f"Tipo de Variable de 'results' : {type(results)}")
            #logger.debug(f"Contenido de 'results' : {results}")
            #print(f"Contenido de 'results' : {results}")
            #st.write(results["respuesta_empleos_recomendados"])
            #logger.debug("Se llegó a instanciar el método st.write para la respuesta del 'results'")
            st.markdown(body="###Te presentamos las mejores ofertas de trabajo que hacen match con tu CV:")
            st.markdown(results["respuesta_empleos_recomendados"], unsafe_allow_html= True)
        




        





























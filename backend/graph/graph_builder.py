from state.state_graph import State, CVData
from langgraph.graph import StateGraph, END, START
#from langgraph.prebuilt import tools_condition, ToolNode
from typing import TypedDict, Annotated, Literal, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph.message import add_messages
from nodes.cv_nodes import CVNodes
import logging

logger = logging.getLogger("Proyecto1.graph_builder")

class GraphBuilder:
    def __init__(self):
        self.graph = StateGraph(State)
        

    # cuando se crear los nodos, no sería necesario que sea async
    def graph_cv(self):
        """
        Construcción del grafo para el proceso de Recomendador de Ofertas Laborales
        """
        cv_nodes = CVNodes()

        # nodes
        self.graph.add_node("cargar_documentos_pdf", cv_nodes.cargar_documentos_pdf)
        self.graph.add_node("transformacion_cv", cv_nodes.transformacion_cv)
        logger.debug("Se cargó los nodos cargar_documentos y transformación_cv correctamente")
        self.graph.add_node("embedding_cv", cv_nodes.embedding_cv)
        self.graph.add_node("busq_simil_cv_vs_empleos", cv_nodes.busq_simil_cv_vs_empleos)
        self.graph.add_node("transformacion_respuesta_busqueda", cv_nodes.transformacion_respuesta_busqueda)
        self.graph.add_node("respuesta_usuario_cv", cv_nodes.respuesta_usuario_cv)
        logger.debug("Se cargaron todos los nodos correctamente")
        # edges
        self.graph.add_edge(START, "cargar_documentos_pdf")
        self.graph.add_edge("cargar_documentos_pdf", "transformacion_cv")
        self.graph.add_edge("transformacion_cv", "embedding_cv")
        self.graph.add_edge("embedding_cv", "busq_simil_cv_vs_empleos")
        self.graph.add_edge("busq_simil_cv_vs_empleos", "transformacion_respuesta_busqueda")
        self.graph.add_edge("transformacion_respuesta_busqueda", "respuesta_usuario_cv")
        self.graph.add_edge("respuesta_usuario_cv", END)
        logger.debug("Se agregaron todos los nodos y edges del grafo")
        #self.graph.compile()
        #logger.debug("Se compiló el grafo")

    def compile_graph(self):
        """
        Compila el grafo adecuado
        """
        self.graph_cv()
        logger.debug("Se está retornando el grafo compilado...")
        app = self.graph.compile()

        # SOLO estos campos saldrán en la respuesta del graph
        app = app.pick([
            "cv_data",
            "cv_metadata",
            "cv_texto",
            "id_cv",
            "cv_resumen",
            "cv_empleos_recomendados",
            "cv_feedback",
            "respuesta_empleos_recomendados",
        ])
        return app
        

    


















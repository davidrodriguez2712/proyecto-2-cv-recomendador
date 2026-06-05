from dotenv import load_dotenv, find_dotenv
import os
from langgraph.graph import StateGraph, END, START
from llms.openaillm import OpenAILLM
from state.react_state_graph import StateAgentReact
from langgraph.prebuilt import ToolNode, tools_condition
from nodes.react_agent import ReactNode

class ReactAgent:
    def __init__(self):
        #self.llm_model = OpenAILLM().llm
        #self.embedding_model = OpenAILLM().embedding_llm
        self.graph = StateGraph(StateAgentReact)

    def graph_builder_react(self):
        """Flujo de Langgraph para construir el agente conversacional"""
        
        nodes_agent = ReactNode()
        # nodes
        self.graph.add_node("main_query_analizer", nodes_agent.main_query_analizer)
        self.graph.add_node("router_decision", nodes_agent.route_decision)
        self.graph.add_node("node_rag", )
        self.graph.add_node("node_search_web", )
        self.graph.add_node("node_llm", nodes_agent.llm_reponse )

        # edges
        self.graph.add_edge(START, "main_query_analizer")
        self.graph.add_conditional_edges(
            "main_query_analizer",
            nodes_agent.route_decision,
            {
                "rag": "node_rag",
                "web": "node_search_web",
                "llm": "node_llm"
            }
        )
        self.graph.add_edge("main_query_analizer", END)

        # compilation
    def compile_react(self):
        self.graph_builder_react()
        #self.graph.compile()
        return self.graph.compile()


























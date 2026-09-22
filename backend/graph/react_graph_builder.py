import logging
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from state.react_state_graph import StateAgentReact
from llms.openaillm import OpenAILLM
from tools.web_search import search_tavily
from tools.salary_tool import consultar_sueldos_peru

logger = logging.getLogger("backend.react_graph_builder")

SYSTEM_PROMPT = """Eres el Asistente Profesional de Empleo y Carrera de ChambeaPe.
Tu misión es guiar al usuario en su búsqueda de empleo, orientación laboral, optimización de CV y consultas salariales en Perú.

Reglas de uso de herramientas:
1. 'consultar_sueldos_peru': Invócala obligatoriamente cuando el usuario consulte por rangos salariales, cuánto se gana, remuneraciones o tarifas de mercado en Perú. Basa tu respuesta en los datos que devuelva la herramienta.
2. 'search_tavily': Invócala cuando el usuario pida información reciente, noticias, empresas específicas, tecnologías emergentes o temas que requieran verificación en la web.
3. Si el usuario hace preguntas generales (consejos de CV, preparación para entrevistas, preguntas motivacionales), responde directamente con tu conocimiento profesional sin invocar herramientas innecesarias.

Estilo:
- Profesional, cordial, empático y motivador.
- Siempre invita al usuario a un siguiente paso accionable al final de tu respuesta.
"""

class ReactAgent:
    def __init__(self):
        self.tools = [search_tavily, consultar_sueldos_peru]
        self.llm = OpenAILLM().llm.bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools)
        self.graph = StateGraph(StateAgentReact)

    async def agent_node(self, state: StateAgentReact):
        """Nodo principal que invoca al LLM con las herramientas vinculadas."""
        messages = list(state["messages"])
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = await self.llm.ainvoke(messages)
        return {"messages": [response]}

    def graph_builder_react(self):
        """Construye el flujo ReAct con ToolNode y tools_condition."""
        self.graph.add_node("agent", self.agent_node)
        self.graph.add_node("tools", self.tool_node)

        self.graph.add_edge(START, "agent")
        self.graph.add_conditional_edges(
            "agent",
            tools_condition,
        )
        self.graph.add_edge("tools", "agent")

    def compile_react(self):
        """Compila y retorna el grafo ejecutable."""
        self.graph_builder_react()
        return self.graph.compile()

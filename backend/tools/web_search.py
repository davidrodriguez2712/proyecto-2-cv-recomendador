import os
import logging
from tavily import TavilyClient
from langchain_core.tools import tool

logger = logging.getLogger("backend.web_search")

@tool
def search_tavily(query: str) -> str:
    """Permite buscar información actualizada, noticias, empresas o tendencias laborales en internet usando Tavily.
    Úsala cuando la consulta requiera información externa, reciente o de hechos actuales."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "La búsqueda web no está configurada (falta TAVILY_API_KEY)."

        tavily_client = TavilyClient(api_key=api_key)
        response = tavily_client.search(
            query=query,
            max_results=4,
            topic="general",
            search_depth="basic"
        )

        results = response.get("results", [])
        if not results:
            return "No se encontraron resultados web para esta búsqueda."

        snippets = [f"- {doc.get('title', '')}: {doc.get('content', '')}" for doc in results]
        return "\n".join(snippets)

    except Exception as e:
        logger.exception(f"Error en búsqueda web Tavily: {e}")
        return f"No se pudo completar la búsqueda en la web en este momento. Detalle: {e}"

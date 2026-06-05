from dotenv import load_dotenv, find_dotenv
import os
from tavily import TavilyClient
from langchain_core.tools import tool

@tool
def search_tavily(query: str):
    """Permite la búsqueda web mediante la API de Talivy"""
    tavily_client = TavilyClient(api_key= os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(
        query= query,
        max_results= 5,
        topic= "general",
        search_depth= "basic"
    )

    response_final = [doc["content"] for doc in response["results"]]

    return response_final











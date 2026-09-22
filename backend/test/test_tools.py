import pytest
from backend.tools.web_search import search_tavily
from backend.tools.salary_tool import consultar_sueldos_peru

def test_salary_tool_structure():
    assert callable(consultar_sueldos_peru)
    assert consultar_sueldos_peru.name == "consultar_sueldos_peru"
    assert "sueldo" in consultar_sueldos_peru.description.lower()

def test_web_search_tool_structure():
    assert callable(search_tavily)
    assert search_tavily.name == "search_tavily"
    assert "web" in search_tavily.description.lower() or "tavily" in search_tavily.description.lower()

def test_salary_tool_resilience_on_invalid_input():
    result = consultar_sueldos_peru.invoke({"consulta": ""})
    assert isinstance(result, str)
    assert "indica" in result.lower() or "error" in result.lower() or "sueldo" in result.lower()

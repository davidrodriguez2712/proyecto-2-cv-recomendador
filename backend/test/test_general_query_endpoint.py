import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from backend.schemas import GeneralQueryRequest

@pytest.mark.asyncio
async def test_general_query_endpoint_logic():
    mock_compiled = AsyncMock()
    mock_compiled.ainvoke.return_value = {
        "messages": [
            AIMessage(content="Respuesta del asistente laboral")
        ]
    }

    with patch("backend.routers.agent.react_graph_instance", mock_compiled):
        from backend.routers.agent import process_general_query
        req = GeneralQueryRequest(query="Hola, ¿cómo estás?", history=[])
        res = await process_general_query(req, username="admin")
        assert res.response == "Respuesta del asistente laboral"
        assert res.tools_used == []

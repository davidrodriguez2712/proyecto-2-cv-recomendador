import pytest
from pydantic import ValidationError
from backend.schemas import ChatMessageDTO, GeneralQueryRequest, GeneralQueryResponse
from backend.state.react_state_graph import StateAgentReact
from langchain_core.messages import HumanMessage, AIMessage

def test_chat_message_dto():
    msg = ChatMessageDTO(role="user", content="Hola")
    assert msg.role == "user"
    assert msg.content == "Hola"

def test_general_query_request():
    req = GeneralQueryRequest(
        query="¿Cuánto gana un programador?",
        history=[ChatMessageDTO(role="user", content="Hola"), ChatMessageDTO(role="assistant", content="Hola, ¿en qué te ayudo?")]
    )
    assert len(req.history) == 2
    assert req.query == "¿Cuánto gana un programador?"

def test_general_query_response():
    resp = GeneralQueryResponse(response="Respuesta generada", tools_used=["consultar_sueldos_peru"])
    assert resp.response == "Respuesta generada"
    assert resp.tools_used == ["consultar_sueldos_peru"]

def test_state_agent_react_types():
    state: StateAgentReact = {
        "messages": [HumanMessage(content="Hola")],
        "user": "test_user"
    }
    assert len(state["messages"]) == 1
    assert state["user"] == "test_user"

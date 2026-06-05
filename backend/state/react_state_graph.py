from pydantic import BaseModel, Field
from typing import TypedDict, List, Literal
import os

class StateAgentReact(TypedDict):
    message_user = str
    route_query = str
    history_messages = List[str]
    response_user = str
    user = str

class RouterQuery(BaseModel):
    """Formato estructurado que decide la intención del usuario"""
    route: Literal["rag, web, llm"] = Field(
        ...,
        description= "Ruta elegida para responder la consulta"
    )
    reason: str = Field(
        ...,
        description= "Es la razón del por qué eligió la ruta"
    )















from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class StateAgentReact(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user: Optional[str]

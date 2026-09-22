import pytest
from backend.graph.react_graph_builder import ReactAgent
from langchain_core.messages import HumanMessage

def test_react_graph_compilation():
    agent = ReactAgent()
    compiled = agent.compile_react()
    assert compiled is not None
    # Verifica que los nodos agent y tools existan
    node_names = list(compiled.nodes.keys())
    assert "agent" in node_names
    assert "tools" in node_names

# ReAct Agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar y dejar 100% operativo el pipeline del asistente conversacional ReAct en LangGraph con herramientas de búsqueda híbrida salarial (Pinecone + BM25) y búsqueda web (Tavily), conectándolo al endpoint FastAPI `/agent/general-query` y a la interfaz de chat en Streamlit sin dependencia de Redis.

**Architecture:** Se construye un agente ReAct estándar en LangGraph (`ChatOpenAI.bind_tools` + `ToolNode` + `tools_condition`). El agente decide autónomamente si responder directo como asesor laboral o invocar `consultar_sueldos_peru` o `search_tavily`. La memoria de conversación se mantiene en el frontend y se transfiere en el payload de cada solicitud hacia el estado `StateAgentReact` con el reducer `add_messages`.

**Tech Stack:** Python 3.13, FastAPI 0.121, LangGraph 0.6.10, LangChain 0.3.27, OpenAI (`gpt-4o-mini`, `text-embedding-3-small`), Pinecone 7.3, pinecone-text (BM25), Streamlit 1.50, pytest.

**Spec:** `docs/superpowers/specs/2026-09-22-react-agent-pipeline-design.md`

## Global Constraints

- Python 3.13 compatible, código puramente asíncrono en endpoints y nodos I/O.
- Pydantic v2 (`model_dump()`, no `.dict()`).
- Resolución de rutas de conocimiento mediante `pathlib.Path(__file__).resolve().parent...`.
- Cero dependencias de Redis en este flujo.
- Manejo de fallos en herramientas con capturas `try/except` amigables para evitar excepciones no controladas.
- Límite de recursión en LangGraph de 10 iteraciones.

## Review Focus

1. **Credenciales o conexión a Pinecone fallida:** La herramienta `consultar_sueldos_peru` debe capturar la excepción y devolver un mensaje descriptivo sin interrumpir la ejecución del LLM.
2. **`TAVILY_API_KEY` ausente o cuota agotada:** La herramienta `search_tavily` debe capturar el error y permitir al LLM responder con conocimiento general.
3. **Historial de conversación vacío:** El endpoint y el grafo deben aceptar `history=[]` sin fallar.
4. **Pregunta sin necesidad de herramientas:** Preguntas conceptuales o de redacción de CV no deben disparar llamadas innecesarias a herramientas.
5. **Historial multi-turno con alternancia de roles:** La conversión de `history` debe preservar el orden cronológico estricto de mensajes de usuario y asistente.

---

### Task 1: Fix Security & Auth Prerequisites

**Files:**
- Modify: `backend/core/security.py:75-98`
- Modify: `backend/routers/admin.py:40-65`
- Test: `backend/test/test_security_patch.py`

**Interfaces:**
- Consumes: `schemas.LoginRequest`, `database.get_db`, `pwd_context`
- Produces: Autenticación segura verificando `pwd_context.verify` y validación correcta del rol admin usando `user.get("user")`.

- [ ] **Step 1: Write the failing test**

Crear `backend/test/test_security_patch.py`:
```python
import pytest
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_verification_logic():
    hashed = pwd_context.hash("secret123")
    assert pwd_context.verify("secret123", hashed) is True
    assert pwd_context.verify("wrong_password", hashed) is False
```

- [ ] **Step 2: Run test to verify test environment**

Run: `pytest backend/test/test_security_patch.py -v`  
Expected: PASS (verifica la librería passlib y bcrypt).

- [ ] **Step 3: Modify `backend/core/security.py` and `backend/routers/admin.py`**

En `backend/core/security.py`:
Reactivar la validación de contraseña en `login`:
```python
@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login(db: db_dependency, data: LoginRequest):
    try:
        response = await db.execute(
            select(User).where(User.username == data.username)
        )
        user = response.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User doesn't exist")
        if not pwd_context.verify(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is wrong")
        
        token = create_token(id_user=user.id, rol=user.rol, user=user.username, expires_delta=timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.debug(f"Error identificado en login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication server error")
```

En `backend/routers/admin.py`:
Corregir la validación de permisos de admin en `create_user`:
```python
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: user_dependency, user_form: CreateUser):
    try:
        response = await db.execute(
            select(User).where(User.username == user.get("user"))
        )
        current_user = response.scalar_one_or_none()
        if current_user is None or current_user.rol != "admin":
            raise HTTPException(status_code=401, detail="Don't have permissions for this endpoint.")
        
        userdb = User(
            username=user_form.user,
            email=user_form.email,
            rol=user_form.rol,
            name=user_form.name,
            lastname=user_form.lastname,
            hashed_password=pwd_context.hash(user_form.hashed_password)
        )
        db.add(userdb)
        await db.commit()
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.debug(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Creation user Failed")
```

- [ ] **Step 4: Run test to verify**

Run: `pytest backend/test/test_security_patch.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/core/security.py backend/routers/admin.py backend/test/test_security_patch.py
git commit -m "fix(security): reactivate password validation and fix admin check"
```

---

### Task 2: State Definition & API DTOs

**Files:**
- Modify: `backend/state/react_state_graph.py`
- Modify: `backend/schemas.py`
- Test: `backend/test/test_state_dto.py`

**Interfaces:**
- Consumes: `langchain_core.messages.BaseMessage`, `langgraph.graph.message.add_messages`
- Produces: `StateAgentReact`, `ChatMessageDTO`, `GeneralQueryRequest`, `GeneralQueryResponse`

- [ ] **Step 1: Write the failing test**

Crear `backend/test/test_state_dto.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/test/test_state_dto.py -v`  
Expected: FAIL (los DTOs y StateAgentReact aún no tienen las firmas esperadas).

- [ ] **Step 3: Implement minimal code**

Actualizar `backend/state/react_state_graph.py`:
```python
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class StateAgentReact(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user: Optional[str]
```

Actualizar `backend/schemas.py` añadiendo al final:
```python
from typing import Literal, List

class ChatMessageDTO(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class GeneralQueryRequest(BaseModel):
    query: str
    history: List[ChatMessageDTO] = []

class GeneralQueryResponse(BaseModel):
    response: str
    tools_used: List[str] = []
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/test/test_state_dto.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/state/react_state_graph.py backend/schemas.py backend/test/test_state_dto.py
git commit -m "feat(state): define StateAgentReact with add_messages and chat DTOs"
```

---

### Task 3: Implement ReAct Tools (`consultar_sueldos_peru` & `search_tavily`)

**Files:**
- Create: `backend/tools/salary_tool.py`
- Modify: `backend/tools/web_search.py`
- Test: `backend/test/test_tools.py`

**Interfaces:**
- Consumes: `backend/knowledge/bm25_fit.pkl`, `OpenAILLM.embedding_llm`, Pinecone index `rag-sueldosperu`, TavilyClient
- Produces: `@tool consultar_sueldos_peru(consulta: str) -> str`, `@tool search_tavily(query: str) -> str`

- [ ] **Step 1: Write the failing test**

Crear `backend/test/test_tools.py`:
```python
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
    # Debe retornar un string descriptivo y no lanzar excepción fatal
    result = consultar_sueldos_peru.invoke({"consulta": ""})
    assert isinstance(result, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/test/test_tools.py -v`  
Expected: FAIL (módulo `salary_tool` no existe).

- [ ] **Step 3: Implement minimal code**

Crear `backend/tools/salary_tool.py`:
```python
import os
from pathlib import Path
import logging
import joblib
from langchain_core.tools import tool
from pinecone import Pinecone
from llms.openaillm import OpenAILLM

logger = logging.getLogger("backend.salary_tool")

@tool
def consultar_sueldos_peru(consulta: str) -> str:
    """Consulta la base de datos de rangos salariales y compensaciones en el mercado laboral de Perú.
    Úsala cuando el usuario pregunte por sueldos, salarios o tarifas de perfiles laborales en Perú."""
    try:
        if not consulta or not consulta.strip():
            return "Por favor indica el puesto o rol profesional sobre el cual deseas consultar el sueldo."

        knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
        bm25_path = knowledge_dir / "bm25_fit.pkl"

        if not bm25_path.exists():
            logger.warning(f"Archivo BM25 no encontrado en: {bm25_path}")
            return "La base de conocimientos salariales no está disponible localmente."

        bm25 = joblib.load(bm25_path)
        vector_sparse = bm25.encode_queries(consulta)

        embedding_llm = OpenAILLM().embedding_llm
        vector_dense = embedding_llm.embed_query(consulta)

        pc = Pinecone()
        index = pc.Index(name="rag-sueldosperu")

        search_res = index.query(
            vector=vector_dense,
            sparse_vector=vector_sparse,
            top_k=5,
            include_metadata=True,
            include_values=False
        )

        matches = search_res.get("matches", [])
        if not matches:
            return "No se encontraron registros salariales exactos para esta consulta en la base de datos."

        extracted_texts = []
        for match in matches:
            meta = match.get("metadata", {})
            text = meta.get("text") or meta.get("contexto") or str(meta)
            extracted_texts.append(text)

        return "\n\n---\n\n".join(extracted_texts)

    except Exception as e:
        logger.exception(f"Error consultando base de sueldos: {e}")
        return f"No fue posible consultar la base de datos salarial en este momento. Detalle: {e}"
```

Actualizar `backend/tools/web_search.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/test/test_tools.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/tools/salary_tool.py backend/tools/web_search.py backend/test/test_tools.py
git commit -m "feat(tools): add salary hybrid search tool and resilient web search tool"
```

---

### Task 4: ReAct Graph Builder (`ReactAgent`)

**Files:**
- Modify: `backend/graph/react_graph_builder.py`
- Modify: `backend/nodes/react_agent.py` (mantenerlo limpio o redirigir lógica)
- Test: `backend/test/test_react_graph.py`

**Interfaces:**
- Consumes: `OpenAILLM().llm`, `StateAgentReact`, `search_tavily`, `consultar_sueldos_peru`, `ToolNode`, `tools_condition`
- Produces: `ReactAgent().compile_react()` retornando un `CompiledStateGraph` ejecutable.

- [ ] **Step 1: Write the failing test**

Crear `backend/test/test_react_graph.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/test/test_react_graph.py -v`  
Expected: FAIL (sintaxis rota actual en `react_graph_builder.py`).

- [ ] **Step 3: Implement `ReactAgent`**

Reescribir `backend/graph/react_graph_builder.py`:
```python
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import ChatPromptTemplate
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/test/test_react_graph.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/graph/react_graph_builder.py backend/test/test_react_graph.py
git commit -m "feat(graph): implement autonomous ReAct agent with ToolNode and tools_condition"
```

---

### Task 5: Endpoint `/agent/general-query` in FastAPI

**Files:**
- Modify: `backend/routers/agent.py:61-75`
- Test: `backend/test/test_general_query_endpoint.py`

**Interfaces:**
- Consumes: `ReactAgent().compile_react()`, `GeneralQueryRequest`, `GeneralQueryResponse`
- Produces: `POST /agent/general-query` endpoint funcional

- [ ] **Step 1: Write the failing test**

Crear `backend/test/test_general_query_endpoint.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from backend.schemas import GeneralQueryRequest

@pytest.mark.asyncio
async def test_general_query_endpoint_logic():
    # Simula la ejecución del grafo para validar transformación de entrada y salida
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/test/test_general_query_endpoint.py -v`  
Expected: FAIL (función `process_general_query` no existe).

- [ ] **Step 3: Implement endpoint and helper logic**

En `backend/routers/agent.py`:
Importar DTOs y `ReactAgent`:
```python
from schemas import User, GeneralQueryRequest, GeneralQueryResponse
from graph.react_graph_builder import ReactAgent
from langchain_core.messages import HumanMessage, AIMessage

react_agent = ReactAgent()
react_graph_instance = react_agent.compile_react()

async def process_general_query(request: GeneralQueryRequest, username: str) -> GeneralQueryResponse:
    messages = []
    for msg in request.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=request.query))

    config = {"recursion_limit": 10}
    result = await react_graph_instance.ainvoke(
        {"messages": messages, "user": username},
        config=config
    )

    all_messages = result.get("messages", [])
    last_message = all_messages[-1] if all_messages else AIMessage(content="No se pudo generar respuesta.")
    
    tools_used = []
    for m in all_messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tname = tc.get("name")
                if tname and tname not in tools_used:
                    tools_used.append(tname)

    return GeneralQueryResponse(
        response=last_message.content,
        tools_used=tools_used
    )

@router.post("/general-query", response_model=GeneralQueryResponse, status_code=status.HTTP_200_OK)
async def general_query(db: db_dependecy, user: user_dependency, data: GeneralQueryRequest):
    try:
        response = await db.execute(
            select(User).where(User.username == user.get("user"))
        )
        username = response.scalar_one_or_none()
        if username is None:
            raise HTTPException(status_code=401, detail="User doesn't exist")
        
        return await process_general_query(data, username=user.get("user"))

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error procesando general query: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno procesando la consulta: {str(e)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/test/test_general_query_endpoint.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/routers/agent.py backend/test/test_general_query_endpoint.py
git commit -m "feat(api): implement /agent/general-query endpoint with ReAct execution"
```

---

### Task 6: Streamlit Chat Integration

**Files:**
- Modify: `ui/pages/Chat.py`

**Interfaces:**
- Consumes: `POST /agent/general-query`, `st.session_state.chat_messages`, `st.session_state.token`
- Produces: Chat interactivo multi-turno en vivo en la interfaz de Streamlit

- [ ] **Step 1: Check existing `Chat.py` and prepare integration**

Revisar líneas de `Chat.py` para asegurar que la funcionalidad existente de evaluación de CV PDF se mantenga intacta en la barra lateral mientras el chat ocupa el cuerpo principal.

- [ ] **Step 2: Update `ui/pages/Chat.py`**

Reemplazar la interacción en `ui/pages/Chat.py` con:
```python
import streamlit as st
import requests
import os
from streamlitui.loadui import LoadStreamlitUI

ui = LoadStreamlitUI()
user_input = ui.load_streamlit_ui()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("pages/Login.py")

token = st.session_state["token"]
headers = {"Authorization": f"Bearer {token}"}
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Flujo 1: Búsqueda y Evaluación de CV (Barra Lateral) ---
if st.session_state.get("UploadPDF") and st.session_state.get("InicioBusqueda"):
    with st.spinner("Analizando el CV..."):
        url = f"{API_URL}/agent/cv-upload"
        cv_file = ui.cv
        file = {"file": (cv_file.name, cv_file, cv_file.type)}
        response = requests.post(url=url, files=file, headers=headers)
        try:
            data = response.json()
            respuesta_usuario = data.get("respuesta_empleos_recomendados")
            cv_resumen = data.get("cv_resumen")
            st.success("¡CV analizado con éxito!")
            st.markdown("### Resumen de tu perfil:")
            st.info(cv_resumen)
            st.markdown("### Ofertas laborales recomendadas:")
            st.markdown(respuesta_usuario, unsafe_allow_html=True)
        except Exception as e:
            st.error("Ha sucedido un problema al analizar el CV, inténtelo más tarde.")
            st.error(f"Detalle: {e}")

# --- Flujo 2: Asistente Conversacional ReAct (Cuerpo Principal) ---
st.markdown("---")
st.subheader("💬 Asistente Laboral ChambeaPe")
st.caption("Pregúntame sobre rangos salariales en Perú, tendencias laborales o cómo mejorar tu perfil.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de carrera. ¿Tienes alguna duda sobre salarios en Perú, ofertas laborales o tu CV?"}
    ]

# Renderizar historial previo
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Captura de nuevo mensaje
user_query = st.chat_input("Escribe tu consulta aquí...")
if user_query:
    st.session_state.chat_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Preparar payload para API
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages[:-1]
        if m["role"] in ["user", "assistant"]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Consultando fuentes y redactando respuesta..."):
            try:
                chat_url = f"{API_URL}/agent/general-query"
                payload = {
                    "query": user_query,
                    "history": history_payload
                }
                res = requests.post(chat_url, json=payload, headers=headers, timeout=90)
                if res.status_code == 200:
                    resp_data = res.json()
                    answer = resp_data.get("response", "Sin respuesta.")
                    tools_used = resp_data.get("tools_used", [])

                    if tools_used:
                        tool_badges = []
                        if "consultar_sueldos_peru" in tools_used:
                            tool_badges.append("💼 Base Salarial Perú")
                        if "search_tavily" in tools_used:
                            tool_badges.append("🌐 Búsqueda Web")
                        st.caption(f"Fuentes consultadas: {' | '.join(tool_badges)}")

                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = f"Error {res.status_code}: {res.text}"
                    st.error(err_msg)
            except Exception as e:
                st.error(f"Error de conexión con el asistente: {e}")
```

- [ ] **Step 3: Verify syntax of `ui/pages/Chat.py`**

Run: `python3 -m py_compile ui/pages/Chat.py`  
Expected: Sin errores de sintaxis.

- [ ] **Step 4: Commit**

```bash
git add ui/pages/Chat.py
git commit -m "feat(ui): integrate multi-turn chat in Streamlit with tool badges"
```

---

### Task 7: End-to-End Verification & Test Suite Execution

**Files:**
- Create: `backend/test/test_e2e_react_pipeline.py`
- Modify: `README.md` (actualizar estado del asistente conversacional)

**Interfaces:**
- Consumes: Todos los componentes construidos en Tasks 1-6
- Produces: Validación automatizada de los 3 caminos del agente (general, salarios, web)

- [ ] **Step 1: Write comprehensive test script**

Crear `backend/test/test_e2e_react_pipeline.py`:
```python
import pytest
from backend.graph.react_graph_builder import ReactAgent
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_react_agent_general_advice():
    agent = ReactAgent()
    compiled = agent.compile_react()
    res = await compiled.ainvoke({
        "messages": [HumanMessage(content="¿Cómo puedo destacar mis habilidades técnicas en mi CV?")],
        "user": "test_user"
    })
    last_msg = res["messages"][-1]
    assert len(last_msg.content) > 50
    # No debió invocar herramientas para un consejo general
    assert not getattr(last_msg, "tool_calls", None)

@pytest.mark.asyncio
async def test_react_agent_salary_query():
    agent = ReactAgent()
    compiled = agent.compile_react()
    res = await compiled.ainvoke({
        "messages": [HumanMessage(content="¿Cuánto es el salario promedio de un Data Engineer en Perú?")],
        "user": "test_user"
    })
    messages = res["messages"]
    last_msg = messages[-1]
    assert len(last_msg.content) > 20
    # Verifica que en la cadena existan tool calls o mensajes de herramientas
    tool_invoked = any(hasattr(m, "tool_calls") and m.tool_calls for m in messages) or any(m.type == "tool" for m in messages)
    assert tool_invoked is True
```

- [ ] **Step 2: Run all backend tests**

Run: `pytest backend/test/ -v`  
Expected: Todos los tests pasan exitosamente.

- [ ] **Step 3: Update `README.md`**

Actualizar en `README.md` la tabla de funcionalidades reflejando que el Asistente Conversacional ReAct con RAG de sueldos y búsqueda web ha pasado de "En Proceso" a "Implementado".

- [ ] **Step 4: Commit**

```bash
git add backend/test/test_e2e_react_pipeline.py README.md
git commit -m "docs & test: complete e2e ReAct pipeline verification and update README"
```

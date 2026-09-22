# AGENTS.md - Guía de Desarrollo y Contexto para Agentes de IA

> Este documento sirve como contexto operativo y guía de desarrollo para cualquier agente de inteligencia artificial (o desarrollador) que trabaje en el repositorio **Proyecto 2: CV Recomendador y Asistente de Empleo con LangGraph**.

---

## 1. Visión General del Proyecto

Este sistema es una plataforma inteligente orientada al ecosistema de contratación y búsqueda de empleo en Perú y Latinoamérica. Su arquitectura divide el problema en dos frentes:

1. **Frente del Candidato:**
   - **Evaluación y Recomendación de Empleos:** Ingesta de CVs en formato PDF, extracción de datos estructurados con LLM, generación de embeddings densos, almacenamiento en Pinecone y búsqueda por similitud vectorial contra una base de empleos.
   - **Feedback Personalizado y Análisis de Gaps:** Comparación cualitativa entre el perfil del usuario y los requisitos del puesto (seniority, educación, experiencia y habilidades técnicas).
   - **Asistente Conversacional (En desarrollo):** Chat inteligente con router ReAct para resolver dudas salariales (RAG sobre sueldos en Perú), búsquedas web en tiempo real (Tavily) o asesoría general de carrera.

2. **Frente del Reclutador (Backlog):**
   - Búsqueda semántica de candidatos basada en descripciones de puesto.
   - Generación automática de feedbacks para postulantes no seleccionados.

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión / Detalle |
| :--- | :--- | :--- |
| **Backend REST API** | FastAPI + Uvicorn | FastAPI `0.121.0`, ASGI asíncrono |
| **Orquestación de Agentes** | LangGraph + LangChain | LangGraph `0.6.10`, LangChain `0.3.27` |
| **Modelos de Lenguaje** | OpenAI API | `gpt-4o-mini`, `text-embedding-3-small` |
| **Base de Datos Vectorial** | Pinecone | SDK `7.3.0`, Serverless (namespaces e índices dedicados) |
| **Búsqueda Híbrida** | BM25 (`pinecone-text`) | Sparse vectors + Dense vectors para RAG salarial |
| **Base de Datos Relacional** | PostgreSQL + SQLAlchemy | SQLAlchemy `2.0.44` (AsyncEngine + AsyncSession), asyncpg, pgvector |
| **Caché y Memoria Corto Plazo**| Redis | `redis-py` asíncrono para ventana de mensajes recientes |
| **Frontend** | Streamlit | Streamlit `1.50.0`, arquitectura multipágina (`st.switch_page`) |
| **Búsqueda Externa** | Tavily Search API | `tavily-python` para navegación web |
| **Contenerización** | Docker | `Dockerfile.api` (puerto 4050) y `Dockerfile.frontend` (puerto 4060) |

---

## 3. Estructura de Directorios

```text
proyect1/
├── assets/                  # Recursos gráficos y demostraciones (demo.gif)
├── backend/
│   ├── core/
│   │   ├── logging_config.py   # Configuración de RotatingFileHandler y consola
│   │   ├── request_logger.py   # Middleware Starlette para auditar requests/responses
│   │   └── security.py         # JWT tokens, hashing de passwords, dependencias auth
│   ├── cvs/                    # Almacenamiento local temporal de PDFs subidos
│   ├── database.py             # Configuración de SQLAlchemy con AsyncEngine y async_session
│   ├── graph/
│   │   ├── graph_builder.py    # Grafo LangGraph: Pipeline de CV Recomendador (Funcional)
│   │   └── react_graph_builder.py # Grafo LangGraph: Asistente ReAct Router (Incompleto/WIP)
│   ├── infra/
│   │   ├── cache/redis.py      # Conexión asíncrona a Redis
│   │   └── db/memory_lt.py     # Notas de persistencia de largo plazo
│   ├── knowledge/              # Datasets y artefactos serializados (BM25 fit, CSV sueldos)
│   ├── llms/openaillm.py       # Wrapper de instancias ChatOpenAI y OpenAIEmbeddings
│   ├── memory/short_term.py    # Gestión de historial conversacional en Redis
│   ├── nodes/
│   │   ├── cv_nodes.py         # Nodos del flujo de CV: carga, parseo LLM, embeddings, match
│   │   └── react_agent.py      # Nodos del agente ReAct: enrutador, LLM general, RAG sueldos
│   ├── routers/
│   │   ├── admin.py            # Endpoints administrativos (usuarios, listado)
│   │   └── agent.py            # Endpoints del agente (/cv-upload, /general-query)
│   ├── schemas.py              # Modelos ORM (User, Memory) y Pydantic (Auth, DTOs)
│   ├── state/
│   │   ├── state_graph.py      # State y Schemas Pydantic del flujo de CV (CVData, EmpleosData)
│   │   └── react_state_graph.py# State y Schemas del flujo ReAct
│   ├── tools/web_search.py     # Herramienta LangChain de Tavily Search
│   ├── utils/rag_utils.py      # Esqueleto pendiente para pipelines RAG avanzados
│   └── main.py                 # Entrada principal FastAPI, middlewares, routers y lifespan
├── ui/
│   ├── app.py                  # Entrada Streamlit (redirección a Login o Chat)
│   ├── pages/
│   │   ├── Login.py            # Página de autenticación (solicitud de token JWT)
│   │   └── Chat.py             # Página principal interactiva (subida de CV y chat)
│   ├── streamlitui/
│   │   ├── loadui.py           # Configuración visual de la barra lateral y controles
│   │   └── display_results.py  # Renderizado de resultados de recomendación
│   ├── uiconfigfile.ini        # Archivo INI de títulos y opciones de interfaz
│   ├── uiconfigfile.py         # Lector ConfigParser para uiconfigfile.ini
│   └── utils/logger.py         # Logger exclusivo de Streamlit
├── Dockerfile.api              # Contenedor para FastAPI
├── Dockerfile.frontend         # Contenedor para Streamlit
├── requirements.txt            # Dependencias fijadas del proyecto
└── README.md                   # Documentación pública del proyecto
```

---

## 4. Estado de Implementación de Funcionalidades

| Módulo / Funcionalidad | Estado Actual | Ubicación Principal |
| :--- | :--- | :--- |
| **Login y JWT Auth** | **100% Funcional** | `backend/core/security.py` |
| **Pipeline CV Recomendador** | **100% Funcional** | `backend/graph/graph_builder.py`, `backend/nodes/cv_nodes.py` |
| **Structured Output CV -> Empleos** | **100% Funcional** | `backend/state/state_graph.py` |
| **Persistencia Pinecone (CVs + Empleos)** | **100% Funcional** | `backend/nodes/cv_nodes.py` |
| **Frontend: Subida de CV & Matching** | **100% Funcional** | `ui/pages/Chat.py`, `ui/streamlitui/` |
| **RAG de Sueldos Perú** | **100% Funcional (Tool)** | `backend/tools/salary_tool.py` |
| **Agente Conversacional ReAct** | **100% Funcional** | `backend/graph/react_graph_builder.py` |
| **Búsqueda Web con Tavily** | **100% Funcional (Tool)** | `backend/tools/web_search.py` |
| **Memoria Conversacional** | **Funcional en State/Frontend** | `ui/pages/Chat.py`, `backend/routers/agent.py` |
| **Endpoint `/agent/general-query`** | **100% Funcional** | `backend/routers/agent.py` |
| **Recomendador de Candidatos para Reclutador** | **En Backlog** | Pendiente |
| **Generador de CV adaptado al puesto** | **En Backlog** | Pendiente |

---

## 5. Directrices Técnicas y Convenciones de Código

### 5.1. Asincronismo Obligatorio
- Todo endpoint de FastAPI y todo nodo de LangGraph que interactúe con I/O (Pinecone, OpenAI, Redis, PostgreSQL) **debe ser asíncrono (`async def`)**.
- Usar métodos asíncronos de LangChain / LangGraph: `.ainvoke(...)`, `.aembed_query(...)`.
- En SQLAlchemy, usar exclusivamente `await session.execute(...)` y `await session.commit()`. Evitar llamadas síncronas que bloqueen el event loop.

### 5.2. Manejo de Rutas y Dependencias de Sistema
- **No utilizar `sys.path.append(f"{str(PARENT_DIRECTORY)}/proyect1/backend")`**. Utilizar imports basados en el paquete raíz (`from backend.core...` o ejecutando con `PYTHONPATH=.`).
- En contenedores Docker, `PYTHONPATH=/usr/src/app` está configurado para resolver rutas desde el directorio de trabajo.
- Para leer archivos locales de conocimiento (`backend/knowledge/`), emplear `pathlib.Path(__file__).resolve().parent...` en lugar de rutas relativas fijas como `../knowledge/...`.

### 5.3. Pydantic y Tipado
- El proyecto usa **Pydantic v2**. Usar `model.model_dump()` en vez de `model.dict()`.
- En definiciones de `TypedDict` para estados de LangGraph, definir los tipos con dos puntos (`field: type`) y **nunca** con asignación (`field = type`).
- En `Literal`, separar los elementos por comas entre comillas: `Literal["rag", "web", "llm"]` y no `Literal["rag, web, llm"]`.

### 5.4. Logging Estructurado
- Utilizar `setup_backend_logger()` para obtener el logger estándar.
- Utilizar `logger.exception("Mensaje")` dentro de bloques `except Exception:` para registrar el stack trace completo.

---

## 6. Variables de Entorno Requeridas

Asegurar la existencia de un archivo `.env` en la raíz o en `backend/` con las siguientes claves:

```bash
# LLMs y Proveedores de IA
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
TAVILY_API_KEY=tvly-...

# Pinecone
PINECONE_API_KEY=...
HOST_BASECVS=https://basecvs-...pinecone.io
HOST_EMPLEOS=https://recursoshumanos-...pinecone.io

# Bases de Datos
URL_DATABASE=postgresql+asyncpg://usuario:password@localhost:5432/chambea_pe
HOST_REDIS=redis://localhost:6379/0

# Seguridad JWT
KEY=tu_clave_secreta_jwt_muy_segura
ALGORITHM=HS256

# Frontend Streamlit
API_URL=http://localhost:8000
```

---

## 7. Instrucciones para Ejecutar y Testear

### Ejecutar el Backend (FastAPI):
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Documentación interactiva disponible en: `http://localhost:8000/docs`.

### Ejecutar el Frontend (Streamlit):
```bash
cd ui
streamlit run app.py --server.port 8501
```

---

## 8. Registro de Deuda Técnica y Correcciones Prioritarias

Cualquier agente que trabaje en estabilizar o extender el código debe atender prioritariamente estos puntos:

1. **Vulnerabilidad en `backend/core/security.py` (Endpoint `/auth/token`):**
   - La validación de contraseña (`pwd_context.verify`) está comentada. Cualquier petición con un `username` existente genera un token JWT válido sin verificar credenciales. Se debe reactivar la verificación y lanzar `HTTPException(401)`.

2. **Error de Lógica en `backend/routers/admin.py` (`create_user`):**
   - El endpoint valida si quien realiza la petición es admin consultando `where(User.username == user_form.user)`. Debe consultar `user.get("user")` (el usuario autenticado en el token), de lo contrario fallará al crear usuarios nuevos.

3. **Incompletitud en `backend/routers/agent.py` (`general_query`):**
   - El endpoint `/agent/general-query` instancia `ReactAgent()` pero no ejecuta ningún método ni retorna respuesta. Debe recibir la query, invocar el grafo compilado del agente ReAct y devolver la respuesta estructurada.

4. **Sintaxis Incompleta en `backend/graph/react_graph_builder.py`:**
   - Líneas 22-23 contienen llamadas con parámetros vacíos: `self.graph.add_node("node_rag", )` y `self.graph.add_node("node_search_web", )`.
   - Faltan los edges hacia `END` desde `node_rag`, `node_search_web` y `node_llm`.

5. **Instanciación Rota en `backend/nodes/react_agent.py`:**
   - Se llama a `OpenAILLM.openai_model()`, el cual no es un método de clase estático y requiere un argumento no documentado `x`. Se debe instanciar `OpenAILLM().llm` como en `cv_nodes.py`.
   - En `main_query_analizer`, la firma recibe `(self, StateAgentReact, user)`. En LangGraph los nodos reciben únicamente `(state: StateAgentReact)`.
   - En `main_query_analizer`, falta el `await` en `chain.ainvoke(...)`.
   - En `llm_reponse` y `node_rag`, la llamada `self.short_memory.save_message(...)` es asíncrona y no tiene `await`.

6. **Tipado Erróneo en `backend/state/react_state_graph.py`:**
   - Corregir `StateAgentReact` para usar dos puntos (`:`) en lugar de (`=`).
   - Corregir `RouterQuery` para usar `Literal["rag", "web", "llm"]`.

7. **Error Tipográfico en `backend/infra/cache/redis.py`:**
   - Parámetro con typo: `decode_reponses=True` -> cambiar a `decode_responses=True`.

8. **Rutas Frágiles de Carga:**
   - En `backend/nodes/react_agent.py`: `joblib.load('../knowledge/bm25_fit.pkl')` falla dependiendo del directorio de ejecución. Usar rutas absolutas basadas en `Path(__file__)`.

9. **Conexión de Chat en Frontend (`ui/pages/Chat.py`):**
   - El widget `st.chat_input("Escriba su mensaje")` captura la entrada pero no la envía a ningún endpoint. Debe conectarse con `/agent/general-query` y renderizar el historial con `st.chat_message`.

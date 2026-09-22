# Workflow Inteligente con LangGraph

> El sistema utiliza LangGraph para orquestar un flujo inteligente para evaluación automática de CVs, matching semántico de candidatos y asistencia al proceso de reclutamiento utilizando RAG y búsqueda vectorial.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![LanGraph](https://img.shields.io/badge/LangGraph-0.6.10-orange)
![LangChain](https://img.shields.io/badge/LangChain-0.3.27-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-2.3.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121.0-green?logo=fastapi)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12-blue)
![Pinecone](https://img.shields.io/badge/Pinecone-7.3-green?logo=scikitlearn)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50.0-purple)

## Tabla de Contenidos
- [Problema de Negocio](#problema-de-negocio)
- [Solución Propuesta](#solución-propuesta)
- [Demo en Producción](#demo-en-producción)
- [Funcionalidades Principales](#funcionalidades-principales)
- [Arquitectura del Sitema](#arquitectura-del-sistema)
- [Flujo End-to-End](#flujo-end-to-end)
- [Pipeline RAG](#pipeline-rag)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Endpoints de la API](#endpoints-de-la-api)
- [Arquitectura de Despliegue](#arquitectura-de-despliegue)
- [Próximas Mejoras](#próximas-mejoras)

## Problema de Negocio

Para los candidatos les es muy difícil encontrar un match ideal a su perfil, es decir, adecuado a sus años de experiencia, funciones y habilidades técnicas. Es por ello que en la actualidad existen plataformas con varios filtros como palabras clave, años de experiencia, rango salarial, etc, los cuales reducen las opciones a unos cientos dependiendo del perfil a postular. Ahora el trabajo del postulante está en ingresar a cada una de esas decenas o cientos de empleos a revisar si calza su perfil adecuadamente y suele ser un proceso cansado y frustante sino encuentras algo adecuado a ti.

Para los reclutadores, los cuales no solo gestionan un proceso de reclutamiento sino varios a la vez, su indicador de idoniedad se basa por un lado en las ATS o la revisión rápida manual que hacen al CV del candidato, pero allí pierden oportunidad de crossear al candidato, el cual podría calificar para otro puesto que el reclutador también esté gestionando.

## Solución Propuesta

En vista de la realidad en ambos frente, este proyecto tiene por objetivo ser una plataforma centrada de búsqueda de empleo inteligente por el lado del candidato y a la vez una plataforma del talento humano por el lado de los reclutadores, utilizando el RAG como pilar en la optimización de esta problemática.

#### Por el frente del Candidato:
Reducir las horas de búsqueda de empleo a minutos, de la siguiente forma:
- Lista de empleos disponibles priorizados por Match al puesto.
- Feedback de mejoras o gaps que tiene el candidato frente a cada empleo disponible.
- Creación de CV optimizado para cada puesto.

#### Por el frente del Reclutador:
Reducir las horas de búsqueda del candidato ideal, de la siguiente forma:
- Lista de candidatos priorizados por Match al puesto gestionado.
- Recomendación de candidatos para otros puestos gestionados por el reclutador.
- Resumen de habilidades que el candidato no cumple para la idoniedad del puesto.
- Creación de feedback automático para el candidato para los que no sean elegidos.

## Demo en Producción

> [!NOTE]
> La plataforma cuenta con dos módulos principales 100% operativos:
> 1. **Evaluación y Matching de CV (Barra Lateral):** Ingesta de CV en PDF, extracción estructurada con LLM, generación de embeddings y búsqueda semántica en Pinecone contra ofertas laborales disponibles.
> 2. **Asistente Laboral Conversacional ReAct (Cuerpo Principal):** Chat interactivo multi-turno capaz de consultar bases de datos de salarios en Perú (RAG híbrido BM25 + Pinecone) y navegar en internet en tiempo real (Tavily) para resolver dudas de empleo, mercado y carrera.

![DEMO](assets/demo.gif)

## Funcionalidades Principales

| Funcionalidad | Descripción | Estado |
|---------------|-------------|--------|
| Recomendación Empleos | El usuario ingresa su CV y obtendrá como respuesta el top 5 empleos que hagan mayor match. | Implementado |
| Feedback de mejoras y gaps | El usuario además de recibir los top 5 empleos que hagan mayor match, recibe un feedback por cada uno enfocado en los gaps que le faltan para ser más idóneo al puesto | Implementado |
| Responder sobre salarios | La LLM usa como contexto una base vectorial con datos de salarios en distintos perfiles tech y administrativos en Perú. Devuelve rangos salariales y las empresas que los pagan | Implementado |
| Responder sobre cosas nuevas | La LLM usa tools de búsqueda web para responder a preguntas que no se encuentran en su base de entrenamiento o sean eventos futuros para evitar la alucinación. | Implementado |
| Recomendación Candidatos | El reclutador ingresa una palabra clave o descripción del perfil buscado y obtendrá como respuesta el top 5 candidadtos que hagan mayor match. | En Backlog |
| Creación de CV por cada puesto | El usuario tendrá la opción de generar un CV optimizado para el puesto que esté interesado antes de enviar su postulación | En Backlog |

## Arquitectura del Sistema

### Vista Funcional

**Vista candidato**
```mermaid
flowchart LR

A[Ingreso a la plataforma]
S[Login con sus datos]
F[Subida del CV]
P[Retorno de Top 5 Empleos]

A --> S
S --> F
F --> P

```

### Vista Técnica

```mermaid
flowchart TD

    USUARIO[Usuario]
    STREAMLIT[Streamlit Frontend]
    FASTAPI[FastAPI Backend]
    LANGRAPH[LangGraph]
    POSTGRESSQL[(PostgresSQL)]
    REDIS[(Redis)]
    OPENAI[OpenAI]

    USUARIO --> STREAMLIT
    STREAMLIT --> FASTAPI
    FASTAPI --> LANGGRAPH
    FASTAPI --> POSTGRESSQL
    POSTGRESSQL --> REDIS

    subgraph CV Recomendador

        PDF[CV PDF]
        EXTRACCION[CV Extracción]
        ESTRUCTURA[Estructuración CV]
        EMBEDDING[Generación del Embedding]
        PINECONE[Pinecone]
        MATCH[Match de Empleos]

        PDF --> EXTRACCION
        EXTRACCION --> ESTRUCTURA
        ESTRUCTURA --> EMBEDDING
        EMBEDDING --> PINECONE
        PINECONE --> MATCH
    
    end

    subgraph Asistente Conversacional

        ROUTER[Agente Router]
        WEB[Búsqueda Web]
        RAG[RAG Sueldos]
        LLM[LLM Generalista]

        ROUTER --> WEB
        ROUTER --> RAG
        ROUTER --> LLM
    
    end

    MATCH --> OPENAI
    RAG --> PINECONE
    LLM --> OPENAI

```

## Flujo End-to-End

#### CV Recomendador
```mermaid
flowchart TD

INGRESOCV[Usuario ingresa CV]
CARGAR[Cargar Documento PDF]
TRANSFORMAR[Transformación CV]
EMBEDDING[Embedding del CV]
PINECONE[Guardar en Pinecone]
BUSQUEDA[Búsqueda semántica]
TRANSFORMACION2[Transformación respuesta]
RESPUESTA[Respuesta al usuario]

INGRESO --> CARGAR
CARGAR --> TRANSFORMAR
TRANSFORMAR --> EMBEDDING
EMBEDDING --> PINECONE
EMBEDDING --> BUSQUEDA
BUSQUEDA --> TRANSFORMACION2
TRANSFORMACION2 --> REPUESTA

```

#### Asistente Conversacional ReAct (LangGraph)
```mermaid
flowchart TD

    USUARIO[Usuario ingresa consulta en Chat]
    AGENT[Agente ReAct - ChatOpenAI bind_tools]
    DECISION{tools_condition}
    TOOL_SALARY[Tool: consultar_sueldos_peru<br>BM25 + Pinecone Híbrido]
    TOOL_WEB[Tool: search_tavily<br>Búsqueda Web en Tiempo Real]
    TOOLNODE[ToolNode Execution]
    RESPUESTA[Respuesta Final con Badges de Fuentes]

    USUARIO --> AGENT
    AGENT --> DECISION
    DECISION -- Salarios o Tarifas Perú --> TOOL_SALARY
    DECISION -- Consultas Web / Empresas / Noticias --> TOOL_WEB
    DECISION -- Charla General / Consejos CV --> RESPUESTA

    TOOL_SALARY --> TOOLNODE
    TOOL_WEB --> TOOLNODE
    TOOLNODE --> AGENT
```

## Pipeline RAG

#### RAG Sueldos

```mermaid
flowchart TD

PREGUNTA[Pregunta Usuario]
OPENAI[OpenAI Embedding - Dense vector]
BM25[BM25 - Sparse vector]
PINECONE[Pinecone Búsqueda Híbrida]
TOP[Top K documentos]
PROMPT[Prompt con contexto]
OPENAIGPT[OpenAI GPT]
RESPUESTA[Respuesta Final]

PREGUNTA --> OPENAI
PREGUNTA --> BM25
OPENAI --> PINECONE
BM25 --> PINECONE
PINECONE --> TOP
TOP --> PROMPT
PROMPT --> OPENAIGPT
OPENAIGPT --> RESPUESTA

```

#### RAG CV Match

```mermaid
flowchart TD

CV[CV del usuario]
OPENAI[OpenAI Embedding]
PINECONE[Pinecone Búsqueda Semántica]
TOP[Top K documents]
PROMPT[Prompt con Contexto]
OPENAIGPT[OpenAI GPT]
RESPUESTA[Respuesta Final]

CV --> OPENAI
OPENAI --> PINECONE
PINECONE --> TOP
TOP --> PROMPT
PROMPT --> OPENAIGPT
OPENAIGPT --> RESPUESTA

```

## Stack Tecnológico

| Librería | Descripción |
|----------|---------|
| FastAPI | REST API Framework |
| Uvicorn | Servidor ASGI |
| Streamlit | Front interactivo |
| LangGraph | Orquestador |
| LangChain | LCEL + PromptTemplate |
| OpenAI | Generador de embeddings y LLM |
| Pinecone | Base vectorial y búsqueda híbrida o semántica |
| Docker | Creación de imágenes |
| PostgresSQL | Validación y creación de usuario |

## Estructura del Repositorio

```text
proyect1/
├── assets/
│   └── demo.gif
├── backend/
│   ├── core/
│   │   ├── logging_config.py      # Configuración de logs rotativos y consola
│   │   ├── request_logger.py      # Middleware para auditoría HTTP
│   │   └── security.py            # Autenticación JWT y hash bcrypt
│   ├── cvs/                       # Directorio local temporal de PDFs
│   ├── database.py                # Conexión SQLAlchemy async con asyncpg
│   ├── graph/
│   │   ├── graph_builder.py       # Grafo LangGraph: Pipeline CV Recomendador
│   │   └── react_graph_builder.py # Grafo LangGraph: Asistente ReAct con ToolNode
│   ├── infra/
│   │   ├── cache/redis.py         # Cliente Redis asíncrono
│   │   └── db/memory_lt.py        # Persistencia de memoria a largo plazo
│   ├── knowledge/
│   │   ├── bm25_fit.pkl           # Modelo BM25 serializado para salarios
│   │   ├── dense_vectors.pkl      # Embeddings densos de salarios
│   │   ├── Sueldos_peru_incompleto_csv.csv
│   │   └── sueldos_peru.pkl
│   ├── llms/
│   │   └── openaillm.py           # Wrapper ChatOpenAI y OpenAIEmbeddings
│   ├── memory/
│   │   └── short_term.py          # Manejo de memoria conversacional
│   ├── nodes/
│   │   └── cv_nodes.py            # Nodos de extracción, parsing y match de CV
│   ├── routers/
│   │   ├── admin.py               # Endpoints administrativos (/admin/all, /admin/create)
│   │   └── agent.py               # Endpoints (/cv-upload, /general-query)
│   ├── schemas.py                 # Modelos ORM y esquemas Pydantic v2
│   ├── state/
│   │   ├── react_state_graph.py   # State del agente ReAct (add_messages)
│   │   └── state_graph.py         # State del pipeline de CV
│   ├── test/
│   │   ├── test_e2e_react_pipeline.py     # Pruebas E2E de routing ReAct
│   │   ├── test_general_query_endpoint.py # Pruebas del endpoint /agent/general-query
│   │   ├── test_react_graph.py            # Pruebas de compilación del grafo
│   │   ├── test_security_patch.py         # Pruebas de validación de contraseñas
│   │   ├── test_state_dto.py              # Validación de esquemas y DTOs
│   │   └── test_tools.py                  # Pruebas de tools (BM25, Pinecone, Tavily)
│   ├── tools/
│   │   ├── salary_tool.py         # Tool RAG híbrido de salarios (BM25 + Pinecone)
│   │   └── web_search.py          # Tool de búsqueda web con Tavily
│   ├── utils/
│   │   └── rag_utils.py
│   └── main.py                    # Punto de entrada FastAPI, CORS y lifespan
├── ui/
│   ├── app.py                     # Entrada Streamlit (redirección login/chat)
│   ├── pages/
│   │   ├── Chat.py                # Interfaz principal (subida de CV + Chat ReAct)
│   │   └── Login.py               # Identificación de usuario y obtención de JWT
│   ├── streamlitui/
│   │   ├── display_results.py     # Componente visual para resultados de CV
│   │   └── loadui.py              # Barra lateral y configuración de controles
│   ├── uiconfigfile.ini           # Configuración de títulos y selectores
│   ├── uiconfigfile.py            # Lector de uiconfigfile.ini
│   └── utils/
│       └── logger.py              # Logger de Streamlit
├── .dockerignore
├── Dockerfile.api                 # Contenedor Backend FastAPI (Puerto 4050)
├── Dockerfile.frontend            # Contenedor Frontend Streamlit (Puerto 4060)
├── requirements.txt
└── README.md
```

## Endpoints de la API

| Método | Path | Auth Requerida | Descripción |
|---|---|---|---|
| `POST` | `/auth/token` | Pública | Login con `{"username": "...", "password": "..."}`. Retorna token JWT Bearer. |
| `POST` | `/admin/create` | Bearer (Admin) | Creación de nuevos usuarios con rol (`admin` / `user`) y contraseña hasheada con bcrypt. |
| `GET` | `/admin/all` | Bearer (Admin) | Listado de todos los usuarios registrados en PostgreSQL. |
| `POST` | `/agent/cv-upload` | Bearer | Ingesta de CV en PDF (`multipart/form-data`). Retorna resumen y top de empleos recomendados. |
| `POST` | `/agent/general-query` | Bearer | Consulta conversacional con historial (`{"query": "...", "history": [...]}`). Retorna respuesta y `tools_used`. |

## Despliegue con Docker y Docker Hub

Las imágenes oficiales están compiladas para arquitectura **`linux/amd64`** (compatibles con servidores VPS en Contabo, Hetzner, DigitalOcean o AWS con Easypanel):

| Componente | Repositorio Docker Hub | Tags | Puerto Contenedor |
|---|---|---|---|
| **Backend API** | `davidrodriguez2712/proyecto-2-cv-recomendador-api` | `1.0.0`, `latest` | `4050` |
| **Frontend UI** | `davidrodriguez2712/proyecto-2-cv-recomendador-frontend` | `1.0.0`, `latest` | `4060` |

### Comandos de Despliegue en VPS:

```bash
# 1. Descargar las imágenes actualizadas
docker pull davidrodriguez2712/proyecto-2-cv-recomendador-api:latest
docker pull davidrodriguez2712/proyecto-2-cv-recomendador-frontend:latest

# 2. Ejecutar el Backend (FastAPI)
docker run -d \
  --name cv-recomendador-api \
  --restart unless-stopped \
  -p 4050:4050 \
  --env-file .env \
  davidrodriguez2712/proyecto-2-cv-recomendador-api:latest

# 3. Ejecutar el Frontend (Streamlit)
docker run -d \
  --name cv-recomendador-frontend \
  --restart unless-stopped \
  -p 4060:4060 \
  -e API_URL="http://TU_DOMINIO_O_IP:4050" \
  davidrodriguez2712/proyecto-2-cv-recomendador-frontend:latest
```

## Variables de Entorno

Configurar en el archivo `.env` o en el panel de variables de entorno de tu VPS (Easypanel):

| Variable | Obligatoria | Descripción / Formato |
|---|:---:|---|
| `OPENAI_API_KEY` | ✅ | Clave de OpenAI (`sk-...`) con saldo prepagado activo para modelos (`gpt-4o-mini`) y embeddings (`text-embedding-3-small`). |
| `TAVILY_API_KEY` | ✅ | Clave de Tavily Search API para navegación web en tiempo real. |
| `PINECONE_API_KEY` | ✅ | Clave de API de Pinecone para índices vectoriales. |
| `HOST_BASECVS` | ✅ | URL del índice de CVs en Pinecone (ej. `https://basecvs-...pinecone.io`). |
| `HOST_EMPLEOS` | ✅ | URL del índice de empleos en Pinecone (ej. `https://recursoshumanos-...pinecone.io`). |
| `URL_DATABASE` | ✅ | Cadena de conexión PostgreSQL async (`postgresql+asyncpg://user:pass@host:port/dbname`). |
| `HOST_REDIS` | ❌ | URL de conexión a Redis (`redis://...`) para memoria de corto plazo. |
| `KEY` | ✅ | Clave secreta para firmar tokens JWT. |
| `ALGORITHM` | ✅ | Algoritmo de firma JWT (ej. `HS256`). |
| `API_URL` | ✅ *(Frontend)* | URL base del backend al que apunta Streamlit (ej. `http://localhost:8000` o `http://api:4050`). |
| `LANGCHAIN_TRACING_V2` | ❌ | Trazabilidad en LangSmith (`false` para desactivar advertencias si no se usa). |

> [!TIP]
> **Codificación en `URL_DATABASE`:**
> Si la contraseña de tu base de datos contiene caracteres especiales como `#` o `$`, debes ingresarlos codificados en formato URL percent-encoding (ej. `#` como `%23` y `$` como `%24`) para evitar que parsers de entornos de contenedores (Easypanel, Docker) truncen la cadena al interpretar el `#` como comentario.

## Pruebas Automatizadas

El proyecto cuenta con una suite integral de 14 pruebas unitarias y de integración en `backend/test/`:

```bash
# Ejecución de la suite completa con cobertura:
PYTHONPATH=.:backend pytest backend/test/ -v
```

Casos cubiertos:
- Resolución de consultas generales con el agente ReAct.
- Invocación de herramienta de salarios en Perú (`consultar_sueldos_peru`).
- Invocación de búsqueda web externa (`search_tavily`).
- Validación criptográfica de contraseñas bcrypt y autenticación JWT.
- Validación de DTOs y esquemas de entrada/salida de la API.
- Resiliencia de tools ante entradas vacías o fuera de rango.

## Próximas Mejoras (Backlog)

- [ ] Recomendador de candidatos para reclutadores (búsqueda semántica inversa puesto -> candidatos).
- [ ] Generación automática de CV adaptado al puesto deseado con IA.
- [ ] Persistencia de memoria conversacional a largo plazo en PostgreSQL (`pgvector`).

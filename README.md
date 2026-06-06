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
> Por ahora solo se ha terminado con la funcionalidad de Recomendación de Empleos a través del CV del candidato (barra lateral izquierda), se está trabajando en la implementación de las siguientes funcionalidades.

![DEMO](assets/demo.gif)

## Funcionalidades Principales

| Funcionalidad | Descripción | Estado |
|---------------|-------------|--------|
| Recomendación Empleos | El usuario ingresa su CV y obtendrá como respuesta el top 5 empleos que hagan mayor match. | Implementado |
| Feedback de mejoras y gaps | El usuario además de recibir los top 5 empleos que hagan mayor match, recibe un feedback por cada uno enfocado en los gaps que le faltan para ser más idóneo al puesto | Implementado |
| Responder sobre salarios | La LLM usa como contexto una base vectorial con datos de salarios en distintos perfiles tech y administrativos en Perú. Devuelve rangos salariales y las empresas que los pagan | En Proceso |
| Responder sobre cosas nuevas | La LLM usa tools de búsqueda web para responder a preguntas que no se encuentran en su base de entrenamiento o sean eventos futuros para evitar la alucinación. | En Proceso |
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

#### Asistente Conversacional
```mermaid
flowchart TD

USUARIO[Usuario ingresa consulta por chat]
ROUTER[Router decide intención]
GENERALISTA[LLM General]
RAG[RAG Sueldos]
WEB[Búsqueda Web]
RESPUESTA[Respuesta al usuario]

USUARIO --> ROUTER
ROUTER --> GENERALISTA
ROUTER --> RAG
ROUTER --> WEB
GENERALISTA --> REPUESTA
RAG --> RESPUESTA
WEB --> RESPUESTA

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

Proyecto
├── assets
│   └── demo.gif
├── backend
│   ├── core
│   │   ├── logging_config.py
│   │   ├── request_logger.py
│   │   └── security.py
│   ├── cvs
│   │   └── 20260604_221451_admin.pdf
│   ├── database.py
│   ├── graph
│   │   ├── graph_builder.py
│   │   └── react_graph_builder.py
│   ├── infra
│   │   ├── cache
│   │   └── db
│   ├── knowledge
│   │   ├── bm25_fit.pkl
│   │   ├── dense_vectors.pkl
│   │   ├── Sueldos_peru_incompleto_csv.csv
│   │   └── sueldos_peru.pkl
│   ├── llms
│   │   └── openaillm.py
│   ├── main.py
│   ├── memory
│   │   └── short_term.py
│   ├── nodes
│   │   ├── bm25_params.json
│   │   ├── cv_nodes.py
│   │   └── react_agent.py
│   ├── routers
│   │   ├── admin.py
│   │   └── agent.py
│   ├── schemas.py
│   ├── state
│   │   ├── react_state_graph.py
│   │   └── state_graph.py
│   ├── tools
│   │   └── web_search.py
│   └── utils
│       └── rag_utils.py
├── Dockerfile.api
├── Dockerfile.frontend
├── requirements.txt
└── ui
    ├── app.py
    ├── pages
    │   ├── Chat.py
    │   └── Login.py
    ├── streamlitui
    │   ├── display_results.py
    │   └── loadui.py
    ├── uiconfigfile.ini
    ├── uiconfigfile.py
    └── utils
        └── logger.py

```

## Endpoints de la API

| Método | Path | Descripción |
|--------|------|-------------|
| `POST` | `/auth/token` | Login para ingreso a la plataforma |
| `POST` | `/admin/create`| Creación de la cuenta del usuario en postgresql |
| `POST` | `/agent/cv-upload`| Inicia pipeline CV recomendador |
| `POST` | `/agent/general-query` | Inicia pipeline Asistente Conversacional | 

## Arquitectura de Despliegue

```mermaid
flowchart TD

    USUARIO[Usuario]
    EASYPANEL[EasyPanel VPS Contabo]
    FASTAPI[FastAPI Container]
    FRONTEND[Streamlit Container]
    POSTGRESSQL[(PostgreSQL Container)]
    OPENAI[OpenAI API]
    PINECONE[Pinecone Cloud]

    USUARIO --> STREAMLIT
    STREAMLIT --> FASTAPI
    FASTAPI --> POSTGRESSQL
    FASTAPI --> OPENAI
    FASTAPI --> PINECONE

    subgraph Contabo VPS
        FASTAPI
        FRONTEND
        POSTGRESSQL
    end

```

## Variables de Entorno

| Variable | Obligatoria | Descripción |
|-----------|------------|-------------|
| `GOOGLE_API_KEY` | ✅ | Clave de acceso a los modelos de Google Gemini. |
| `OPENAI_API_KEY` | ✅ | Clave de acceso a los modelos y embeddings de OpenAI. |
| `PINECONE_API_KEY` | ✅ | Clave de acceso a Pinecone para almacenamiento y búsqueda vectorial. |
| `TAVILY_API_KEY` | ✅ | Clave de acceso a Tavily para búsquedas web en tiempo real. |
| `LANGCHAIN_API_KEY` | ❌ | Clave de LangSmith para monitoreo, trazabilidad y observabilidad de agentes. |
| `LANGCHAIN_PROJECT` | ❌ | Nombre del proyecto registrado en LangSmith. |
| `LANGCHAIN_TRACING_V2` | ❌ | Habilita el trazado de ejecuciones en LangSmith (`true` / `false`). |
| `HF_TOKEN` | ❌ | Token de acceso a Hugging Face para descargar modelos o recursos privados. |
| `GROQ_API_KEY` | ❌ | Clave de acceso a los modelos servidos por Groq. |


## Próximas Mejoras

- Responder sobre salarios
- Responder sobre cosas nuevas
- Recomendación candidatos

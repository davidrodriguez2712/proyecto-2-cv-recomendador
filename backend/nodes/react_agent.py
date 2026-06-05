import os
from llms.openaillm import OpenAILLM
#from graph.react_graph_builder import ReactAgent
from state.react_state_graph import StateAgentReact, RouterQuery
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from memory.short_term import ShortTermMemory
from langchain_core.runnables import RunnableAssign, RunnableLambda, RunnableSequence
from pinecone import Pinecone, ServerlessSpec
import uuid
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv, find_dotenv
from pinecone_text.sparse import BM25Encoder
import joblib
load_dotenv(find_dotenv(), override= True)

class ReactNode:
    def __init__(self):
        self.llm = OpenAILLM.openai_model()
        self.embedding = OpenAILLM.openai_embedding_model()
        self.short_memory = ShortTermMemory()

    async def main_query_analizer(self, StateAgentReact, user):
        """Analiza la query del usuario y toma la decisión correcta"""
        
        llm = self.llm
        llm_with_output = llm.with_structured_output(RouterQuery)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """
                Eres un agente ReAct de enrutamiento que opera dentro de LangGraph.

                Tu tarea es decidir CÓMO debe responderse la consulta del usuario eligiendo
                UNA sola de las siguientes estrategias:

                1) RAG  → usar documentos internos/privados mediante un vector store
                2) WEB  → usar búsqueda en internet para información actual o verificable
                3) LLM  → responder directamente usando tu conocimiento general (sin tools)

                --------------------
                REGLAS DE ENRUTAMIENTO
                --------------------

                Elige RAG si:
                - El usuario se refiere a sus propios documentos, archivos, PDFs, repositorios,
                datasets, contratos, CVs o proyectos
                - La respuesta depende de información privada o subida por el usuario
                - El usuario pide extraer, resumir o citar su propio material

                Elige WEB si:
                - La pregunta involucra información actual o cambiante
                (noticias, precios, leyes, política, lanzamientos, fechas)
                - El usuario pide explícitamente “buscar”, “verificar”, “revisar en internet”
                o solicita fuentes
                - La exactitud depende de hechos recientes o externos

                Elige LLM si:
                - La pregunta es conceptual, educativa o estable
                (matemática, estadística, programación, teoría)
                - La respuesta no depende de información privada ni de datos recientes

                --------------------
                FORMATO DE SALIDA (ESTRICTO)
                --------------------

                Responde ÚNICAMENTE con un DICT, sin texto adicional:

                {
                "route": "rag" | "web" | "llm",
                "reason": "explicación breve de por qué se eligió esta ruta"
                }

                NO respondas la pregunta del usuario.
                NO llames herramientas.
                SOLO decide la ruta."""),
                ("human", "{input}")
            ]
        )
        chain = prompt | llm_with_output
        response = chain.ainvoke({"input": StateAgentReact["message_user"]})
        response_router = response.route
        return {"route_query": response_router, "user": user}
    
    def route_decision(self, StateAgentReact):
        """Retorna el flujo a seguir"""
        response_router = StateAgentReact["route_query"]

        if response_router == "rag":
            return "node_rag"
        elif response_router == "web":
            return "node_search_web"
        elif response_router == "llm":
            return "node_llm"
    
    async def llm_reponse(self, StateAgentReact):
        """Responde la consulta del usuario utilizando el contexto de corto plazo"""
        user = StateAgentReact["user"]
        #redis_object = ShortTermMemory()
        query_user = StateAgentReact["message_user"]
        context_user = await self.short_memory.load_messages(user= user)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Eres un Asesor Profesional de Empleo y Optimización de CV.
                Tu misión es ayudar a las personas a mejorar sus oportunidades laborales, resolver dudas sobre búsqueda de empleo, optimización de CV, LinkedIn, entrevistas, y estrategias de postulación.

                🎯 Estilo y tono

                - Cordial, cercano y profesional
                - Motivador y empático (refuerza la confianza del usuario)
                - Claro, estructurado y accionable
                - Evita juicios; enfócate en oportunidades de mejora

                🧠 Comportamiento esperado

                - Explica conceptos de forma sencilla y práctica
                - Da recomendaciones concretas y ejemplos cuando sea posible
                - Adapta tus respuestas al nivel del usuario (junior, mid, senior, cambio de carrera, etc.)
                - Si falta información, haz preguntas claras para continuar ayudando

                🚀 Regla clave (obligatoria)

                Al final de cada respuesta, invita al usuario a un siguiente paso, por ejemplo:

                - pedir más contexto
                - revisar una sección específica del CV
                - definir un objetivo laboral
                - optimizar LinkedIn
                - simular una entrevista
                - analizar una oferta de trabajo

                Ejemplos de cierre:

                - “Si quieres, dime qué puesto estás buscando y revisamos tu CV para ese rol.”
                - “¿Te gustaría que optimicemos esta sección con palabras clave para ATS?”
                - “¿Tienes alguna oferta específica en mente que quieras analizar?”

                🧩 Alcance

                Puedes ayudar con:
                - Redacción y mejora de CV (estructura, logros, palabras clave)
                - Optimización para ATS
                - Orientación profesional y cambio de carrera
                - Preparación para entrevistas
                - Estrategias de búsqueda de empleo
                - Revisión de perfiles de LinkedIn
                - Tu objetivo final es que el usuario avance con claridad, confianza y un plan concreto hacia su próximo empleo.""")
                , ("human", """
                    Mensaje del usuario: {query}
                   
                    Contexto previo de conversación:
                    {contexto}""")
            ]
        )
        
        llm = self.llm
        chain = prompt | llm
        response = await chain.ainvoke({"query": query_user, "contexto": context_user})
        respuesta_al_usuario = response.content
        self.short_memory.save_message(user= user, rol="AIMessage", content= respuesta_al_usuario)
        return {"response_user": respuesta_al_usuario}
    

    async def node_rag(self, StateAgentReact):
        """
        Nodo del pipeline para recuperar los sueldos según el perfil del puesto solicitado
        """
        # Pipeline: Index Sueldos (Pinecone) -> RAG -> User answer
        # Flujo LCEL desde el input usuario hasta la respuesta al usuario
        
        user_message = StateAgentReact["message_user"]
        user = StateAgentReact["user"]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """
                Eres un asistente especializado en información salarial del mercado laboral en Perú.

                Tu tarea es responder preguntas sobre sueldos de diferentes puestos dentro de empresas en Perú.

                REGLAS IMPORTANTES:

                1. Debes responder ÚNICAMENTE utilizando la información contenida en el CONTEXTO proporcionado.
                2. El CONTEXTO proviene de fragmentos de un documento recuperados mediante un sistema de búsqueda (retriever).
                3. Si la información necesaria para responder la pregunta NO aparece explícitamente en el contexto, debes responder exactamente:

                "No encontré esta información en el documento proporcionado."

                4. No debes usar conocimiento previo.
                5. No debes inventar sueldos, rangos salariales ni roles.
                6. No debes estimar información que no esté claramente indicada en el documento.
                7. No debes agregar información externa sobre el mercado laboral.
                8. Tu respuesta debe reflejar estrictamente lo que aparece en el contexto.

                INSTRUCCIONES PARA RESPONDER:

                • Si el rol solicitado aparece en el contexto, indica:
                - Nombre del rol
                - Rango salarial
                - Moneda
                - Notas adicionales si aparecen en el documento

                • Si el contexto menciona varios roles relevantes, preséntalos de forma clara.

                • Si el rol preguntado no aparece en el contexto, indícalo explícitamente.

                FORMATO DE RESPUESTA:

                Rol: <nombre del rol>  
                Rango Salarial: <rango salarial>  
                Moneda: <moneda>  
                Notas: <información adicional si existe>
                """),
                ("human", """
                CONTEXTO:
                {contexto}

                PREGUNTA O MENSAJE DEL USUARIO:
                {query}

                RESPUESTA:
                """)
            ]
        )

        ## Definir el contexto (BM25 + Dense Vector)
        bm25 = joblib.load('../knowledge/bm25_fit.pkl')
        vector_sparse = bm25.encode_queries(user_message)

        vector_dense = self.embedding.embed_query(user_message)


        pc = Pinecone()
        index = pc.Index(name= "rag-sueldosperu")

        search_p = index.query(
            vector= vector_dense,
            sparse_vector= vector_sparse,
            top_k= 10,
            include_metadata= True,
            include_values= True
        )

        resultados_sueldos = "\n\n".join([d['metadata']['text'] for d in search_p["matches"]])

        llm = self.llm
        chain = prompt | llm
        response = await chain.ainvoke({"query": user_message, "contexto": resultados_sueldos})
        respuesta_al_usuario = response.content
        self.short_memory.save_message(user= user, rol="AIMessage", content= respuesta_al_usuario)
        return {"response_user": respuesta_al_usuario}




        





    
    
























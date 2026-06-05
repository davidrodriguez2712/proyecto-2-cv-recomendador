from llms.openaillm import OpenAILLM
from state.state_graph import State, CVData, EmpleosData, ListaEmpleosData
import os
import logging
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone, ServerlessSpec
import uuid
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import json

logger = logging.getLogger("Proyecto1.cv_nodes")

class CVNodes:
    def __init__(self):
        self.llm = OpenAILLM().llm
        self.llm_embedding = OpenAILLM().embedding_llm
        #self.documento_cv = documento_cv

    def cargar_documentos_pdf(self, state: State):
        """
        Proceso para cargar el CV del usuario en PDF a la carpeta correspondiente.
        """
        archivo_subido = state["cv_object"]
        ruta_abs_archivo = os.path.abspath(__file__)
        ruta_carpeta_archivo = os.path.dirname(ruta_abs_archivo)
        ruta_carpeta_proyecto = os.path.dirname(ruta_carpeta_archivo)
        ruta_carpeta_cvs = os.path.join(ruta_carpeta_proyecto, "cvs")
        # modificación del nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_final = f"{timestamp}_{archivo_subido.get("username")}.pdf"
        ruta_pdf = os.path.join(ruta_carpeta_proyecto,"cvs", nombre_final)

        if os.path.exists(ruta_carpeta_cvs):
            logger.debug(f"La ruta ya existe: {ruta_carpeta_cvs}")
        os.makedirs(ruta_carpeta_cvs, exist_ok= True)

        with open(ruta_pdf, 'wb') as file:
            file.write(archivo_subido.get("content"))
        logger.info(f"Archivo guardado correctamente {ruta_pdf}")
        return {"cv_file_pdf": ruta_pdf}
    
    # def transformacion_cv(self, state: State): # método sync
    async def transformacion_cv(self, state: State):
        """
        Se encarga de transformar el CV antes de insertarlo en la base vectorial
        """
        cv_guardado_ruta = state["cv_file_pdf"]
        logger.debug(f"Se capturó la ruta del CV guardado aqui: {cv_guardado_ruta}")
        loader = PyPDFLoader(cv_guardado_ruta)
        document = loader.load()
        document_concatenado = "\n".join([d.page_content for d in document])

        logger.debug(f"El CV concatenado tiene una longitud de {len(document_concatenado)} caracteres")
        model = self.llm
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """
                Objetivo:
                Extrae toda la información disponible de un CV o perfil profesional en español y devuélvela como un objeto que siga exactamente la estructura del modelo CVData. 
                Usa todos los campos disponibles y asigna valores precisos; si algún dato no existe, deja el campo vacío o como None. 
                Respeta los tipos de datos: listas, submodelos y valores opcionales.

                Instrucciones Generales:
                - Todo debe estar en español.
                - No inventes datos que no estén presentes.
                - Si no hay información, usa None o listas vacías según corresponda.
                - Mantén la coherencia con los tipos de datos de CVData.
            
                Instrucción para el campo "texto_embedding":
                Crea un texto narrativo fluido, coherente y natural en español, que describa al candidato de manera similar a un resumen profesional de LinkedIn.
                - La longitud debe ser proporcional a la cantidad de información disponible.
                - Si el CV es muy completo, genera una descripción más detallada (200–400 palabras).
                - Si es breve, genera un resumen conciso (100–200 palabras).
                El resultado debe ser una descripción rica en contexto, que capture:
                - Formación académica
                - Experiencia laboral con logros cuantificables
                - Habilidades técnicas y blandas
                - Certificaciones relevantes
                - Idiomas
                - Intereses profesionales o extracurriculares
                - Ubicación y modalidad preferida
                - Enfoque profesional o propósito de carrera

                Ejemplo de estilo narrativo (no de longitud ni contenido):
                “María López es una Ingeniera de Software con más de 5 años de experiencia en desarrollo backend y análisis de datos. Egresada de la Universidad de Buenos Aires, ha trabajado en empresas de tecnología y banca liderando proyectos de optimización de infraestructura. Destaca por su dominio de Python, SQL y Power BI, así como por su capacidad analítica y orientación a resultados.”          
                """),
                ("user", "{cv_usuario}")
            ]
        )

        llm_output = model.with_structured_output(CVData)
        chain = prompt | llm_output
        # Método sync
        # response = chain.invoke({"cv_usuario": document_concatenado})
        
        # Método async 
        response = await chain.ainvoke({"cv_usuario": document_concatenado})
        logger.debug("Se hizo el invoke respectivo para obtener el objeto CVData")

        timestamp = datetime.now().strftime("%d%m%Y")

        metadata = {
        "nombre_completo": response.nombre_completo,
        "dni": response.dni or "",
        "telefono": response.telefono or "",
        "email": response.email or "",
        "linkedin": str(response.linkedin) if response.linkedin else "",
        "portfolio_blog": str(response.portfolio_blog) if response.portfolio_blog else "",
        "fecha_extraccion": timestamp,
        "titulo_profesional": response.titulo_profesional or "",
        "educacion": json.dumps([edu.dict() for edu in response.educacion]) if response.educacion else [],
        "certificaciones": [d for d in response.certificaciones] if response.certificaciones else [],
        "experiencia_laboral": json.dumps([exp.dict() for exp in response.experiencia_laboral]) if response.experiencia_laboral else [],
        "industrias_experiencia": [d for d in response.industrias_experiencia] if response.industrias_experiencia else [],
        "categorias_laborales": [d for d in response.categorias_laborales] if response.categorias_laborales else [],
        "habilidades_tecnicas": [d for d in response.habilidades_tecnicas] if response.habilidades_tecnicas else [],
        "idiomas": json.dumps([idi.dict() for idi in response.idiomas]) if response.idiomas else [],
        "anos_experiencia_total": response.anos_experiencia_total or 0,
        "actividades_extracurriculares": [d for d in response.actividades_extracurriculares] if response.actividades_extracurriculares else [],
        "ubicacion_preferida": response.ubicacion_preferida or "",
        "modalidad_preferida": response.modalidad_preferida or "",
        "nivel_salarial_esperado": json.dumps(response.nivel_salarial_esperado.dict()) if response.nivel_salarial_esperado else [],
        "keywords_perfil": [d for d in response.keywords_perfil] if response.keywords_perfil else [],
        "texto_embedding": response.texto_embedding or ""
        }
        logger.debug(f"La metadata se ha guardado correctamente: {len(metadata)} elemento")
        return {"cv_data": response, "cv_metadata": metadata}
    
    #def embedding_cv(self, state:State):
    async def embedding_cv(self, state:State):
        """
        Aqui se inserta la información del CV en la base vectorial para su posterior uso
        """
        cv_resumen = state["cv_data"].texto_embedding
        logger.info(f"El resumen del usuario tiene un tamaño de: {len(cv_resumen)}")
        metadata = state["cv_metadata"]
        logger.info(f"La metadata se trajo al nodo embedding_cv correctamente, longitud de: {len(metadata)}")
        
        embedding_model = self.llm_embedding
        # Método sync
        #vector_cv = embedding_model.embed_query(cv_resumen)
        # Método async
        vector_cv = await embedding_model.aembed_query(cv_resumen)
        id_unico = str(uuid.uuid4())
        id = state["cv_data"].email if state["cv_data"].email else id_unico

        try:
            pc = Pinecone()
            index_name = "basecvs"
            HOST_BASECVS = os.getenv("HOST_BASECVS")

            # Método async
            async with pc.IndexAsyncio(host=HOST_BASECVS) as index:
                resp = await index.upsert(
                    namespace= "version1",
                    vectors= [
                        {
                            "id": id,
                            "values": vector_cv,
                            "metadata": metadata
                        }
                    ]
                )

            # Método sync
            # index = pc.Index(index_name)
            # resp = index.upsert(
            #     namespace= "version1",
            #     vectors= [
            #         {
            #             "id": id,
            #             "values": vector_cv,
            #             "metadata": metadata
            #         }
            #     ]
            # )
            logger.info(f"Se insertó correctamente el vector en el namespace con el id: {id}")
            return {"id_cv": id, "cv_resumen": cv_resumen, "cv_vector": vector_cv}
        except Exception as e:
            logger.error(f"Hubo un error al momento de insertar el cv_vector en la base de Pinecone. Detalles: {e}")
            return f"Hubo un error al momento de insertar el cv_vector en la base de Pinecone: {e}"
    
    #def busq_simil_cv_vs_empleos(self, state:State):
    async def busq_simil_cv_vs_empleos(self, state:State):
        """
        Realiza una búsqueda por similitud en base al CV proporcionado por el usuario vs una base vectorial de empleos disponibles
        
        Args:
            state: Usar el state actual.
        Returns:
            state: Actualización del state con el campo cv_empleos_recomendados
        """
        logger.debug("Iniciando el proceso del nodo búsqueda por similitud del cv")
        pc = Pinecone()
        name_index = "recursoshumanos"
        name_namespace = "empleos"
        vector_cv = state["cv_vector"]
        HOST_EMPLEOS = os.getenv("HOST_EMPLEOS")
        #llm = self.llm_embedding
        #id_cv = state["id_cv"]
        #vector_value = llm.embed_query()
        try:
            # Método sync
            # index = pc.Index(name=name_index)
            # matchs = index.query(
            #     namespace= name_namespace,
            #     vector= vector_cv,
            #     #id= id_cv,
            #     top_k= 5,
            #     include_metadata= True,
            #     include_values= False
            # )
            
            # Método async
            async with pc.IndexAsyncio(host=HOST_EMPLEOS) as index:
                matchs = await index.query(
                    namespace= name_namespace,
                    vector= vector_cv,
                    top_k= 5,
                    include_metadata= True,
                    include_values= False
                )
        except Exception as e:
            logger.debug("Falló la búsqueda del vector por el método .query()")
        logger.debug("Se realizó la búsqueda por similitud del ID")
        matchs_dict = matchs.to_dict()
        matchs_dict_lista = matchs_dict["matches"] # lista de dict
        return {"cv_empleos_recomendados": matchs_dict_lista}
    
    # def transformacion_respuesta_busqueda(self, state: State):
    async def transformacion_respuesta_busqueda(self, state: State):
        """
        Transforma los resultados extraídos de la búsqueda de similitud a una respuesta más detallada al usuario
        """
        logger.debug("Inicio del método transformacion_respuesta_busqueda...")
        empleos_recomendados = state["cv_empleos_recomendados"]
        cv_resumen = state["cv_resumen"]
        llm = self.llm
        
        llm_with_output = llm.with_structured_output(ListaEmpleosData)
        logger.debug("Se cargó correctamente la LLM with otput de EmpleosData")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """

                Tu tarea es analizar cada oferta y devolver una lista de objetos estructurados siguiendo el modelo `EmpleosData`.

                Cada objeto debe reflejar el análisis comparativo entre la oferta de trabajo y el CV del usuario, con un lenguaje profesional, natural y coherente.

                Formato obligatorio de cada objeto (`EmpleosData`):

                - `nombre_empleo`: título exacto del puesto.
                - `modalidad_trabajo`: modalidad de trabajo (Full-time, Part-time, Híbrido, Presencial o Remoto).
                - `ubicacion`: ciudad o país donde se desarrolla el empleo.
                - `seniority`: nivel del puesto (Junior, Semi-senior, Senior, etc.).
                - `experiencia_relevante`: escribe un breve párrafo que comience con **“Experiencia relevante”**, seguido de una explicación concreta sobre por qué la experiencia del usuario se alinea con el puesto. Ejemplo:
                > Experiencia relevante  
                > Tienes una amplia experiencia en desarrollo backend y sistemas distribuidos, lo cual se alinea perfectamente con el enfoque del puesto en roles de ingeniería backend.
                - `seniority_relevante`: escribe un párrafo que comience con **“Antigüedad/Años de experiencia”**, donde compares el nivel de experiencia del usuario con lo que requiere el puesto. Ejemplo:
                > Antigüedad/Años de experiencia  
                > Tus más de 5 años de experiencia como Ingeniero Backend superan el requisito de más de 3 años, lo que te convierte en un candidato sólido para el puesto de Ingeniero Backend Senior.
                - `educacion_relevante`: comienza con **“Educación”**, y explica por qué la formación académica del usuario encaja con el empleo. Ejemplo:
                > Educación  
                > Tu licenciatura en Ciencias de la Computación en UCSD cumple con el requisito educativo para este sector y nivel de antigüedad.
                - `skills_relevante`: comienza con **“Habilidades principales”**, y describe brevemente qué herramientas o tecnologías del CV son relevantes. Ejemplo:
                > Habilidades principales  
                > Tienes dominio en tecnologías clave de backend como Python y diseño de sistemas, esenciales para el puesto. Sin embargo, tu falta de experiencia en Rust indica una coincidencia parcial.
                - `url`: URL directa del puesto de trabajo.
                - `puntuacion_match`: valor derivado del score de Pinecone (escala 0–1 → convierte a porcentaje entre 0 y 100, con dos decimales).

                📌 Reglas importantes:
                - Usa solo la información que aparezca en el CV o en la oferta.
                - Mantén un tono profesional, claro y objetivo.
                - No inventes datos.
                - La salida **debe ser estructurada** (lista de objetos tipo `EmpleosData`), no narrativa.
                - No incluyas texto adicional ni explicaciones fuera de los campos definidos.
                """),
                ("user", """
                Este es el CV del usuario:
                {cv_usuario}

                Estas son las ofertas de empleo encontradas:
                {ofertas_empleo}
                """)
            ]
        )

        chain = prompt | llm_with_output
        # Método sync:
        # response = chain.invoke({"cv_usuario": cv_resumen, "ofertas_empleo": empleos_recomendados})

        # Método async:
        response = await chain.ainvoke({"cv_usuario": cv_resumen, "ofertas_empleo": empleos_recomendados})
        logger.debug("Se ha realizado el invoke correctamente para tener el feedback al usuario de cada oferta de empleo.")
        return {"cv_feedback": response}
    
    def respuesta_usuario_cv(self, state: State):
        """
        Respuesta final al usuario cuando carga su CV en el front.
        """
        lista_obj_recomendados = state["cv_feedback"]
        #lista_objetos_final = lista_obj_recomendados.lista_empleos_data
        logger.debug(f"Se ha cargado correctamente la lista de objetos del feedback...")
        logger.debug(f"El tipo de variable de 'lista_obj_recomendados': {type(lista_obj_recomendados)}")
        logger.debug(f"El contenido de la variable 'lista_obj_recomendados': {lista_obj_recomendados}")
        
        str_final_usuario = ""
        contador = 0
        for obj in lista_obj_recomendados.lista_empleos_data:
            contador += 1
            respuesta_final = f"""
            **Empleo #{contador}**\n
            🔥 Match con tu Perfil: {obj.puntuacion_match}\n
            💼 {obj.nombre_empleo}\n
            📍 Ubicación: {obj.ubicacion}\n
            💻 Modalidad: {obj.modalidad_trabajo}\n
            🎓 Seniority: {obj.seniority}\n
            📅 Años de experiencia: {obj.anos_experiencia}\n
            🔗 URL de la oferta: <a href="{obj.url}" target ="_blank">Ver Empleo</a>\n\n
            ----------------------------\n
            """
            str_final_usuario += respuesta_final
        
        #lista_empleos = [empleo for empleo in lista_obj_recomendados]
        
        logger.debug("Se creó correctamente la concatenación de respuestas al usuario de cada oferta laboral.")
        logger.debug(str_final_usuario)
        return {"respuesta_empleos_recomendados": str_final_usuario}








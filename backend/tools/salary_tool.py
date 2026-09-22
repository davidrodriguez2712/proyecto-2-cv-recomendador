import os
from pathlib import Path
import logging
import joblib
from langchain_core.tools import tool
from pinecone import Pinecone
from llms.openaillm import OpenAILLM

logger = logging.getLogger("backend.salary_tool")

_bm25_instance = None
_pinecone_index_instance = None

def get_bm25_model():
    """Retorna la instancia en caché del modelo BM25 o la carga si es la primera vez."""
    global _bm25_instance
    if _bm25_instance is None:
        knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
        bm25_path = knowledge_dir / "bm25_fit.pkl"
        if bm25_path.exists():
            logger.info("Cargando modelo BM25 en memoria...")
            _bm25_instance = joblib.load(bm25_path)
        else:
            logger.warning(f"Archivo BM25 no encontrado en: {bm25_path}")
    return _bm25_instance

def get_pinecone_index():
    """Retorna la instancia en caché del índice Pinecone o la inicializa si es la primera vez."""
    global _pinecone_index_instance
    if _pinecone_index_instance is None:
        logger.info("Inicializando cliente Pinecone...")
        pc = Pinecone()
        _pinecone_index_instance = pc.Index(name="rag-sueldosperu")
    return _pinecone_index_instance

@tool
def consultar_sueldos_peru(consulta: str) -> str:
    """Consulta la base de datos de rangos salariales y compensaciones en el mercado laboral de Perú.
    Úsala cuando el usuario pregunte por sueldos, salarios o tarifas de perfiles laborales en Perú."""
    try:
        if not consulta or not consulta.strip():
            return "Por favor indica el puesto o rol profesional sobre el cual deseas consultar el sueldo."

        bm25 = get_bm25_model()
        if bm25 is None:
            return "La base de conocimientos salariales no está disponible localmente."

        vector_sparse = bm25.encode_queries(consulta)

        embedding_llm = OpenAILLM().embedding_llm
        vector_dense = embedding_llm.embed_query(consulta)

        index = get_pinecone_index()

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

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

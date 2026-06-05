from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

class OpenAILLM:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", timeout= 120)
        self.embedding_llm = OpenAIEmbeddings(model="text-embedding-3-small")

    def openai_model(self, x):
        """Retorna la LLM de openai (gpt-4o-mini)"""
        llm = self.llm
        return llm
    
    def openai_embedding_model(self):
        """Retorna la LLM Embedding de openai (text-embedding-3-small)"""
        embedding_llm = self.embedding_llm

        return embedding_llm











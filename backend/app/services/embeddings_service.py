from typing import List
from openai import OpenAI
from app.config import settings

class EmbeddingsService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Modelo recomendado en la API >=1.0.0
        self.model = "text-embedding-3-small"
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            raise Exception(f"Error al generar embeddings: {str(e)}")
    
    # Adapter para LangChain: mismo nombre que espera FAISS
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embed_texts(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una consulta"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error al generar embedding para consulta: {str(e)}")

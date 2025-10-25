import json
from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from app.config import settings
from app.services.vector_store import VectorStore

class ChatService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.vector_store = VectorStore()
    
    def _format_context(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Formatea los documentos similares como contexto"""
        if not similar_docs:
            return "No se encontró información relevante en los documentos."
        
        context_parts = []
        for i, doc in enumerate(similar_docs, 1):
            context_parts.append(f"Documento {i}:\n{doc['content']}\n")
        
        return "\n".join(context_parts)
    
    def _check_relevance(self, similar_docs: List[Dict[str, Any]], query: str) -> bool:
        """Considera relevante si existe al menos un resultado."""
        return bool(similar_docs)
    
    async def generate_response_stream(
        self, 
        query: str, 
        chat_history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """Genera una respuesta en streaming usando RAG"""
        try:
            # Buscar documentos similares
            similar_docs = self.vector_store.search_similar(query, n_results=3)
            
            # Si no hay resultados, responder con el mensaje específico
            if not self._check_relevance(similar_docs, query):
                yield "No poseo información sobre ese tema en el documento cargado"
                return
            
            context = self._format_context(similar_docs)
            
            # Construir mensajes para OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """Eres un asistente útil que responde preguntas basándose ÚNICAMENTE en los documentos proporcionados. 
                    Usa únicamente la información del contexto para responder. Si no encuentras información relevante 
                    en el contexto, responde exactamente: "No poseo información sobre ese tema en el documento cargado".
                    
                    Responde de manera clara y concisa en español."""
                }
            ]
            
            # Añadir historial de chat si existe
            if chat_history:
                for msg in chat_history[-5:]:  # Últimos 5 mensajes
                    messages.append(msg)
            
            # Añadir la consulta actual con contexto
            messages.append({
                "role": "user",
                "content": f"Contexto de los documentos:\n{context}\n\nPregunta: {query}"
            })
            
            # Generar respuesta en streaming
            stream = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error al generar respuesta: {str(e)}"
    
    async def generate_response(
        self, 
        query: str, 
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Genera una respuesta completa usando RAG"""
        try:
            # Buscar documentos similares
            similar_docs = self.vector_store.search_similar(query, n_results=3)
            
            # Si no hay resultados, responder con el mensaje específico
            if not self._check_relevance(similar_docs, query):
                return "No poseo información sobre ese tema en el documento cargado"
            
            context = self._format_context(similar_docs)
            
            # Construir mensajes para OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """Eres un asistente útil que responde preguntas basándose ÚNICAMENTE en los documentos proporcionados. 
                    Usa únicamente la información del contexto para responder. Si no encuentras información relevante 
                    en el contexto, responde exactamente: "No poseo información sobre ese tema en el documento cargado".
                    
                    Responde de manera clara y concisa en español."""
                }
            ]
            
            # Añadir historial de chat si existe
            if chat_history:
                for msg in chat_history[-5:]:  # Últimos 5 mensajes
                    messages.append(msg)
            
            # Añadir la consulta actual con contexto
            messages.append({
                "role": "user",
                "content": f"Contexto de los documentos:\n{context}\n\nPregunta: {query}"
            })
            
            # Generar respuesta
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """Obtiene información del almacén vectorial"""
        return self.vector_store.get_collection_info()

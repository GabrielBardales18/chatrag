import os
from typing import List, Dict, Any
from langchain.vectorstores import FAISS
from app.config import settings
from app.services.embeddings_service import EmbeddingsService

class VectorStore:
    def __init__(self):
        # Usar nuestro servicio que implementa embed_documents/embed_query con OpenAI >=1.0
        self.embeddings = EmbeddingsService()
        self.vectorstore = None
        self.storage_path = os.path.join(settings.CHROMA_PERSIST_DIRECTORY, "faiss_index")
        self.load_vectorstore()
    
    def load_vectorstore(self):
        """Carga el vectorstore desde disco"""
        try:
            if os.path.exists(self.storage_path):
                self.vectorstore = FAISS.load_local(
                    self.storage_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self.vectorstore = None
        except Exception as e:
            print(f"Error al cargar vectorstore: {e}")
            self.vectorstore = None
    
    def save_vectorstore(self):
        """Guarda el vectorstore en disco"""
        try:
            if self.vectorstore:
                self.vectorstore.save_local(self.storage_path)
        except Exception as e:
            print(f"Error al guardar vectorstore: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Añade documentos al almacén vectorial"""
        try:
            # Preparar textos y metadatos
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]

            if self.vectorstore is None:
                # Crear nuevo vectorstore
                self.vectorstore = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas
                )
            else:
                # Añadir a vectorstore existente
                self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            
            # Guardar en disco
            self.save_vectorstore()
            
            return True
        except Exception as e:
            raise Exception(f"Error al añadir documentos al almacén vectorial: {str(e)}")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares a la consulta"""
        try:
            if self.vectorstore is None:
                return []
            
            # Buscar documentos similares
            docs = self.vectorstore.similarity_search_with_score(query, k=n_results)
            
            # Formatear resultados
            formatted_results = []
            for doc, score in docs:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "distance": float(score)
                })
            
            return formatted_results
        except Exception as e:
            raise Exception(f"Error al buscar documentos similares: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la colección"""
        try:
            if self.vectorstore is None:
                return {
                    "total_documents": 0,
                    "collection_name": "pdf_documents"
                }
            
            # Obtener información del vectorstore
            return {
                "total_documents": self.vectorstore.index.ntotal if hasattr(self.vectorstore, 'index') else 0,
                "collection_name": "pdf_documents"
            }
        except Exception as e:
            raise Exception(f"Error al obtener información de la colección: {str(e)}")
    
    def clear_collection(self) -> bool:
        """Limpia toda la colección"""
        try:
            self.vectorstore = None
            if os.path.exists(self.storage_path):
                import shutil
                shutil.rmtree(self.storage_path)
            return True
        except Exception as e:
            raise Exception(f"Error al limpiar la colección: {str(e)}")

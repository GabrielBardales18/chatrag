import os
import json
import uuid
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore
from app.services.chat_service import ChatService

# Crear directorios necesarios
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

app = FastAPI(title="RAG Chat API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
pdf_processor = PDFProcessor()
vector_store = VectorStore()
chat_service = ChatService()

# Almacenar conexiones WebSocket activas
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "RAG Chat API está funcionando"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "vector_store": vector_store.get_collection_info()}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint para subir y procesar un PDF"""
    try:
        # Validar archivo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Generar nombre único para el archivo
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_FOLDER, f"{file_id}.pdf")
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validar PDF
        if not pdf_processor.validate_pdf(file_path):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Archivo PDF inválido o corrupto")
        
        # Procesar PDF
        result = pdf_processor.process_pdf(file_path)
        
        # Añadir al almacén vectorial
        success = vector_store.add_documents(result["chunks"])
        
        if not success:
            os.remove(file_path)
            raise HTTPException(status_code=500, detail="Error al procesar el documento")
        
        # Limpiar archivo temporal
        os.remove(file_path)
        
        return JSONResponse(content={
            "message": "PDF procesado exitosamente",
            "file_id": file_id,
            "total_chunks": result["total_chunks"],
            "total_characters": result["total_characters"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Limpiar archivo si existe
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Obtiene información sobre los documentos cargados"""
    try:
        info = vector_store.get_collection_info()
        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documentos: {str(e)}")

@app.delete("/documents")
async def clear_documents():
    """Limpia todos los documentos del almacén vectorial"""
    try:
        success = vector_store.clear_collection()
        if success:
            return JSONResponse(content={"message": "Documentos eliminados exitosamente"})
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar documentos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar documentos: {str(e)}")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para chat en tiempo real"""
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            query = message_data.get("query", "")
            chat_history = message_data.get("chat_history", [])
            
            if not query.strip():
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Consulta vacía"}), 
                    client_id
                )
                continue
            
            # Enviar indicador de que está procesando
            await manager.send_personal_message(
                json.dumps({"type": "processing", "message": "Procesando..."}), 
                client_id
            )
            
            # Generar respuesta en streaming
            full_response = ""
            async for chunk in chat_service.generate_response_stream(query, chat_history):
                full_response += chunk
                await manager.send_personal_message(
                    json.dumps({
                        "type": "chunk", 
                        "content": chunk,
                        "full_response": full_response
                    }), 
                    client_id
                )
            
            # Enviar mensaje de finalización
            await manager.send_personal_message(
                json.dumps({
                    "type": "complete", 
                    "message": "Respuesta completada",
                    "full_response": full_response
                }), 
                client_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": f"Error: {str(e)}"}), 
            client_id
        )
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

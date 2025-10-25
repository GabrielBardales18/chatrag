# RAG Chat - Aplicación de Chat con Documentos PDF

Una aplicación moderna que permite chatear con documentos PDF usando RAG (Retrieval-Augmented Generation), WebSockets para comunicación en tiempo real, y la API de OpenAI.

## 🚀 Características

- **Subida de PDFs**: Interfaz drag & drop para subir documentos PDF
- **Chat en tiempo real**: Comunicación bidireccional vía WebSockets
- **RAG con OpenAI**: Búsqueda vectorial + generación de respuestas
- **Streaming de respuestas**: Visualización en tiempo real de las respuestas
- **UI moderna**: Interfaz limpia y responsiva con Nuxt 3 y Tailwind CSS
- **Almacenamiento vectorial**: ChromaDB para embeddings persistentes

## 🏗️ Arquitectura

### Backend (FastAPI)
- **FastAPI**: Framework web moderno y rápido
- **WebSockets**: Comunicación en tiempo real
- **ChromaDB**: Base de datos vectorial para embeddings
- **LangChain**: Orquestación del pipeline RAG
- **OpenAI API**: Embeddings y generación de texto
- **PyPDF2**: Procesamiento de archivos PDF

### Frontend (Nuxt 3)
- **Nuxt 3**: Framework Vue.js con SSR/SSG
- **Vue 3 Composition API**: Reactividad moderna
- **Tailwind CSS**: Estilos utilitarios
- **WebSocket Client**: Comunicación en tiempo real
- **VueUse**: Utilidades de Vue

## 📁 Estructura del Proyecto

```
ChatRag/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicación FastAPI principal
│   │   ├── config.py            # Configuración
│   │   └── services/
│   │       ├── pdf_processor.py # Procesamiento de PDFs
│   │       ├── embeddings_service.py # Servicio de embeddings
│   │       ├── vector_store.py  # Operaciones ChromaDB
│   │       └── chat_service.py  # Servicio RAG
│   ├── requirements.txt         # Dependencias Python
│   └── .env.example            # Variables de entorno
└── frontend/
    ├── components/
    │   ├── PdfUploader.vue     # Componente de subida
    │   ├── ChatInterface.vue   # Interfaz de chat
    │   └── MessageBubble.vue   # Burbuja de mensaje
    ├── composables/
    │   └── useWebSocket.js     # Composable WebSocket
    ├── pages/
    │   └── index.vue           # Página principal
    ├── assets/css/
    │   └── main.css            # Estilos globales
    ├── package.json            # Dependencias Node.js
    └── nuxt.config.ts          # Configuración Nuxt
```

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Node.js 18+
- Clave API de OpenAI

### Backend

1. **Navegar al directorio del backend:**
   ```bash
   cd ChatRag/backend
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env y añadir tu OPENAI_API_KEY
   ```

5. **Ejecutar el servidor:**
   ```bash
   python -m app.main
   # O usando uvicorn directamente:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. **Navegar al directorio del frontend:**
   ```bash
   cd ChatRag/frontend
   ```

2. **Instalar dependencias:**
   ```bash
   npm install
   ```

3. **Ejecutar en modo desarrollo:**
   ```bash
   npm run dev
   ```

4. **Abrir en el navegador:**
   ```
   http://localhost:3000
   ```

## 🔧 Configuración

### Variables de Entorno

**Backend (.env):**
```env
OPENAI_API_KEY=tu_clave_api_aqui
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_FOLDER=./uploads
```

**Frontend (nuxt.config.ts):**
```typescript
runtimeConfig: {
  public: {
    apiBase: 'http://localhost:8000',
    wsBase: 'ws://localhost:8000'
  }
}
```

## 📡 API Endpoints

### REST API
- `GET /` - Estado de la API
- `GET /health` - Verificación de salud
- `POST /upload-pdf` - Subir y procesar PDF
- `GET /documents` - Información de documentos
- `DELETE /documents` - Limpiar documentos

### WebSocket
- `WS /ws/chat` - Chat en tiempo real

## 🎯 Flujo de Trabajo

1. **Subida de PDF**: El usuario sube un archivo PDF
2. **Procesamiento**: El backend extrae texto y lo divide en chunks
3. **Embeddings**: Se generan embeddings usando OpenAI
4. **Almacenamiento**: Los embeddings se guardan en ChromaDB
5. **Chat**: El usuario hace preguntas vía WebSocket
6. **RAG**: Se buscan chunks similares y se genera respuesta
7. **Streaming**: La respuesta se envía en tiempo real

## 🚀 Uso

1. **Iniciar el backend** en el puerto 8000
2. **Iniciar el frontend** en el puerto 3000
3. **Subir un PDF** usando la interfaz drag & drop
4. **Esperar** a que se procese el documento
5. **Hacer preguntas** sobre el contenido del PDF
6. **Recibir respuestas** en tiempo real

## 🔍 Características Técnicas

### RAG Pipeline
- **Chunking**: División inteligente del texto en fragmentos
- **Embeddings**: Vectorización usando text-embedding-ada-002
- **Búsqueda**: Búsqueda de similitud coseno en ChromaDB
- **Generación**: Respuestas contextuales con GPT-3.5-turbo

### WebSocket
- **Conexión persistente**: Mantiene conexión activa
- **Reconexión automática**: Manejo de desconexiones
- **Streaming**: Respuestas en tiempo real
- **Manejo de errores**: Gestión robusta de errores

### Frontend
- **Responsive**: Diseño adaptativo
- **Real-time**: Actualizaciones instantáneas
- **UX moderna**: Interfaz intuitiva
- **Manejo de estados**: Gestión completa del estado

## 🐛 Solución de Problemas

### Backend no inicia
- Verificar que Python 3.8+ esté instalado
- Verificar que todas las dependencias estén instaladas
- Verificar que la clave API de OpenAI esté configurada

### Frontend no se conecta
- Verificar que el backend esté ejecutándose
- Verificar la configuración de CORS
- Verificar las URLs en nuxt.config.ts

### WebSocket no funciona
- Verificar que el puerto 8000 esté disponible
- Verificar la configuración de firewall
- Verificar que no haya proxies bloqueando WebSockets

## 📝 Notas de Desarrollo

- El proyecto usa TypeScript en el frontend
- Los estilos están en Tailwind CSS
- La comunicación es completamente asíncrona
- Se incluye manejo de errores robusto
- El código está documentado en español

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

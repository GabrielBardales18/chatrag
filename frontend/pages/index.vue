<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">RAG Chat</h1>
            <span class="ml-3 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
              Beta
            </span>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="text-sm text-gray-600">
                {{ isConnected ? 'Conectado' : 'Desconectado' }}
              </span>
            </div>
            <button 
              @click="showDocumentInfo = !showDocumentInfo"
              class="btn-secondary"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Documentos
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Panel izquierdo: Subida de PDF -->
        <div class="space-y-6">
          <div>
            <h2 class="text-lg font-medium text-gray-900 mb-4">1. Subir Documento</h2>
            <PdfUploader 
              @upload-success="handleUploadSuccess"
              @upload-error="handleUploadError"
            />
          </div>

          <!-- Información del documento -->
          <div v-if="showDocumentInfo" class="card p-4">
            <h3 class="text-md font-medium text-gray-900 mb-3">Información del Sistema</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Estado de conexión:</span>
                <span :class="isConnected ? 'text-green-600' : 'text-red-600'">
                  {{ isConnected ? 'Conectado' : 'Desconectado' }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Documentos cargados:</span>
                <span class="text-gray-900">{{ documentCount }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Última subida:</span>
                <span class="text-gray-900">{{ lastUploadTime || 'Ninguna' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Panel derecho: Chat -->
        <div class="space-y-6">
          <div>
            <h2 class="text-lg font-medium text-gray-900 mb-4">2. Chatear con el Documento</h2>
            <ChatInterface />
          </div>
        </div>
      </div>

      <!-- Mensajes de estado -->
      <div v-if="statusMessage" class="mt-6">
        <div :class="[
          'p-4 rounded-lg',
          statusMessage.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 
          statusMessage.type === 'error' ? 'bg-red-50 border border-red-200 text-red-800' :
          'bg-blue-50 border border-blue-200 text-blue-800'
        ]">
          <div class="flex items-center">
            <svg v-if="statusMessage.type === 'success'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else-if="statusMessage.type === 'error'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ statusMessage.text }}</span>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center text-sm text-gray-500">
          <p>RAG Chat - Aplicación de chat conversacional con documentos PDF</p>
          <p class="mt-1">Powered by OpenAI, ChromaDB y Nuxt 3</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Meta tags
useHead({
  title: 'RAG Chat - Chat con Documentos PDF',
  meta: [
    { name: 'description', content: 'Aplicación de chat conversacional con documentos PDF usando RAG, WebSockets y OpenAI' }
  ]
})

// Estado del componente
const showDocumentInfo = ref(false)
const documentCount = ref(0)
const lastUploadTime = ref('')
const statusMessage = ref(null)

// WebSocket connection
const { isConnected } = useWebSocket()

const config = useRuntimeConfig()

// Manejar éxito de subida
const handleUploadSuccess = (result) => {
  documentCount.value = result.total_chunks
  lastUploadTime.value = new Date().toLocaleString('es-ES')
  
  statusMessage.value = {
    type: 'success',
    text: `¡Documento procesado exitosamente! Se generaron ${result.total_chunks} fragmentos.`
  }
  
  // Limpiar mensaje después de 5 segundos
  setTimeout(() => {
    statusMessage.value = null
  }, 5000)
}

// Manejar error de subida
const handleUploadError = (error) => {
  statusMessage.value = {
    type: 'error',
    text: `Error al procesar el documento: ${error}`
  }
  
  // Limpiar mensaje después de 5 segundos
  setTimeout(() => {
    statusMessage.value = null
  }, 5000)
}

// Cargar información inicial
onMounted(async () => {
  try {
    const response = await $fetch(`${config.public.apiBase}/documents`)
    documentCount.value = response.total_documents
  } catch (error) {
    console.error('Error al cargar información de documentos:', error)
  }
})
</script>

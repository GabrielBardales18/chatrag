<template>
  <div class="card h-96 flex flex-col">
    <!-- Header del chat -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
      <div class="flex items-center space-x-3">
        <div class="w-3 h-3 rounded-full" :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></div>
        <h3 class="text-lg font-medium text-gray-900">Chat con el documento</h3>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500">{{ messages.length }} mensajes</span>
        <button 
          @click="clearMessages" 
          class="text-gray-400 hover:text-gray-600 transition-colors"
          title="Limpiar chat"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Área de mensajes -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- Mensaje de bienvenida -->
      <div v-if="messages.length === 0" class="text-center text-gray-500 py-8">
        <svg class="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <p class="text-lg font-medium">¡Hola! 👋</p>
        <p class="text-sm">Sube un documento PDF y comienza a hacer preguntas sobre su contenido.</p>
      </div>

      <!-- Mensajes del chat -->
      <MessageBubble 
        v-for="message in messages" 
        :key="message.id" 
        :message="message" 
      />

      <!-- Respuesta en streaming -->
      <div v-if="isProcessing && currentResponse" class="flex justify-start mb-4">
        <div class="message-bubble message-assistant">
          <div class="whitespace-pre-wrap">{{ currentResponse }}</div>
          <div class="flex items-center mt-2">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
            <span class="text-xs text-gray-500 ml-2">Escribiendo...</span>
          </div>
        </div>
      </div>

      <!-- Indicador de conexión -->
      <div v-if="!isConnected && !isConnecting" class="text-center text-red-500 py-4">
        <p class="text-sm">Sin conexión al servidor</p>
        <button @click="connect" class="btn-primary mt-2">Reconectar</button>
      </div>
    </div>

    <!-- Área de entrada -->
    <div class="p-4 border-t border-gray-200">
      <div class="flex space-x-2">
        <input
          v-model="inputMessage"
          @keydown.enter="sendMessage"
          :disabled="!isConnected || isProcessing"
          placeholder="Escribe tu pregunta aquí..."
          class="input-field flex-1"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || !isConnected || isProcessing"
          class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      
      <!-- Mensaje de error -->
      <div v-if="error" class="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'

const { 
  isConnected, 
  isConnecting, 
  error, 
  messages, 
  currentResponse, 
  isProcessing, 
  connect, 
  sendMessage: sendWebSocketMessage, 
  clearMessages: clearWebSocketMessages 
} = useWebSocket()

const inputMessage = ref('')
const messagesContainer = ref(null)

// Auto-scroll al final cuando hay nuevos mensajes
watch([messages, currentResponse], async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}, { deep: true })

const sendMessage = () => {
  if (!inputMessage.value.trim() || !isConnected.value || isProcessing.value) {
    return
  }

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  // Crear historial de chat para el contexto
  const chatHistory = messages.value.slice(-10).map(msg => ({
    role: msg.type === 'user' ? 'user' : 'assistant',
    content: msg.content
  }))

  sendWebSocketMessage(message, chatHistory)
}

const clearMessages = () => {
  clearWebSocketMessages()
}
</script>

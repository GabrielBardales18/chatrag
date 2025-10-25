import { ref, onMounted, onUnmounted } from 'vue'

export const useWebSocket = () => {
  const socket = ref(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref(null)
  const messages = ref([])
  const currentResponse = ref('')
  const isProcessing = ref(false)

  const config = useRuntimeConfig()

  const connect = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      return
    }

    isConnecting.value = true
    error.value = null

    try {
      socket.value = new WebSocket(`${config.public.wsBase}/ws/chat`)

      socket.value.onopen = () => {
        isConnected.value = true
        isConnecting.value = false
        console.log('WebSocket conectado')
      }

      socket.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          switch (data.type) {
            case 'processing':
              isProcessing.value = true
              currentResponse.value = ''
              break
              
            case 'chunk':
              currentResponse.value = data.full_response
              break
              
            case 'complete':
              isProcessing.value = false
              if (currentResponse.value) {
                messages.value.push({
                  id: Date.now(),
                  type: 'assistant',
                  content: currentResponse.value,
                  timestamp: new Date()
                })
                currentResponse.value = ''
              }
              break
              
            case 'error':
              isProcessing.value = false
              error.value = data.message
              break
          }
        } catch (err) {
          console.error('Error al procesar mensaje WebSocket:', err)
          error.value = 'Error al procesar respuesta del servidor'
        }
      }

      socket.value.onclose = () => {
        isConnected.value = false
        isConnecting.value = false
        isProcessing.value = false
        console.log('WebSocket desconectado')
      }

      socket.value.onerror = (err) => {
        isConnected.value = false
        isConnecting.value = false
        isProcessing.value = false
        error.value = 'Error de conexión WebSocket'
        console.error('Error WebSocket:', err)
      }

    } catch (err) {
      isConnecting.value = false
      error.value = 'No se pudo conectar al servidor'
      console.error('Error al conectar WebSocket:', err)
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    isConnected.value = false
    isConnecting.value = false
    isProcessing.value = false
  }

  const sendMessage = (query, chatHistory = []) => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      error.value = 'No hay conexión con el servidor'
      return
    }

    // Añadir mensaje del usuario
    messages.value.push({
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    })

    // Enviar mensaje al servidor
    const message = {
      query: query,
      chat_history: chatHistory
    }

    try {
      socket.value.send(JSON.stringify(message))
      error.value = null
    } catch (err) {
      error.value = 'Error al enviar mensaje'
      console.error('Error al enviar mensaje:', err)
    }
  }

  const clearMessages = () => {
    messages.value = []
    currentResponse.value = ''
    error.value = null
  }

  // Auto-conectar al montar
  onMounted(() => {
    connect()
  })

  // Desconectar al desmontar
  onUnmounted(() => {
    disconnect()
  })

  return {
    socket: readonly(socket),
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    error: readonly(error),
    messages: readonly(messages),
    currentResponse: readonly(currentResponse),
    isProcessing: readonly(isProcessing),
    connect,
    disconnect,
    sendMessage,
    clearMessages
  }
}

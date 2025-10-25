<template>
  <div class="card p-6">
    <div class="text-center">
      <div class="mb-4">
        <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      
      <div v-if="!isUploading && !uploadSuccess" class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Subir documento PDF</h3>
        <p class="text-sm text-gray-500">Arrastra y suelta tu archivo PDF aquí, o haz clic para seleccionar</p>
        
        <div
          ref="dropZone"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          :class="[
            'border-2 border-dashed rounded-lg p-6 transition-colors cursor-pointer',
            isDragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          ]"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect"
            class="hidden"
          />
          <div class="text-center">
            <svg class="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <span class="font-medium text-blue-600 hover:text-blue-500">Haz clic para subir</span>
              o arrastra y suelta
            </p>
            <p class="text-xs text-gray-500 mt-1">PDF hasta 10MB</p>
          </div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div v-if="isUploading" class="space-y-4">
        <div class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <h3 class="text-lg font-medium text-gray-900">Procesando PDF...</h3>
        <p class="text-sm text-gray-500">{{ uploadProgress }}</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: progressPercentage + '%' }"></div>
        </div>
      </div>

      <!-- Estado de éxito -->
      <div v-if="uploadSuccess" class="space-y-4">
        <div class="flex justify-center">
          <svg class="h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-green-900">¡PDF procesado exitosamente!</h3>
        <p class="text-sm text-gray-600">
          Se procesaron {{ uploadResult.total_chunks }} fragmentos del documento.
        </p>
        <button @click="resetUpload" class="btn-primary">
          Subir otro documento
        </button>
      </div>

      <!-- Estado de error -->
      <div v-if="uploadError" class="space-y-4">
        <div class="flex justify-center">
          <svg class="h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-red-900">Error al procesar PDF</h3>
        <p class="text-sm text-red-600">{{ uploadError }}</p>
        <button @click="resetUpload" class="btn-primary">
          Intentar de nuevo
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['upload-success', 'upload-error'])

// Estado del componente
const isUploading = ref(false)
const isDragOver = ref(false)
const uploadProgress = ref('')
const progressPercentage = ref(0)
const uploadSuccess = ref(false)
const uploadError = ref('')
const uploadResult = ref(null)

// Referencias del DOM
const dropZone = ref(null)
const fileInput = ref(null)

const config = useRuntimeConfig()

// Manejar drag and drop
const handleDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

// Manejar selección de archivo
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    handleFile(file)
  }
}

// Procesar archivo
const handleFile = async (file) => {
  // Validaciones
  if (!file.type.includes('pdf')) {
    uploadError.value = 'Solo se permiten archivos PDF'
    return
  }

  if (file.size > 10 * 1024 * 1024) { // 10MB
    uploadError.value = 'El archivo es demasiado grande (máximo 10MB)'
    return
  }

  // Resetear estado
  uploadError.value = ''
  uploadSuccess.value = false
  isUploading.value = true
  progressPercentage.value = 0

  try {
    // Simular progreso
    uploadProgress.value = 'Subiendo archivo...'
    progressPercentage.value = 20

    const formData = new FormData()
    formData.append('file', file)

    uploadProgress.value = 'Procesando PDF...'
    progressPercentage.value = 50

    const response = await $fetch(`${config.public.apiBase}/upload-pdf`, {
      method: 'POST',
      body: formData
    })

    uploadProgress.value = 'Generando embeddings...'
    progressPercentage.value = 80

    // Simular tiempo de procesamiento
    await new Promise(resolve => setTimeout(resolve, 1000))

    progressPercentage.value = 100
    uploadProgress.value = '¡Completado!'

    uploadResult.value = response
    uploadSuccess.value = true
    
    emit('upload-success', response)

  } catch (error) {
    console.error('Error al subir PDF:', error)
    uploadError.value = error.data?.detail || 'Error al procesar el PDF'
    emit('upload-error', uploadError.value)
  } finally {
    isUploading.value = false
  }
}

// Resetear estado de subida
const resetUpload = () => {
  isUploading.value = false
  uploadSuccess.value = false
  uploadError.value = ''
  uploadResult.value = null
  progressPercentage.value = 0
  uploadProgress.value = ''
  
  // Limpiar input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

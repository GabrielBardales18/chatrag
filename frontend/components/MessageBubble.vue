<template>
  <div :class="[
    'flex mb-4',
    message.type === 'user' ? 'justify-end' : 'justify-start'
  ]">
    <div :class="[
      'message-bubble',
      message.type === 'user' ? 'message-user' : 'message-assistant'
    ]">
      <div class="whitespace-pre-wrap">{{ message.content }}</div>
      <div :class="[
        'text-xs mt-1 opacity-70',
        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
      ]">
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: Object,
    required: true
  }
})

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

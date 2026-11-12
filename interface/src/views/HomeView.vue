<template>
  <main class="starter">
    <h1>Plantilla de proyecto</h1>
    <p>La interfaz está lista para iniciar.</p>
    <p class="backend-status" :class="{ connected }" role="status" aria-live="polite">
      {{ status }}
    </p>
  </main>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { obtenerEstadoBackend } from '../services/api'
import '../assets/styles/HomeView.css'

const connected = ref(false)
const status = ref('Esperando conexión con el backend Python…')
let mounted = true

async function connectBackend() {
  try {
    const response = await obtenerEstadoBackend()
    if (mounted) {
      connected.value = true
      status.value = response.message
    }
  } catch (error) {
    if (mounted) {
      status.value = error.message
    }
  }
}

onMounted(() => {
  window.addEventListener('pywebviewready', connectBackend, { once: true })
  if (window.pywebview?.api) {
    connectBackend()
  }
})

onUnmounted(() => {
  mounted = false
  window.removeEventListener('pywebviewready', connectBackend)
})
</script>

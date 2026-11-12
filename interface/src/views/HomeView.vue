<template>
  <main class="file-manager">
    <header class="app-header">
      <div>
        <p class="eyebrow">GESTOR DE ARCHIVOS</p>
        <h1>Explorador</h1>
      </div>
      <div class="connection-state" :class="{ connected }" role="status" aria-live="polite">
        <span class="connection-dot" aria-hidden="true"></span>
        {{ connected ? 'Conectado' : 'Esperando a Python' }}
      </div>
    </header>

    <section class="workspace" aria-label="Explorador de archivos">
      <div class="toolbar" aria-label="Acciones de archivos">
        <button type="button" :disabled="!connected || busy" @click="openCreateDialog('folder')">
          Nueva carpeta
        </button>
        <button type="button" :disabled="!connected || busy" @click="openCreateDialog('file')">
          Nuevo archivo .txt
        </button>
        <span class="toolbar-divider" aria-hidden="true"></span>
        <button
          type="button"
          :disabled="!connected || !canEdit || busy"
          @click="openEditor"
        >
          Abrir / editar
        </button>
        <button
          type="button"
          :disabled="!connected || !canEdit || busy"
          @click="openAppendDialog"
        >
          Agregar información
        </button>
        <span class="toolbar-spacer"></span>
        <button
          type="button"
          class="icon-button"
          aria-label="Subir una carpeta"
          :disabled="!connected || !currentPath || busy"
          @click="navigateUp"
        >
          ↑
        </button>
        <button
          type="button"
          class="icon-button"
          aria-label="Actualizar"
          :disabled="!connected || busy"
          @click="loadDirectory()"
        >
          ↻
        </button>
      </div>

      <nav class="breadcrumbs" aria-label="Ruta actual">
        <button type="button" :disabled="!connected" @click="navigateTo('')">
          directory
        </button>
        <template v-for="(segment, index) in pathSegments" :key="index">
          <span aria-hidden="true">›</span>
          <button
            type="button"
            :disabled="!connected"
            @click="navigateTo(pathSegments.slice(0, index + 1).join('/'))"
          >
            {{ segment }}
          </button>
        </template>
      </nav>

      <div v-if="errorMessage" class="message error-message" role="alert">
        <span>{{ errorMessage }}</span>
        <button type="button" aria-label="Cerrar error" @click="errorMessage = ''">×</button>
      </div>
      <div v-if="successMessage" class="message success-message" role="status">
        {{ successMessage }}
      </div>

      <div class="file-list" role="table" aria-label="Contenido de la carpeta">
        <div class="file-row file-header" role="row">
          <span role="columnheader">Nombre</span>
          <span role="columnheader">Tipo</span>
          <span role="columnheader">Tamaño</span>
          <span role="columnheader">Modificado</span>
        </div>
        <button
          v-for="item in entries"
          :key="item.path"
          type="button"
          class="file-row file-entry"
          :class="{ selected: selectedPath === item.path }"
          :disabled="busy"
          role="row"
          :aria-label="`${item.type === 'directory' ? 'Carpeta' : 'Archivo'} ${item.name}`"
          @click="selectItem(item)"
          @dblclick="openItem(item)"
        >
          <span class="file-name" role="cell">
            <span class="file-icon" aria-hidden="true">{{ iconFor(item) }}</span>
            <span>{{ item.name }}</span>
          </span>
          <span role="cell">{{ typeLabel(item) }}</span>
          <span role="cell">{{ item.type === 'file' ? formatSize(item.size) : '—' }}</span>
          <span role="cell">{{ formatDate(item.modified) }}</span>
        </button>
        <div v-if="!entries.length && connected && !busy" class="empty-state">
          <span class="empty-icon" aria-hidden="true">📁</span>
          <strong>Esta carpeta está vacía</strong>
          <span>Crea una carpeta o un archivo .txt para comenzar.</span>
        </div>
        <div v-if="!connected" class="empty-state">
          <strong>Conecta el backend de Python</strong>
          <span>Inicia Vite y ejecuta <code>python init.py</code> en otra terminal.</span>
        </div>
        <div v-if="busy" class="loading-state" role="status">Procesando…</div>
      </div>

      <footer class="selection-bar">
        <span v-if="selectedItem">
          Seleccionado: <strong>{{ selectedItem.name }}</strong>
        </span>
        <span v-else>
          Doble clic para abrir · {{ entries.length }} elemento(s)
        </span>
        <div class="selection-actions">
          <button
            type="button"
            :disabled="!connected || !isSelectedFile || busy"
            @click="openRenameDialog"
          >
            Renombrar
          </button>
          <button
            type="button"
            :disabled="!connected || !isSelectedFile || busy"
            @click="openCopyDialog"
          >
            Copiar
          </button>
          <button
            type="button"
            class="danger-button"
            :disabled="!connected || !isSelectedFile || busy"
            @click="deleteSelected"
          >
            Eliminar
          </button>
          <button
            type="button"
            :disabled="!connected || !isSelectedFile || busy"
            @click="showInformation"
          >
            Información
          </button>
        </div>
      </footer>
    </section>

    <div v-if="dialog" class="modal-backdrop" @click.self="closeDialog">
      <section class="modal" role="dialog" aria-modal="true" :aria-labelledby="`${dialog.kind}-title`">
        <h2 :id="`${dialog.kind}-title`">{{ dialog.title }}</h2>
        <p v-if="dialog.description" class="modal-description">{{ dialog.description }}</p>
        <form @submit.prevent="submitDialog">
          <label :for="`${dialog.kind}-input`">{{ dialog.label }}</label>
          <p v-if="errorMessage" class="dialog-error" role="alert">{{ errorMessage }}</p>
          <textarea
            v-if="dialog.multiline"
            :id="`${dialog.kind}-input`"
            v-model="dialog.value"
            rows="6"
            autofocus
            required
          ></textarea>
          <input
            v-else
            :id="`${dialog.kind}-input`"
            v-model="dialog.value"
            type="text"
            autocomplete="off"
            autofocus
            required
          >
          <div class="modal-actions">
            <button type="button" @click="closeDialog">Cancelar</button>
            <button type="submit" class="primary-button" :disabled="busy">
              {{ dialog.submitLabel || 'Continuar' }}
            </button>
          </div>
        </form>
      </section>
    </div>

    <div v-if="editorOpen" class="modal-backdrop" @click.self="closeEditor">
      <section class="editor-window" role="dialog" aria-modal="true" aria-labelledby="editor-title">
        <header class="editor-header">
          <div>
            <p class="eyebrow">BLOC DE NOTAS</p>
            <h2 id="editor-title">{{ editorPath }}</h2>
          </div>
          <button type="button" class="icon-button" aria-label="Cerrar editor" @click="closeEditor">
            ×
          </button>
        </header>
        <textarea
          v-model="editorContent"
          class="editor-content"
          aria-label="Contenido del archivo de texto"
          spellcheck="false"
        ></textarea>
        <p v-if="errorMessage" class="dialog-error editor-error" role="alert">
          {{ errorMessage }}
        </p>
        <footer class="editor-footer">
          <span>{{ editorDirty ? 'Cambios sin guardar' : 'Todos los cambios guardados' }}</span>
          <div>
            <button type="button" @click="closeEditor">Cerrar</button>
            <button
              type="button"
              class="primary-button"
              :disabled="busy || !editorDirty"
              @click="saveEditor"
            >
              Guardar
            </button>
          </div>
        </footer>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  agregarInformacion,
  copiarArchivo,
  crearArchivoTexto,
  crearDirectorio,
  eliminarArchivo,
  guardarArchivo,
  leerArchivo,
  listarDirectorio,
  obtenerEstadoBackend,
  obtenerInformacion,
  renombrarArchivo,
} from '../services/api'
import '../assets/styles/HomeView.css'

const connected = ref(false)
const busy = ref(false)
const currentPath = ref('')
const entries = ref([])
const selectedPath = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const dialog = ref(null)
const editorOpen = ref(false)
const editorPath = ref('')
const editorContent = ref('')
const savedContent = ref('')
let mounted = true
let successTimer

const pathSegments = computed(() => currentPath.value.split('/').filter(Boolean))
const selectedItem = computed(
  () => entries.value.find((item) => item.path === selectedPath.value) || null,
)
const isSelectedFile = computed(() => selectedItem.value?.type === 'file')
const canEdit = computed(
  () => isSelectedFile.value && selectedItem.value.name.toLowerCase().endsWith('.txt'),
)
const editorDirty = computed(() => editorContent.value !== savedContent.value)

function showSuccess(message) {
  successMessage.value = message
  window.clearTimeout(successTimer)
  successTimer = window.setTimeout(() => {
    successMessage.value = ''
  }, 3500)
}

async function perform(operation) {
  if (busy.value) return null
  busy.value = true
  errorMessage.value = ''
  try {
    return await operation()
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : 'Ocurrió un error inesperado.'
    return null
  } finally {
    busy.value = false
  }
}

async function loadDirectory(path = currentPath.value) {
  const result = await perform(() => listarDirectorio(path))
  if (result) {
    currentPath.value = path
    entries.value = result
    selectedPath.value = ''
  }
}

async function connectBackend() {
  const result = await perform(async () => {
    const response = await obtenerEstadoBackend()
    return response
  })
  if (result && mounted) {
    connected.value = true
    await loadDirectory('')
  }
}

function navigateTo(path) {
  loadDirectory(path)
}

function navigateUp() {
  navigateTo(pathSegments.value.slice(0, -1).join('/'))
}

function selectItem(item) {
  selectedPath.value = item.path
}

function openItem(item) {
  if (item.type === 'directory') {
    navigateTo(item.path)
  } else if (item.type === 'file' && item.name.toLowerCase().endsWith('.txt')) {
    selectedPath.value = item.path
    openEditor()
  } else {
    selectedPath.value = item.path
  }
}

function iconFor(item) {
  if (item.type === 'directory') return '📁'
  if (item.type === 'link') return '↗'
  return item.name.toLowerCase().endsWith('.txt') ? '📝' : '📄'
}

function typeLabel(item) {
  if (item.type === 'directory') return 'Carpeta'
  if (item.type === 'link') return 'Enlace no compatible'
  return item.name.toLowerCase().endsWith('.txt') ? 'Documento de texto' : 'Archivo'
}

function formatSize(bytes) {
  if (bytes === null || bytes === undefined) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString()
}

function openCreateDialog(kind) {
  errorMessage.value = ''
  const isFolder = kind === 'folder'
  dialog.value = {
    kind,
    title: isFolder ? 'Crear carpeta' : 'Crear archivo de texto',
    label: isFolder ? 'Nombre de la carpeta' : 'Nombre del archivo (.txt)',
    value: '',
    submitLabel: 'Crear',
  }
}

function openRenameDialog() {
  if (!isSelectedFile.value) return
  errorMessage.value = ''
  dialog.value = {
    kind: 'rename',
    title: 'Renombrar archivo',
    label: 'Nuevo nombre',
    value: selectedItem.value.name,
    submitLabel: 'Renombrar',
  }
}

function openCopyDialog() {
  if (!isSelectedFile.value) return
  errorMessage.value = ''
  const parent = selectedItem.value.path.includes('/')
    ? `${selectedItem.value.path.slice(0, selectedItem.value.path.lastIndexOf('/') + 1)}`
    : ''
  const extension = selectedItem.value.name.includes('.')
    ? `.${selectedItem.value.name.split('.').pop()}`
    : ''
  const stem = extension ? selectedItem.value.name.slice(0, -extension.length) : selectedItem.value.name
  dialog.value = {
    kind: 'copy',
    title: 'Copiar archivo',
    description: 'Escribe la ruta de destino dentro de directory.',
    label: 'Ruta nueva (relativa a directory)',
    value: `${parent}${stem} - copia${extension}`,
    submitLabel: 'Copiar',
  }
}

function openAppendDialog() {
  if (!canEdit.value) return
  errorMessage.value = ''
  dialog.value = {
    kind: 'append',
    title: 'Agregar información',
    description: `El texto se agregará al final de ${selectedItem.value.name}.`,
    label: 'Información para agregar',
    value: '',
    multiline: true,
    submitLabel: 'Agregar',
  }
}

function closeDialog() {
  if (!busy.value) dialog.value = null
}

async function submitDialog() {
  if (!dialog.value || busy.value) return
  const currentDialog = { ...dialog.value }
  const value = currentDialog.value.trim()
  if (!value) {
    errorMessage.value =
      currentDialog.kind === 'append'
        ? 'Escribe la información que quieres agregar.'
        : 'Indica un nombre o una ruta de destino.'
    return
  }
  let result

  if (currentDialog.kind === 'folder') {
    result = await perform(() => crearDirectorio(currentPath.value, value))
    if (result) showSuccess('Carpeta creada.')
  } else if (currentDialog.kind === 'file') {
    const fileName = value.toLowerCase().endsWith('.txt') ? value : `${value}.txt`
    result = await perform(() => crearArchivoTexto(currentPath.value, fileName))
    if (result) showSuccess('Archivo de texto creado.')
  } else if (currentDialog.kind === 'rename') {
    result = await perform(() => renombrarArchivo(selectedPath.value, value))
    if (result) showSuccess('Archivo renombrado.')
  } else if (currentDialog.kind === 'copy') {
    result = await perform(() => copiarArchivo(selectedPath.value, value))
    if (result) showSuccess('Archivo copiado.')
  } else if (currentDialog.kind === 'append') {
    result = await perform(() => agregarInformacion(selectedPath.value, currentDialog.value))
    if (result) showSuccess('Información agregada.')
  }

  if (result) {
    dialog.value = null
    await loadDirectory()
  }
}

async function deleteSelected() {
  if (!isSelectedFile.value || busy.value) return
  const confirmed = window.confirm(`¿Eliminar "${selectedItem.value.name}"? Esta acción no se puede deshacer.`)
  if (!confirmed) return
  const result = await perform(() => eliminarArchivo(selectedPath.value))
  if (result) {
    showSuccess('Archivo eliminado.')
    await loadDirectory()
  }
}

async function openEditor() {
  if (!canEdit.value || busy.value) return
  const result = await perform(() => leerArchivo(selectedPath.value))
  if (result) {
    editorPath.value = result.path
    editorContent.value = result.content
    savedContent.value = result.content
    editorOpen.value = true
  }
}

async function saveEditor() {
  if (!editorOpen.value || !editorDirty.value || busy.value) return
  const result = await perform(() => guardarArchivo(editorPath.value, editorContent.value))
  if (result) {
    savedContent.value = editorContent.value
    showSuccess('Cambios guardados.')
    await loadDirectory()
  }
}

function closeEditor() {
  if (busy.value) return
  if (editorDirty.value && !window.confirm('Hay cambios sin guardar. ¿Cerrar sin guardar?')) {
    return
  }
  editorOpen.value = false
}

async function showInformation() {
  if (!isSelectedFile.value) return
  const result = await perform(() => obtenerInformacion(selectedPath.value))
  if (result) {
    const message = `Nombre: ${result.name}\nTamaño: ${formatSize(result.size)}\nModificado: ${formatDate(result.modified)}`
    window.alert(message)
  }
}

onMounted(() => {
  if (window.pywebview?.api) {
    connectBackend()
  } else {
    window.addEventListener('pywebviewready', connectBackend, { once: true })
  }
})

onUnmounted(() => {
  mounted = false
  window.clearTimeout(successTimer)
  window.removeEventListener('pywebviewready', connectBackend)
})
</script>

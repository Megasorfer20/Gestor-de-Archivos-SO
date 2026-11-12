function obtenerApiEscritorio() {
  const api = window.pywebview?.api
  if (!api) {
    throw new Error('Backend no disponible. Inicia la aplicación desde Python.')
  }
  return api
}

async function invocar(metodo, ...argumentos) {
  const api = obtenerApiEscritorio()
  if (typeof api[metodo] !== 'function') {
    throw new Error(`El método ${metodo} no está disponible en el backend.`)
  }
  const response = await api[metodo](...argumentos)
  if (!response?.success) {
    throw new Error(response?.message || 'No se pudo completar la operación.')
  }
  return response
}

export async function obtenerEstadoBackend() {
  return invocar('obtener_estado')
}

export async function listarDirectorio(ruta = '') {
  return (await invocar('listar_directorio', ruta)).data
}

export async function listarCarpetas() {
  return (await invocar('listar_carpetas')).data
}

export async function crearDirectorio(directorio, nombre) {
  return (await invocar('crear_directorio', directorio, nombre)).data
}

export async function crearArchivoTexto(directorio, nombre) {
  return (await invocar('crear_archivo_texto', directorio, nombre)).data
}

export async function leerArchivo(ruta) {
  return (await invocar('leer_archivo', ruta)).data
}

export async function guardarArchivo(ruta, contenido) {
  return (await invocar('guardar_archivo', ruta, contenido)).data
}

export async function agregarInformacion(ruta, contenido) {
  return (await invocar('agregar_informacion', ruta, contenido)).data
}

export async function renombrarArchivo(ruta, nuevoNombre) {
  return (await invocar('renombrar_archivo', ruta, nuevoNombre)).data
}

export async function copiarArchivo(ruta, rutaDestino) {
  return (await invocar('copiar_archivo', ruta, rutaDestino)).data
}

export async function eliminarArchivo(ruta) {
  return (await invocar('eliminar_archivo', ruta, true)).data
}

export async function obtenerInformacion(ruta) {
  return (await invocar('obtener_informacion', ruta)).data
}

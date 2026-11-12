function obtenerApiEscritorio() {
  const api = window.pywebview?.api
  if (!api) {
    throw new Error('Backend no disponible. Inicia la aplicación desde Python.')
  }
  return api
}

export async function obtenerEstadoBackend() {
  const api = obtenerApiEscritorio()
  if (typeof api.obtener_estado !== 'function') {
    throw new Error('El método obtener_estado no está disponible en el backend.')
  }

  const response = await api.obtener_estado()
  if (!response?.success) {
    throw new Error(response?.message || 'El backend no pudo iniciar.')
  }
  return response
}

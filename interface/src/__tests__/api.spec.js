import { afterEach, describe, expect, it, vi } from 'vitest'
import { obtenerEstadoBackend } from '../services/api'

afterEach(() => {
  delete window.pywebview
})

describe('servicio de API de escritorio', () => {
  it('informa si la API de pywebview no está disponible', async () => {
    await expect(obtenerEstadoBackend()).rejects.toThrow('Backend no disponible')
  })

  it('consulta el estado del backend', async () => {
    const obtenerEstado = vi.fn().mockResolvedValue({
      success: true,
      message: 'Backend conectado.',
    })
    window.pywebview = { api: { obtener_estado: obtenerEstado } }

    await expect(obtenerEstadoBackend()).resolves.toEqual({
      success: true,
      message: 'Backend conectado.',
    })
    expect(obtenerEstado).toHaveBeenCalledOnce()
  })

  it('propaga errores de inicialización del backend', async () => {
    window.pywebview = {
      api: {
        obtener_estado: vi.fn().mockResolvedValue({
          success: false,
          message: 'Backend detenido.',
        }),
      },
    }

    await expect(obtenerEstadoBackend()).rejects.toThrow('Backend detenido.')
  })
})

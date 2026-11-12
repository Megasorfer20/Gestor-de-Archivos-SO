import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  agregarInformacion,
  copiarArchivo,
  crearArchivoTexto,
  crearDirectorio,
  eliminarArchivo,
  guardarArchivo,
  leerArchivo,
  listarCarpetas,
  listarDirectorio,
  obtenerEstadoBackend,
  obtenerInformacion,
  renombrarArchivo,
} from '../services/api'

afterEach(() => {
  delete window.pywebview
})

describe('servicio de API de escritorio', () => {
  it('informa si la API de pywebview no está disponible', async () => {
    await expect(obtenerEstadoBackend()).rejects.toThrow('Backend no disponible')
  })

  it('invoca las operaciones con sus argumentos y entrega los datos', async () => {
    const data = { path: 'nota.txt' }
    const api = Object.fromEntries(
      [
        'obtener_estado',
        'listar_directorio',
        'listar_carpetas',
        'crear_directorio',
        'crear_archivo_texto',
        'leer_archivo',
        'guardar_archivo',
        'agregar_informacion',
        'renombrar_archivo',
        'copiar_archivo',
        'eliminar_archivo',
        'obtener_informacion',
      ].map((method) => [method, vi.fn().mockResolvedValue({ success: true, data })]),
    )
    api.obtener_estado.mockResolvedValue({
      success: true,
      message: 'Conectado.',
      data,
    })
    window.pywebview = { api }

    await expect(obtenerEstadoBackend()).resolves.toMatchObject({ message: 'Conectado.' })
    await expect(listarDirectorio('Documentos')).resolves.toEqual(data)
    await expect(listarCarpetas()).resolves.toEqual(data)
    await crearDirectorio('', 'Documentos')
    await crearArchivoTexto('Documentos', 'nota.txt')
    await leerArchivo('Documentos/nota.txt')
    await guardarArchivo('Documentos/nota.txt', 'texto')
    await agregarInformacion('Documentos/nota.txt', 'más texto')
    await renombrarArchivo('Documentos/nota.txt', 'renombrada.txt')
    await copiarArchivo('Documentos/nota.txt', 'Documentos/copia.txt')
    await eliminarArchivo('Documentos/nota.txt')
    await obtenerInformacion('Documentos/nota.txt')

    expect(api.listar_directorio).toHaveBeenCalledWith('Documentos')
    expect(api.listar_carpetas).toHaveBeenCalledOnce()
    expect(api.crear_directorio).toHaveBeenCalledWith('', 'Documentos')
    expect(api.crear_archivo_texto).toHaveBeenCalledWith('Documentos', 'nota.txt')
    expect(api.leer_archivo).toHaveBeenCalledWith('Documentos/nota.txt')
    expect(api.guardar_archivo).toHaveBeenCalledWith('Documentos/nota.txt', 'texto')
    expect(api.agregar_informacion).toHaveBeenCalledWith(
      'Documentos/nota.txt',
      'más texto',
    )
    expect(api.renombrar_archivo).toHaveBeenCalledWith(
      'Documentos/nota.txt',
      'renombrada.txt',
    )
    expect(api.copiar_archivo).toHaveBeenCalledWith(
      'Documentos/nota.txt',
      'Documentos/copia.txt',
    )
    expect(api.eliminar_archivo).toHaveBeenCalledWith('Documentos/nota.txt', true)
    expect(api.obtener_informacion).toHaveBeenCalledWith('Documentos/nota.txt')
  })

  it('propaga errores comunicados por el backend', async () => {
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

  it('informa cuando un método no está disponible', async () => {
    window.pywebview = { api: {} }
    await expect(listarDirectorio()).rejects.toThrow('listar_directorio no está disponible')
  })
})

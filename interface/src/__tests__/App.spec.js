import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import HomeView from '../views/HomeView.vue'
import {
  crearArchivoTexto,
  crearDirectorio,
  copiarArchivo,
  guardarArchivo,
  leerArchivo,
  listarCarpetas,
  listarDirectorio,
  obtenerEstadoBackend,
  renombrarArchivo,
} from '../services/api'

vi.mock('../services/api', () => ({
  agregarInformacion: vi.fn(),
  copiarArchivo: vi.fn(),
  crearArchivoTexto: vi.fn(),
  crearDirectorio: vi.fn(),
  eliminarArchivo: vi.fn(),
  guardarArchivo: vi.fn(),
  leerArchivo: vi.fn(),
  listarCarpetas: vi.fn(),
  listarDirectorio: vi.fn(),
  obtenerEstadoBackend: vi.fn(),
  obtenerInformacion: vi.fn(),
  renombrarArchivo: vi.fn(),
}))

describe('explorador de archivos', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    delete window.pywebview
    vi.mocked(listarDirectorio).mockResolvedValue([])
    vi.mocked(obtenerEstadoBackend).mockResolvedValue({
      success: true,
      message: 'Gestor de archivos conectado.',
    })
  })

  it('muestra la carpeta de trabajo y espera la conexión de escritorio', () => {
    const wrapper = mount(HomeView)

    expect(wrapper.text()).toContain('Explorador')
    expect(wrapper.text()).toContain('directory')
    expect(wrapper.text()).toContain('Conecta el backend de Python')
    expect(wrapper.get('button[aria-label="Actualizar"]').element.disabled).toBe(true)
    wrapper.unmount()
  })

  it('conecta al backend y carga la carpeta raíz', async () => {
    window.pywebview = { api: {} }
    const wrapper = mount(HomeView)
    await flushPromises()

    expect(obtenerEstadoBackend).toHaveBeenCalledOnce()
    expect(listarDirectorio).toHaveBeenCalledWith('')
    expect(wrapper.get('[role="status"]').text()).toContain('Conectado')
    expect(wrapper.text()).toContain('Esta carpeta está vacía')
    wrapper.unmount()
  })

  it('crea carpetas y archivos .txt en la ubicación actual', async () => {
    window.pywebview = { api: {} }
    vi.mocked(crearDirectorio).mockResolvedValue({ path: 'Informes' })
    vi.mocked(crearArchivoTexto).mockResolvedValue({ path: 'reporte.txt' })
    const wrapper = mount(HomeView)
    await flushPromises()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nueva carpeta'))
      .trigger('click')
    await wrapper.get('input').setValue('Informes')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(crearDirectorio).toHaveBeenCalledWith('', 'Informes')
    expect(wrapper.text()).toContain('Carpeta creada.')

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nuevo archivo .txt'))
      .trigger('click')
    await wrapper.get('input').setValue('reporte')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(crearArchivoTexto).toHaveBeenCalledWith('', 'reporte.txt')
    wrapper.unmount()
  })

  it('muestra un error cuando se intenta crear con un nombre vacío', async () => {
    window.pywebview = { api: {} }
    const wrapper = mount(HomeView)
    await flushPromises()
    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nueva carpeta'))
      .trigger('click')
    await wrapper.get('input').setValue('   ')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.get('[role="alert"]').text()).toContain('Indica un nombre')
    expect(crearDirectorio).not.toHaveBeenCalled()
    wrapper.unmount()
  })

  it('abre y guarda un archivo de texto en el editor', async () => {
    window.pywebview = { api: {} }
    vi.mocked(listarDirectorio).mockResolvedValue([
      {
        name: 'notas.txt',
        path: 'notas.txt',
        type: 'file',
        size: 4,
        modified: '2026-01-01T10:00:00',
      },
    ])
    vi.mocked(leerArchivo).mockResolvedValue({ path: 'notas.txt', content: 'Hola' })
    vi.mocked(guardarArchivo).mockResolvedValue({ path: 'notas.txt' })

    const wrapper = mount(HomeView)
    await flushPromises()
    await wrapper.get('.file-entry').trigger('dblclick')
    await flushPromises()

    expect(leerArchivo).toHaveBeenCalledWith('notas.txt')
    await wrapper.get('.editor-content').setValue('Hola mundo')
    await wrapper.get('.editor-footer .primary-button').trigger('click')
    await flushPromises()

    expect(guardarArchivo).toHaveBeenCalledWith('notas.txt', 'Hola mundo')
    expect(wrapper.text()).toContain('Cambios guardados.')
    wrapper.unmount()
  })

  it('copia archivos a una carpeta distinta dentro de directory', async () => {
    window.pywebview = { api: {} }
    vi.mocked(listarDirectorio).mockResolvedValue([
      {
        name: 'notas.txt',
        path: 'notas.txt',
        type: 'file',
        size: 4,
        modified: '2026-01-01T10:00:00',
      },
    ])
    vi.mocked(listarCarpetas).mockResolvedValue([
      { path: '', name: 'directory (raíz)' },
      { path: 'test', name: 'test' },
    ])
    vi.mocked(copiarArchivo).mockResolvedValue({ path: 'test/notas - copia.txt' })

    const wrapper = mount(HomeView)
    await flushPromises()
    await wrapper.get('.file-entry').trigger('click')
    await wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'Copiar')
      .trigger('click')
    await flushPromises()
    await wrapper.get('#copy-folder').setValue('test')
    await wrapper.get('#copy-input').setValue('notas - copia')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(copiarArchivo).toHaveBeenCalledWith(
      'notas.txt',
      'test/notas - copia.txt',
    )
    expect(listarDirectorio).toHaveBeenLastCalledWith('test')
    wrapper.unmount()
  })

  it('renombra un archivo conservando su extensión fija', async () => {
    window.pywebview = { api: {} }
    vi.mocked(listarDirectorio).mockResolvedValue([
      {
        name: 'notas.txt',
        path: 'notas.txt',
        type: 'file',
        size: 4,
        modified: '2026-01-01T10:00:00',
      },
    ])
    vi.mocked(renombrarArchivo).mockResolvedValue({ path: 'diario.txt' })

    const wrapper = mount(HomeView)
    await flushPromises()
    await wrapper.get('.file-entry').trigger('click')
    await wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'Renombrar')
      .trigger('click')
    await wrapper.get('#rename-input').setValue('diario')
    expect(wrapper.get('.fixed-extension').text()).toBe('.txt')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(renombrarArchivo).toHaveBeenCalledWith('notas.txt', 'diario.txt')
    wrapper.unmount()
  })

  it('inserta tabulación en la posición del cursor del editor', async () => {
    window.pywebview = { api: {} }
    vi.mocked(listarDirectorio).mockResolvedValue([
      {
        name: 'notas.txt',
        path: 'notas.txt',
        type: 'file',
        size: 4,
        modified: '2026-01-01T10:00:00',
      },
    ])
    vi.mocked(leerArchivo).mockResolvedValue({ path: 'notas.txt', content: 'Hola' })

    const wrapper = mount(HomeView)
    await flushPromises()
    await wrapper.get('.file-entry').trigger('dblclick')
    await flushPromises()
    const editor = wrapper.get('.editor-content')
    await editor.setValue('ab')
    editor.element.setSelectionRange(1, 1)
    await editor.trigger('keydown', { key: 'Tab' })

    expect(editor.element.value).toBe('a\tb')
    expect(editor.element.selectionStart).toBe(2)
    expect(editor.element.selectionEnd).toBe(2)
    wrapper.unmount()
  })

  it('presenta errores del backend sin romper la interfaz', async () => {
    window.pywebview = { api: {} }
    vi.mocked(obtenerEstadoBackend).mockRejectedValue(new Error('Servicio no disponible.'))

    const wrapper = mount(HomeView)
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain('Servicio no disponible.')
    expect(wrapper.find('main').exists()).toBe(true)
    wrapper.unmount()
  })
})

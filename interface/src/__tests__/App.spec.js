import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import HomeView from '../views/HomeView.vue'
import { obtenerEstadoBackend } from '../services/api'

vi.mock('../services/api', () => ({
  obtenerEstadoBackend: vi.fn(),
}))

describe('pantalla inicial', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    delete window.pywebview
  })

  it('muestra la plantilla vacía sin funcionalidades anteriores', () => {
    const wrapper = mount(HomeView)

    expect(wrapper.get('h1').text()).toBe('Plantilla de proyecto')
    expect(wrapper.text()).toContain('Esperando conexión con el backend Python')
    expect(wrapper.find('form').exists()).toBe(false)
    wrapper.unmount()
  })

  it('muestra el estado recibido del backend de escritorio', async () => {
    window.pywebview = { api: {} }
    vi.mocked(obtenerEstadoBackend).mockResolvedValue({
      success: true,
      message: 'Backend conectado.',
    })

    const wrapper = mount(HomeView)
    await flushPromises()

    expect(obtenerEstadoBackend).toHaveBeenCalledOnce()
    expect(wrapper.get('[role="status"]').text()).toBe('Backend conectado.')
    expect(wrapper.get('[role="status"]').classes()).toContain('connected')
    wrapper.unmount()
  })
})

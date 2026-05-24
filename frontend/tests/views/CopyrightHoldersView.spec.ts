import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CopyrightHoldersView from '@/views/CopyrightHoldersView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getCopyrightHoldersDirect: vi.fn(),
    getContent: vi.fn(),
    createCopyrightHolder: vi.fn(),
    updateCopyrightHolder: vi.fn(),
    deleteCopyrightHolder: vi.fn()
  }
}))

describe('Компонент CopyrightHoldersView.vue', () => {
  const globalOptions = {
    stubs: {
      DataTable: true,
      Pagination: true
    }
  }

  const mockHolder = {
    copyright_holder_id: 1,
    copyright_holder_name: 'Студия А',
    copyright_holder_phone: '123456789',
    copyright_holder_email: 'studio@mail.com'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Загружает и отображает список правообладателей', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValueOnce({
      items: [mockHolder],
      total: 1,
      page: 1,
      pages: 1
    } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getCopyrightHoldersDirect).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает боковую панель для нового правообладателя', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()

    expect(wrapper.find('.side-panel').classes()).not.toContain('open')

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    expect(wrapper.find('.side-panel').classes()).toContain('open')
  })

  it('Не вызывает API удаления, если пользователь нажал Отмена', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValueOnce({ items: [mockHolder], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    window.confirm = vi.fn(() => false)

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockHolder)
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteCopyrightHolder).not.toHaveBeenCalled()
  })

  it('Вызывает API удаления при подтверждении и перезагружает данные', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValue({ items: [mockHolder], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValue({ items: [] } as any)
    window.confirm = vi.fn(() => true)

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()
    
    vi.clearAllMocks()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockHolder)
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteCopyrightHolder).toHaveBeenCalledWith(1)
    expect(ApiService.getCopyrightHoldersDirect).toHaveBeenCalled()
  })

  it('Показывает alert при ошибке удаления', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValueOnce({ items: [mockHolder], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.deleteCopyrightHolder).mockRejectedValueOnce(new Error('Ошибка удаления'))
    window.confirm = vi.fn(() => true)

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockHolder)
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка удаления')
  })

  it('Показывает alert при ошибке сохранения', async () => {
    vi.mocked(ApiService.getCopyrightHoldersDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.createCopyrightHolder).mockRejectedValueOnce(new Error('Ошибка сохранения'))

    const wrapper = mount(CopyrightHoldersView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка сохранения')
  })
})
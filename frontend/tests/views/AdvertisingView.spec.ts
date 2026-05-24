import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdvertisingView from '@/views/AdvertisingView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getAdvertising: vi.fn(),
    getContent: vi.fn(),
    getTagsDirect: vi.fn(),
    createAdvertising: vi.fn(),
    updateAdvertising: vi.fn(),
    deleteAdvertising: vi.fn()
  }
}))

describe('Компонент AdvertisingView.vue', () => {
  const globalOptions = {
    stubs: {
      DataTable: true,
      Pagination: true,
      Modal: true
    }
  }

  const mockAd = {
    advertising_id: 1,
    advertising_name: 'Реклама 1',
    advertising_duration: '00:00:15',
    advertising_owner: 'Спонсор',
    advertising_start_date: '2023-01-01',
    advertising_finish_date: '2023-12-31',
    is_active: true
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Загружает и отображает список рекламы', async () => {
    vi.mocked(ApiService.getAdvertising).mockResolvedValueOnce({
      items: [mockAd],
      total: 1,
      page: 1,
      pages: 1
    } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)

    const wrapper = mount(AdvertisingView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getAdvertising).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает модальное окно добавления рекламы', async () => {
    vi.mocked(ApiService.getAdvertising).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)

    const wrapper = mount(AdvertisingView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent({ name: 'Modal' })
    expect(modal.props('show')).toBe(true)
  })

  it('Не удаляет рекламу, если действие отменено', async () => {
    vi.mocked(ApiService.getAdvertising).mockResolvedValueOnce({ items: [mockAd], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [] } as any)
    window.confirm = vi.fn(() => false)

    const wrapper = mount(AdvertisingView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockAd)
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteAdvertising).not.toHaveBeenCalled()
  })

  it('Выводит alert при ошибке удаления', async () => {
    vi.mocked(ApiService.getAdvertising).mockResolvedValueOnce({ items: [mockAd], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.deleteAdvertising).mockRejectedValueOnce(new Error('Ошибка удаления'))
    window.confirm = vi.fn(() => true)

    const wrapper = mount(AdvertisingView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockAd)
    await flushPromises()

    expect(ApiService.deleteAdvertising).toHaveBeenCalledWith(1)
    expect(window.alert).toHaveBeenCalledWith('Ошибка удаления')
  })
})
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContentView from '@/views/ContentView.vue'
import { ApiService } from '@/services/api'
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/', component: { template: '<div></div>' } }]
})

vi.mock('@/services/api', () => ({
  ApiService: {
    getContent: vi.fn(),
    getGenres: vi.fn(),
    getTags: vi.fn(),
    getCopyrightHolders: vi.fn(),
    createContent: vi.fn(),
    updateContent: vi.fn(),
    deleteContent: vi.fn()
  }
}))

describe('Компонент ContentView.vue', () => {
  const globalOptions = {
    plugins: [router],
    stubs: {
      DataTable: true,
      Pagination: true,
      Modal: true
    }
  }

  const mockContent = {
    items: [
      {
        content_id: 1,
        content_name: 'Фильм 1',
        content_type: 'Фильм',
        content_duration: '02:00:00',
        content_publish_date: '2023-01-01',
        genres: [{ genre_id: 1, genre_name: 'Драма' }],
        tags: [{ tag_id: 1, tag_name: 'Новинка' }],
        copyright_holders: [{ copyright_holder_id: 1, copyright_holder_name: 'Студия А' }]
      }
    ],
    total: 1,
    page: 1,
    pages: 1
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Загружает списки для фильтров и таблицу контента при монтировании', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getCopyrightHolders).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce(mockContent as any)

    const wrapper = mount(ContentView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getGenres).toHaveBeenCalled()
    expect(ApiService.getTags).toHaveBeenCalled()
    expect(ApiService.getCopyrightHolders).toHaveBeenCalled()
    expect(ApiService.getContent).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает модальное окно для создания контента', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getCopyrightHolders).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)

    const wrapper = mount(ContentView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent({ name: 'Modal' })
    expect(modal.props('show')).toBe(true)
    expect(modal.props('title')).toBe('Новый контент')
  })

  it('Не вызывает API удаления, если пользователь нажал Отмена', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getCopyrightHolders).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce(mockContent as any)
    window.confirm = vi.fn(() => false)

    const wrapper = mount(ContentView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockContent.items[0])
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteContent).not.toHaveBeenCalled()
  })

  it('Вызывает API удаления при подтверждении и перезагружает данные', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValue([])
    vi.mocked(ApiService.getTags).mockResolvedValue([])
    vi.mocked(ApiService.getCopyrightHolders).mockResolvedValue([])
    vi.mocked(ApiService.getContent).mockResolvedValue(mockContent as any)
    window.confirm = vi.fn(() => true)

    const wrapper = mount(ContentView, { global: globalOptions })
    await flushPromises()
    
    vi.clearAllMocks()
    
    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockContent.items[0])
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteContent).toHaveBeenCalledWith(1)
    expect(ApiService.getContent).toHaveBeenCalled()
  })

  it('Показывает alert при ошибке загрузки данных', async () => {
    vi.mocked(ApiService.getGenres).mockRejectedValueOnce(new Error('Ошибка сети'))
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getCopyrightHolders).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce(mockContent as any)

    mount(ContentView, { global: globalOptions })
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка сети')
  })
})
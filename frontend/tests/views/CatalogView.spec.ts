import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CatalogView from '@/views/CatalogView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getGenres: vi.fn(),
    getTags: vi.fn(),
    getContent: vi.fn(),
    getContentAdvertising: vi.fn(),
    getContentProgress: vi.fn()
  }
}))

describe('Компонент CatalogView.vue', () => {
  const globalOptions = {
    stubs: {
      Pagination: true
    }
  }

  const mockContentItem = {
    content_id: 1,
    content_name: 'Дюна',
    content_type: 'Фильм',
    content_duration: '02:35:00',
    content_publish_date: '2021-09-15T00:00:00',
    content_discription: 'Песок',
    genres: [],
    tags: [],
    copyright_holders: []
  }

  beforeEach(() => {
    vi.clearAllMocks()
    Storage.prototype.getItem = vi.fn(() => 'fake-token')
  })

  it('Рендерит карточки контента после загрузки', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([{ genre_id: 1, genre_name: 'Драма' }])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([{ tag_id: 1, tag_name: 'Новинка' }])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({
      items: [
        {
          content_id: 1,
          content_name: 'Мстители',
          content_type: 'Фильм',
          content_duration: '02:20:00',
          content_publish_date: '2012-05-01T00:00:00',
          content_discription: 'Супергеройский фильм',
          genres: [{ genre_id: 1, genre_name: 'Фантастика' }],
          tags: [],
          copyright_holders: []
        }
      ],
      total: 1,
      page: 1,
      pages: 1
    })

    const wrapper = mount(CatalogView, { global: globalOptions })
    await flushPromises()

    expect(wrapper.text()).toContain('Мстители')
    expect(wrapper.text()).toContain('Фантастика')
    expect(wrapper.text()).toContain('Супергеройский фильм')
  })

  it('Корректно обрабатывает пустое состояние каталога', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)

    const wrapper = mount(CatalogView, { global: globalOptions })
    await flushPromises()

    expect(wrapper.find('.card').exists()).toBe(false)
  })

  it('Открывает модальное окно плеера при клике на кнопку Смотреть', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContentProgress).mockResolvedValueOnce({ progress: 15 })
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({
      items: [mockContentItem],
      total: 1,
      page: 1,
      pages: 1
    } as any)

    const wrapper = mount(CatalogView, { global: globalOptions })
    await flushPromises()

    const watchBtn = wrapper.find('.action-btn')
    await watchBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('.player-overlay').exists()).toBe(true)
    expect(wrapper.text()).toContain('Дюна')
    expect(wrapper.text()).toContain('15%')
  })

  it('Открывает плеер с нулевым прогрессом при ошибке получения прогресса', async () => {
    vi.mocked(ApiService.getGenres).mockResolvedValueOnce([])
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([])
    vi.mocked(ApiService.getContentProgress).mockRejectedValueOnce(new Error('Ошибка прогресса'))
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({
      items: [mockContentItem],
      total: 1,
      page: 1,
      pages: 1
    } as any)

    const wrapper = mount(CatalogView, { global: globalOptions })
    await flushPromises()

    const watchBtn = wrapper.find('.action-btn')
    await watchBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('.player-overlay').exists()).toBe(true)
  })
})
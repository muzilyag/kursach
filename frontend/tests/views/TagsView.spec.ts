import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import TagsView from '@/views/TagsView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getTagsDirect: vi.fn(),
    getTags: vi.fn(),
    getContent: vi.fn(),
    getPopularTags: vi.fn(),
    createTag: vi.fn(),
    deleteTag: vi.fn(),
    request: vi.fn()
  }
}))

describe('Компонент TagsView.vue', () => {
  const globalOptions = {
    stubs: {
      DataTable: true,
      Pagination: true
    }
  }

  const mockTag = { tag_id: 1, tag_name: 'Комедия' }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Загружает и отображает список тегов', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({
      items: [mockTag],
      total: 1,
      page: 1,
      pages: 1
    } as any)
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValueOnce([] as any)

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getTagsDirect).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает боковую панель добавления тега', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValueOnce([] as any)

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()

    expect(wrapper.find('.side-panel').classes()).not.toContain('open')

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    expect(wrapper.find('.side-panel').classes()).toContain('open')
  })

  it('Не вызывает API удаления при отмене', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [mockTag], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValueOnce([] as any)
    window.confirm = vi.fn(() => false)

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockTag)
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteTag).not.toHaveBeenCalled()
  })

  it('Вызывает API удаления при подтверждении', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValue({ items: [mockTag], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTags).mockResolvedValue([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValue({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValue([] as any)
    window.confirm = vi.fn(() => true)

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()
    
    vi.clearAllMocks()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockTag)
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteTag).toHaveBeenCalledWith(1)
  })

  it('Показывает alert при ошибке удаления тега', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [mockTag], total: 1, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.deleteTag).mockRejectedValueOnce(new Error('Ошибка удаления'))
    window.confirm = vi.fn(() => true)

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('delete', mockTag)
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка удаления')
  })

  it('Показывает alert при ошибке сохранения тега', async () => {
    vi.mocked(ApiService.getTagsDirect).mockResolvedValueOnce({ items: [], total: 0, page: 1, pages: 1 } as any)
    vi.mocked(ApiService.getTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.getContent).mockResolvedValueOnce({ items: [] } as any)
    vi.mocked(ApiService.getPopularTags).mockResolvedValueOnce([] as any)
    vi.mocked(ApiService.createTag).mockRejectedValueOnce(new Error('Ошибка сохранения'))

    const wrapper = mount(TagsView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка сохранения')
  })
})
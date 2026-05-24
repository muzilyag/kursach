import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SubscriptionsView from '@/views/SubscriptionsView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getSubscriptions: vi.fn(),
    getSubscriptionTypes: vi.fn(),
    getUsers: vi.fn(),
    getFilteredUsers: vi.fn(),
    createSubscription: vi.fn(),
    changeSubscription: vi.fn(),
    cancelSubscription: vi.fn()
  }
}))

describe('Компонент SubscriptionsView.vue', () => {
  const globalOptions = {
    stubs: {
      DataTable: true,
      Pagination: true,
      Modal: true
    }
  }

  const mockTypes = [
    { subscribe_type_id: 1, subscribe_type_name: 'Базовый', subscribe_type_duration: 30, subscribe_type_cost: 199 }
  ]

  const mockUsers = { users: [{ user_id: 1, user_name: 'Юзер' }] }

  const mockSubs = {
    items: [
      {
        user_id: 1,
        subscribe_type_id: 1,
        subscribe_start: '2023-01-01',
        subscribe_finish: '2023-01-31',
        status: 'Активна',
        user: { user_name: 'Юзер' },
        subscribe_type: { subscribe_type_name: 'Базовый' }
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

  it('Успешно загружает список подписок, юзеров и тарифов', async () => {
    vi.mocked(ApiService.getSubscriptions).mockResolvedValueOnce(mockSubs as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockTypes as any)
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)

    const wrapper = mount(SubscriptionsView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getSubscriptions).toHaveBeenCalled()
    expect(ApiService.getSubscriptionTypes).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает модальное окно для создания новой подписки', async () => {
    vi.mocked(ApiService.getSubscriptions).mockResolvedValueOnce({ items: [], total: 0 } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockTypes as any)
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)
    vi.mocked(ApiService.getFilteredUsers).mockResolvedValueOnce([{ user_id: 2, user_name: 'Новый' }] as any)

    const wrapper = mount(SubscriptionsView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent({ name: 'Modal' })
    expect(modal.props('show')).toBe(true)
    expect(modal.props('title')).toBe('Новая подписка')
    expect(ApiService.getFilteredUsers).toHaveBeenCalled()
  })

  it('Отменяет подписку при подтверждении', async () => {
    vi.mocked(ApiService.getSubscriptions).mockResolvedValueOnce(mockSubs as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockTypes as any)
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)
    vi.mocked(ApiService.cancelSubscription).mockResolvedValueOnce({} as any)
    window.confirm = vi.fn(() => true)

    const wrapper = mount(SubscriptionsView, { global: globalOptions })
    await flushPromises()
    vi.clearAllMocks()

    const dataTable = wrapper.findComponent({ name: 'DataTable' })
    dataTable.vm.$emit('actions', mockSubs.items[0]) // эмуляция, в реале там слоты, вызовем функцию напрямую или через заглушку
    // Так как у нас нет доступа к слоту в shallow mount, вызовем метод компонента напрямую:
    await (wrapper.vm as any).cancelSub(mockSubs.items[0])
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.cancelSubscription).toHaveBeenCalledWith(1, 1, '2023-01-01')
  })

  it('Не отменяет подписку, если пользователь нажал Отмена', async () => {
    vi.mocked(ApiService.getSubscriptions).mockResolvedValueOnce(mockSubs as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockTypes as any)
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)
    window.confirm = vi.fn(() => false)

    const wrapper = mount(SubscriptionsView, { global: globalOptions })
    await flushPromises()

    await (wrapper.vm as any).cancelSub(mockSubs.items[0])
    await flushPromises()

    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.cancelSubscription).not.toHaveBeenCalled()
  })

  it('Отображает alert при ошибке сохранения в форме', async () => {
    vi.mocked(ApiService.getSubscriptions).mockResolvedValueOnce({ items: [], total: 0 } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockTypes as any)
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)
    vi.mocked(ApiService.getFilteredUsers).mockResolvedValueOnce([{ user_id: 1 }] as any)
    vi.mocked(ApiService.createSubscription).mockRejectedValueOnce(new Error('Сбой создания'))

    const wrapper = mount(SubscriptionsView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click') // Открыть модалку
    await flushPromises()

    // Имитируем отправку формы
    await (wrapper.vm as any).submitForm()
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Сбой создания')
  })
})
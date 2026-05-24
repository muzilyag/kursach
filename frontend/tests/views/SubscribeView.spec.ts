import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SubscribeView from '@/views/SubscribeView.vue'
import { ApiService } from '@/services/api'
import { useRouter } from 'vue-router'

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

vi.mock('@/services/api', () => ({
  ApiService: {
    getSubscriptionTypes: vi.fn(),
    getMe: vi.fn(),
    changeSubscription: vi.fn(),
    buySubscription: vi.fn()
  }
}))

describe('Компонент SubscribeView.vue', () => {
  const mockPlans = [
    {
      subscribe_type_id: 1,
      subscribe_type_name: 'Базовый',
      subscribe_type_discription: 'Тест',
      subscribe_type_max_type_quality: 1080,
      subscribe_type_cost: 199,
      subscribe_type_duration: 30
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    window.alert = vi.fn()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('Рендерит список тарифов', async () => {
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockPlans)
    vi.mocked(ApiService.getMe).mockRejectedValueOnce(new Error('Guest'))

    const wrapper = mount(SubscribeView)
    await flushPromises()

    expect(wrapper.text()).toContain('Базовый')
    expect(wrapper.text()).toContain('199 ₽')
  })

  it('Вызывает buySubscription для пользователя без подписки', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockPlans)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({ user_id: 1, active_subscription: null } as any)
    vi.mocked(ApiService.buySubscription).mockResolvedValueOnce({})

    const wrapper = mount(SubscribeView)
    await flushPromises()

    await wrapper.find('.purchase-btn').trigger('click')
    await flushPromises()

    expect(ApiService.buySubscription).toHaveBeenCalledWith({
      subscribe_type_id: 1,
      payment_method: 'карта'
    })
    expect(mockPush).toHaveBeenCalledWith('/profile')
  })

  it('Вызывает changeSubscription для пользователя с подпиской', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockPlans)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({
      user_id: 1,
      active_subscription: { subscribe_type_id: 2 }
    } as any)
    vi.mocked(ApiService.changeSubscription).mockResolvedValueOnce({})

    const wrapper = mount(SubscribeView)
    await flushPromises()

    await wrapper.find('.purchase-btn').trigger('click')
    await flushPromises()

    expect(ApiService.changeSubscription).toHaveBeenCalledWith({
      user_id: 1,
      subscribe_type_id: 1,
      payment_method: 'карта'
    })
    expect(mockPush).toHaveBeenCalledWith('/profile')
  })

  it('Логирует ошибку при неудачной загрузке тарифов', async () => {
    vi.mocked(ApiService.getSubscriptionTypes).mockRejectedValueOnce(new Error('Ошибка сервера'))
    vi.mocked(ApiService.getMe).mockRejectedValueOnce(new Error('Guest'))

    mount(SubscribeView)
    await flushPromises()

    expect(console.error).toHaveBeenCalled()
  })

  it('Показывает alert при ошибке покупки подписки', async () => {
    vi.mocked(useRouter).mockReturnValue({ push: vi.fn() } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockPlans)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({ user_id: 1, active_subscription: null } as any)
    vi.mocked(ApiService.buySubscription).mockRejectedValueOnce(new Error('Недостаточно средств'))

    const wrapper = mount(SubscribeView)
    await flushPromises()

    await wrapper.find('.purchase-btn').trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Недостаточно средств')
  })

  it('Показывает alert при ошибке смены подписки', async () => {
    vi.mocked(useRouter).mockReturnValue({ push: vi.fn() } as any)
    vi.mocked(ApiService.getSubscriptionTypes).mockResolvedValueOnce(mockPlans)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({
      user_id: 1,
      active_subscription: { subscribe_type_id: 2 }
    } as any)
    vi.mocked(ApiService.changeSubscription).mockRejectedValueOnce(new Error('Ошибка смены тарифа'))

    const wrapper = mount(SubscribeView)
    await flushPromises()

    await wrapper.find('.purchase-btn').trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка смены тарифа')
  })
})
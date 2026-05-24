import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DashboardView from '@/views/DashboardView.vue'
import { ApiService } from '@/services/api'

vi.mock('@/services/api', () => ({
  ApiService: {
    getStats: vi.fn()
  }
}))

describe('Компонент DashboardView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('Показывает лоадер при монтировании', () => {
    vi.mocked(ApiService.getStats).mockImplementation(() => new Promise(() => {}))
    const wrapper = mount(DashboardView)
    
    expect(wrapper.find('.spinner-border, .spinner-grow').exists()).toBe(true)
  })

  it('Рендерит ключевые метрики после успешной загрузки', async () => {
    const mockStats = {
      total_users: 1500,
      total_content: 350,
      breakdown: {
        content_types: [{ type: 'Фильм', count: 200 }],
        payment_methods: [{ method: 'карта', amount: '1000' }],
        revenue_by_tariffs: [],
        subscriptions_status: [],
        registrations_dynamics: { total_growth: 10, growth_percentage: 5, daily: [] }
      }
    }
    
    vi.mocked(ApiService.getStats).mockResolvedValueOnce(mockStats as any)

    const wrapper = mount(DashboardView)
    await flushPromises()

    expect(wrapper.find('.spinner-border, .spinner-grow').exists()).toBe(false)
    expect(wrapper.text()).toContain('1500')
    expect(wrapper.text()).toContain('350')
  })

  it('Обрабатывает ошибку загрузки данных и скрывает лоадер', async () => {
    vi.mocked(ApiService.getStats).mockRejectedValueOnce(new Error('Сетевая ошибка'))

    const wrapper = mount(DashboardView)
    await flushPromises()

    expect(wrapper.find('.spinner-border, .spinner-grow').exists()).toBe(false)
    expect(console.error).toHaveBeenCalled()
  })

  it('Корректно рендерит дашборд при нулевых значениях', async () => {
    const emptyStats = {
      total_users: 0,
      total_content: 0,
      breakdown: {
        content_types: [],
        payment_methods: [],
        revenue_by_tariffs: [],
        subscriptions_status: [],
        registrations_dynamics: { total_growth: 0, growth_percentage: 0, daily: [] }
      }
    }
    
    vi.mocked(ApiService.getStats).mockResolvedValueOnce(emptyStats as any)

    const wrapper = mount(DashboardView)
    await flushPromises()

    expect(wrapper.text()).toContain('0')
  })
})
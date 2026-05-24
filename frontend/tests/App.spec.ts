import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '@/App.vue'
import { ApiService } from '@/services/api'
import { useRoute } from 'vue-router'

vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  RouterLink: { template: '<a><slot /></a>' },
  RouterView: { template: '<div class="router-view"></div>' }
}))

vi.mock('@/services/api', () => ({
  ApiService: {
    checkHealth: vi.fn(),
    getMe: vi.fn(),
    getRoleFromToken: vi.fn(),
    logout: vi.fn()
  }
}))

vi.mock('@/components/Sidebar.vue', () => ({
  default: { template: '<div class="mock-sidebar"></div>' }
}))

describe('Компонент App.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('Рендерит только RouterView на страницах авторизации (login/register)', async () => {
    vi.mocked(useRoute).mockReturnValue({ name: 'login', path: '/login' } as any)
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue(null)

    const wrapper = mount(App)
    await flushPromises()

    expect(wrapper.find('.router-view').exists()).toBe(true)
    expect(wrapper.find('.mock-sidebar').exists()).toBe(false)
    expect(wrapper.find('header').exists()).toBe(false)
  })

  it('Инициализирует данные пользователя и здоровье БД при наличии токена', async () => {
    vi.mocked(useRoute).mockReturnValue({ name: 'catalog', path: '/catalog' } as any)
    Storage.prototype.getItem = vi.fn(() => 'valid_token')
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('admin')
    vi.mocked(ApiService.checkHealth).mockResolvedValueOnce(true as any)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({ user_name: 'Иван' } as any)

    const wrapper = mount(App)
    await flushPromises()

    expect(ApiService.checkHealth).toHaveBeenCalled()
    expect(ApiService.getMe).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Иван')
    expect(wrapper.text()).toContain('Администратор')
  })

  it('Обрабатывает ошибку загрузки профиля (сервер недоступен)', async () => {
    vi.mocked(useRoute).mockReturnValue({ name: 'catalog', path: '/catalog' } as any)
    Storage.prototype.getItem = vi.fn(() => 'valid_token')
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('admin')
    vi.mocked(ApiService.checkHealth).mockRejectedValueOnce(new Error('DB Error'))
    vi.mocked(ApiService.getMe).mockRejectedValueOnce(new Error('API Error'))

    const wrapper = mount(App)
    await flushPromises()

    expect(console.error).toHaveBeenCalled()
    // Компонент не должен падать, просто данные не загрузятся
    expect(wrapper.find('.mock-sidebar').exists()).toBe(true)
  })

  it('Вызывает логаут при нажатии на кнопку выхода', async () => {
    vi.mocked(useRoute).mockReturnValue({ name: 'catalog', path: '/catalog' } as any)
    Storage.prototype.getItem = vi.fn(() => 'valid_token')
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('admin')
    vi.mocked(ApiService.checkHealth).mockResolvedValueOnce(true as any)
    vi.mocked(ApiService.getMe).mockResolvedValueOnce({ user_name: 'Иван' } as any)

    const wrapper = mount(App)
    await flushPromises()

    const logoutBtn = wrapper.find('.user-profile button')
    await logoutBtn.trigger('click')

    expect(ApiService.logout).toHaveBeenCalled()
  })

  it('Переключает состояние бокового меню (isPinned)', async () => {
    vi.mocked(useRoute).mockReturnValue({ name: 'catalog', path: '/catalog' } as any)
    Storage.prototype.getItem = vi.fn(() => 'valid_token')
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('admin')
    
    const wrapper = mount(App)
    await flushPromises()

    const mainContent = wrapper.find('main')
    expect(mainContent.attributes('style')).toContain('margin-left: 280px')

    const toggleBtn = wrapper.find('header button')
    await toggleBtn.trigger('click')
    await flushPromises()

    expect(mainContent.attributes('style')).toContain('margin-left: 76px')
  })
})
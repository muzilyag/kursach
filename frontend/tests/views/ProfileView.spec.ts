import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ProfileView from '@/views/ProfileView.vue'
import { ApiService } from '@/services/api'
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div></div>' } },
    { path: '/subscribe', component: { template: '<div></div>' } }
  ]
})

vi.mock('@/services/api', () => ({
  ApiService: {
    getMe: vi.fn(),
    updateMe: vi.fn(),
    changePassword: vi.fn(),
    deleteMe: vi.fn(),
    cancelSubscription: vi.fn(),
    logout: vi.fn()
  }
}))

describe('Компонент ProfileView.vue', () => {
  const globalOptions = {
    plugins: [router]
  }

  const mockUser = {
    user_id: 1,
    user_name: 'Тест Тестов',
    user_email: 'test@mail.ru',
    user_birth_date: '1990-01-01T00:00:00',
    user_registration_date: '2023-01-01T00:00:00',
    user_role: 'user',
    active_subscription: null
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Рендерит данные пользователя после загрузки', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    expect((wrapper.find('input[type="text"]').element as HTMLInputElement).value).toBe('Тест Тестов')
    expect((wrapper.find('input[type="email"]').element as HTMLInputElement).value).toBe('test@mail.ru')
  })

  it('Показывает ошибку при несовпадении паролей', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    const passwordInputs = wrapper.findAll('input[type="password"]')
    await passwordInputs[0]!.setValue('oldpass')
    await passwordInputs[1]!.setValue('newpass1')
    await passwordInputs[2]!.setValue('newpass2')

    await wrapper.findAll('form')[1]!.trigger('submit.prevent')
    
    expect(wrapper.find('.alert-danger').text()).toBe('Пароли не совпадают')
    expect(ApiService.changePassword).not.toHaveBeenCalled()
  })

  it('Успешно вызывает удаление аккаунта', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    vi.mocked(ApiService.deleteMe).mockResolvedValueOnce({} as any)
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('button.btn-outline-danger.w-100').trigger('click')
    
    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteMe).toHaveBeenCalled()
    expect(ApiService.logout).toHaveBeenCalled()
  })

  it('Не вызывает удаление аккаунта при отмене действия', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    window.confirm = vi.fn(() => false)
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('button.btn-outline-danger.w-100').trigger('click')
    
    expect(window.confirm).toHaveBeenCalled()
    expect(ApiService.deleteMe).not.toHaveBeenCalled()
  })

  it('Отображает ошибку от сервера при смене пароля', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    vi.mocked(ApiService.changePassword).mockRejectedValueOnce(new Error('Неверный старый пароль'))
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    const passwordInputs = wrapper.findAll('input[type="password"]')
    await passwordInputs[0]!.setValue('wrongoldpass')
    await passwordInputs[1]!.setValue('newpass1')
    await passwordInputs[2]!.setValue('newpass1')

    await wrapper.findAll('form')[1]!.trigger('submit.prevent')
    await flushPromises()
    
    expect(wrapper.find('.alert-danger').text()).toBe('Неверный старый пароль')
  })

  it('Отображает alert при неудачном удалении аккаунта', async () => {
    vi.mocked(ApiService.getMe).mockResolvedValueOnce(mockUser as any)
    vi.mocked(ApiService.deleteMe).mockRejectedValueOnce(new Error('Ошибка при удалении'))
    
    const wrapper = mount(ProfileView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('button.btn-outline-danger.w-100').trigger('click')
    await flushPromises()
    
    expect(ApiService.deleteMe).toHaveBeenCalled()
    expect(window.alert).toHaveBeenCalledWith('Ошибка при удалении аккаунта')
  })
})
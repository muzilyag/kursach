import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginView from '@/views/LoginView.vue'
import { ApiService } from '@/services/api'
import { useRouter } from 'vue-router'

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

vi.mock('@/services/api', () => ({
  ApiService: {
    login: vi.fn(),
    getRoleFromToken: vi.fn()
  }
}))

describe('Компонент LoginView.vue', () => {
  const globalOptions = {
    stubs: {
      RouterLink: true
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('Рендерит форму входа', () => {
    const wrapper = mount(LoginView, { global: globalOptions })
    expect(wrapper.find('h1').text()).toBe('Вход в систему')
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('Отображает ошибку при неверном логине', async () => {
    vi.mocked(ApiService.login).mockRejectedValueOnce(new Error('Неверный пароль'))
    
    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('test@mail.ru')
    await wrapper.find('input[type="password"]').setValue('wrong_pass')
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.find('.alert-danger').text()).toBe('Неверный пароль')
  })

  it('Редиректит обычного пользователя в каталог', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.login).mockResolvedValueOnce({ access_token: '123', token_type: 'bearer' })
    vi.mocked(ApiService.getRoleFromToken).mockReturnValueOnce('user')

    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('user@mail.ru')
    await wrapper.find('input[type="password"]').setValue('123123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith('/catalog')
  })

  it('Редиректит контент-менеджера в раздел контента', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.login).mockResolvedValueOnce({ access_token: '123', token_type: 'bearer' })
    vi.mocked(ApiService.getRoleFromToken).mockReturnValueOnce('content_manager')

    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('manager@mail.ru')
    await wrapper.find('input[type="password"]').setValue('123123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith('/content')
  })

  it('Редиректит суперадмина в раздел пользователей', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.login).mockResolvedValueOnce({ access_token: '123', token_type: 'bearer' })
    vi.mocked(ApiService.getRoleFromToken).mockReturnValueOnce('superadmin')

    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('admin@mail.ru')
    await wrapper.find('input[type="password"]').setValue('123123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith('/users')
  })
  
  it('Редиректит админа в дашборд', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.login).mockResolvedValueOnce({ access_token: '123', token_type: 'bearer' })
    vi.mocked(ApiService.getRoleFromToken).mockReturnValueOnce('admin')

    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('admin@mail.ru')
    await wrapper.find('input[type="password"]').setValue('123123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith('admin/dashboard')
  })

  it('Редиректит в каталог по умолчанию, если роль не определена', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.login).mockResolvedValueOnce({ access_token: '123', token_type: 'bearer' })
    vi.mocked(ApiService.getRoleFromToken).mockReturnValueOnce(null)

    const wrapper = mount(LoginView, { global: globalOptions })
    await wrapper.find('input[type="text"]').setValue('user@mail.ru')
    await wrapper.find('input[type="password"]').setValue('123123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith('/catalog')
  })
})
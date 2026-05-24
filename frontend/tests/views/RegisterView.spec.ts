import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import RegisterView from '@/views/RegisterView.vue'
import { ApiService } from '@/services/api'
import { useRouter } from 'vue-router'

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

vi.mock('@/services/api', () => ({
  ApiService: {
    register: vi.fn()
  }
}))

describe('Компонент RegisterView.vue', () => {
  const globalOptions = {
    stubs: {
      RouterLink: true
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('Рендерит форму регистрации', () => {
    const wrapper = mount(RegisterView, { global: globalOptions })
    expect(wrapper.find('h1').text()).toBe('Регистрация')
    expect(wrapper.findAll('input').length).toBe(4) 
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('Отображает ошибку при неудачной регистрации', async () => {
    vi.mocked(ApiService.register).mockRejectedValueOnce(new Error('Email уже занят'))
    
    const wrapper = mount(RegisterView, { global: globalOptions })
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    
    expect(wrapper.find('.alert-danger').text()).toBe('Email уже занят')
  })

  it('Успешно регистрирует и редиректит на страницу логина', async () => {
    const mockPush = vi.fn()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(ApiService.register).mockResolvedValueOnce({} as any)

    const wrapper = mount(RegisterView, { global: globalOptions })
    await wrapper.find('input[type="email"]').setValue('newuser@mail.ru')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(mockPush).toHaveBeenCalledWith('/login')
  })

  it('Очищает старую ошибку при повторной попытке', async () => {
    vi.mocked(ApiService.register).mockRejectedValueOnce(new Error('Первая ошибка'))
    
    const wrapper = mount(RegisterView, { global: globalOptions })
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    
    expect(wrapper.find('.alert-danger').text()).toBe('Первая ошибка')

    vi.mocked(ApiService.register).mockResolvedValueOnce({} as any)
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.find('.alert-danger').exists()).toBe(false)
  })
})
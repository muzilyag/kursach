import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UsersView from '@/views/UsersView.vue'
import { ApiService } from '@/services/api'
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/', component: { template: '<div></div>' } }]
})

vi.mock('@/services/api', () => ({
  ApiService: {
    getUsers: vi.fn(),
    createUser: vi.fn(),
    updateUser: vi.fn(),
    deleteUser: vi.fn(),
    getRoleFromToken: vi.fn()
  }
}))

describe('Компонент UsersView.vue', () => {
  const globalOptions = {
    plugins: [router],
    stubs: {
      DataTable: true,
      Pagination: true,
      Modal: true
    }
  }

  const mockUsers = {
    users: [
      {
        user_id: 1,
        user_name: 'Иван Иванов',
        user_email: 'ivan@example.com',
        user_role: 'user',
        user_birth_date: '1990-01-01T00:00:00',
        user_registration_date: '2023-01-01T00:00:00'
      },
      {
        user_id: 2,
        user_name: 'Админ Админов',
        user_email: 'admin@example.com',
        user_role: 'admin',
        user_birth_date: '1985-05-05T00:00:00',
        user_registration_date: '2022-01-01T00:00:00'
      }
    ],
    total: 2
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
  })

  it('Загружает и отображает список пользователей', async () => {
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('superadmin')
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce(mockUsers as any)

    const wrapper = mount(UsersView, { global: globalOptions })
    await flushPromises()

    expect(ApiService.getUsers).toHaveBeenCalled()
    expect(wrapper.findComponent({ name: 'DataTable' }).exists()).toBe(true)
  })

  it('Открывает модальное окно для добавления пользователя', async () => {
    vi.mocked(ApiService.getRoleFromToken).mockReturnValue('superadmin')
    vi.mocked(ApiService.getUsers).mockResolvedValueOnce({ users: [], total: 0 } as any)

    const wrapper = mount(UsersView, { global: globalOptions })
    await flushPromises()

    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent({ name: 'Modal' })
    expect(modal.props('show')).toBe(true)
    expect(modal.props('title')).toBe('Новый пользователь')
  })
})
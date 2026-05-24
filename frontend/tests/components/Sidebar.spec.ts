import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Sidebar from '@/components/Sidebar.vue'

describe('Компонент Sidebar.vue', () => {
  const globalOptions = {
    stubs: {
      RouterLink: { template: '<a><slot /></a>' }
    }
  }

  it('Рендерит меню для пользователя', () => {
    const wrapper = mount(Sidebar, {
      props: {
        userRole: 'user',
        currentUser: { active_subscription: null } as any,
        isPinned: true,
        isDbConnected: true
      },
      global: globalOptions
    })

    const text = wrapper.text()
    expect(text).toContain('Каталог')
    expect(text).toContain('Профиль')
    expect(text).toContain('Премиум доступ')
    expect(text).not.toContain('Пользователи')
    expect(text).not.toContain('Контент')
  })

  it('Рендерит меню для администратора', () => {
    const wrapper = mount(Sidebar, {
      props: {
        userRole: 'admin',
        currentUser: {} as any,
        isPinned: true,
        isDbConnected: true
      },
      global: globalOptions
    })

    const text = wrapper.text()
    expect(text).toContain('Дашборд')
    expect(text).toContain('Пользователи')
    expect(text).toContain('Подписки')
    expect(text).toContain('Отчеты')
    expect(text).not.toContain('Контент')
  })

  it('Рендерит меню для контент-менеджера', () => {
    const wrapper = mount(Sidebar, {
      props: {
        userRole: 'content_manager',
        currentUser: {} as any,
        isPinned: true,
        isDbConnected: true
      },
      global: globalOptions
    })

    const text = wrapper.text()
    expect(text).toContain('Контент')
    expect(text).toContain('Реклама')
    expect(text).toContain('Теги')
    expect(text).toContain('Правообладатели')
    expect(text).not.toContain('Дашборд')
  })

  it('Отображает ошибку подключения к БД', () => {
    const wrapper = mount(Sidebar, {
      props: {
        userRole: 'user',
        currentUser: {} as any,
        isPinned: true,
        isDbConnected: false
      },
      global: globalOptions
    })

    expect(wrapper.text()).toContain('Недоступна')
  })

  it('Добавляет класс slim-mode, если меню не закреплено', () => {
    const wrapper = mount(Sidebar, {
      props: {
        userRole: 'user',
        currentUser: {} as any,
        isPinned: false,
        isDbConnected: true
      },
      global: globalOptions
    })

    expect(wrapper.classes()).toContain('slim-mode')
  })
})
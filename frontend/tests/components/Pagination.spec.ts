import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Pagination from '@/components/Pagination.vue'

describe('Компонент Pagination.vue', () => {
  it('Корректно рендерит общее количество записей', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        pages: [1, 2, 3],
        total: 150
      }
    })
    expect(wrapper.text()).toContain('Всего записей: 150')
  })

  it('Корректно отображает состояние при 0 записей и пустых страницах', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        pages: [],
        total: 0
      }
    })
    expect(wrapper.text()).toContain('Всего записей: 0')
  })

  it('Кнопка "Назад" отключена на первой странице', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        pages: [1, 2, 3],
        total: 30
      }
    })
    const prevButtonLi = wrapper.findAll('.page-item')[0]
    expect(prevButtonLi?.classes()).toContain('disabled')
  })

  it('Кнопка "Вперед" отключена на последней странице', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        pages: [1, 2, 3],
        total: 30
      }
    })
    const items = wrapper.findAll('.page-item')
    const nextButtonLi = items[items.length - 1]
    expect(nextButtonLi?.classes()).toContain('disabled')
  })

  it('Не эмитит событие при клике на отключенную кнопку "Назад"', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        pages: [1, 2],
        total: 20
      }
    })
    
    const prevButton = wrapper.findAll('.page-link')[0]
    await prevButton?.trigger('click')

    expect(wrapper.emitted('update:page')).toBeUndefined()
  })

  it('Не эмитит событие при клике на отключенную кнопку "Вперед"', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        pages: [1, 2],
        total: 20
      }
    })
    
    const links = wrapper.findAll('.page-link')
    const nextButton = links[links.length - 1]
    await nextButton?.trigger('click')

    expect(wrapper.emitted('update:page')).toBeUndefined()
  })

  it('Эмитит событие update:page при клике на доступную страницу', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        pages: [1, 2, 3],
        total: 30
      }
    })
    
    const pageTwoBtn = wrapper.findAll('.page-link')[2]
    await pageTwoBtn?.trigger('click')

    expect(wrapper.emitted()).toHaveProperty('update:page')
    expect(wrapper.emitted('update:page')?.[0]).toEqual([2])
  })
})
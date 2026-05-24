import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/Modal.vue'

describe('Компонент Modal.vue', () => {
  it('Не рендерится, если show = false', () => {
    const wrapper = mount(Modal, {
      props: {
        show: false,
        title: 'Тестовый заголовок'
      }
    })
    expect(wrapper.find('.modal').exists()).toBe(false)
  })

  it('Рендерит модальное окно и заголовок, если show = true', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Мой супер заголовок'
      }
    })
    expect(wrapper.find('.modal').exists()).toBe(true)
    expect(wrapper.find('.modal-title').text()).toBe('Мой супер заголовок')
  })

  it('Рендерится без ошибок при пустом title', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: ''
      }
    })
    expect(wrapper.find('.modal').exists()).toBe(true)
    expect(wrapper.find('.modal-title').text()).toBe('')
  })

  it('Эмитит событие close при клике на кнопку-крестик', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Тест'
      }
    })
    const closeBtn = wrapper.find('.btn-close')
    await closeBtn.trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  it('Эмитит событие close при клике на фон (backdrop)', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Тест'
      }
    })
    const modalDiv = wrapper.find('.modal')
    await modalDiv.trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  it('Эмитит событие close при нажатии клавиши Escape', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Тест'
      }
    })
    await wrapper.trigger('keydown.esc')
    
    expect(wrapper.emitted()).toHaveProperty('close')
  })

  it('Рендерит контент через слоты', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true,
        title: 'Слоты'
      },
      slots: {
        default: '<div class="test-body">Тело модалки</div>',
        footer: '<button class="test-footer-btn">Кнопка в футере</button>'
      }
    })
    expect(wrapper.find('.test-body').exists()).toBe(true)
    expect(wrapper.find('.test-footer-btn').exists()).toBe(true)
  })
})
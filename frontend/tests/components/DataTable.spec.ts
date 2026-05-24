import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from '@/components/DataTable.vue'

describe('Компонент DataTable.vue', () => {
  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Имя', sortable: false }
  ]
  
  const items = [
    { id: 1, name: 'Иван' },
    { id: 2, name: 'Анна' }
  ]

  it('Рендерит правильное количество строк и колонок', () => {
    const wrapper = mount(DataTable, {
      props: { columns, items }
    })
    
    const headers = wrapper.findAll('thead th')
    expect(headers.length).toBe(3) 

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)
    expect(rows[0]!.text()).toContain('Иван')
  })

  it('Безопасно рендерит строки с отсутствующими или null значениями', () => {
    const incompleteItems = [
      { id: 1, name: null },
      { id: 2 } 
    ]
    const wrapper = mount(DataTable, {
      props: { columns, items: incompleteItems }
    })
    
    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)
  })

  it('Корректно работает с пустым массивом колонок', () => {
    const wrapper = mount(DataTable, {
      props: { columns: [], items }
    })
    
    const headers = wrapper.findAll('thead th')
    expect(headers.length).toBe(1)
  })

  it('Показывает заглушку, если данных нет', () => {
    const wrapper = mount(DataTable, {
      props: { columns, items: [] }
    })
    
    expect(wrapper.text()).toContain('Данных не найдено')
  })

  it('Эмитит событие sort при клике на сортируемую колонку', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, items }
    })
    
    const sortableHeader = wrapper.findAll('thead th')[1]
    await sortableHeader!.trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('sort')
    expect(wrapper.emitted('sort')?.[0]).toEqual(['id'])
  })

  it('Не эмитит событие sort при клике на несортируемую колонку', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, items }
    })
    
    const unsortableHeader = wrapper.findAll('thead th')[2]
    await unsortableHeader!.trigger('click')
    
    expect(wrapper.emitted('sort')).toBeUndefined()
  })

  it('Рендерит колонку действий и эмитит события edit и delete', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, items, hasActions: true }
    })
    
    const headers = wrapper.findAll('thead th')
    expect(headers.length).toBe(4)

    const editBtns = wrapper.findAll('.btn-outline-primary')
    const deleteBtns = wrapper.findAll('.btn-outline-danger')
    
    expect(editBtns.length).toBe(2)
    expect(deleteBtns.length).toBe(2)

    await editBtns[0]!.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('edit')
    expect(wrapper.emitted('edit')?.[0]).toEqual([items[0]])

    await deleteBtns[1]!.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('delete')
    expect(wrapper.emitted('delete')?.[0]).toEqual([items[1]])
  })

  it('Не рендерит колонку действий, если hasActions = false', () => {
    const wrapper = mount(DataTable, {
      props: { columns, items, hasActions: false }
    })
    
    const headers = wrapper.findAll('thead th')
    expect(headers.length).toBe(3) 
    expect(wrapper.find('.btn-outline-primary').exists()).toBe(false)
  })
})
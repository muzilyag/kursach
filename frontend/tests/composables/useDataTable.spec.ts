import { describe, it, expect, vi } from 'vitest'
import { useDataTable } from '@/composables/useDataTable'

describe('Composable useDataTable', () => {
  it('Инициализируется с дефолтными параметрами', () => {
    const mockFetch = vi.fn()
    const { params, items, total, loading } = useDataTable(mockFetch)

    expect(params.page).toBe(1)
    expect(params.limit).toBe(10)
    expect(params.order).toBe('desc')
    expect(items.value).toEqual([])
    expect(total.value).toBe(0)
    expect(loading.value).toBe(false)
  })

  it('Функция load обновляет items и total при успешном массиве', async () => {
    const mockData = [{ id: 1, name: 'Test 1' }, { id: 2, name: 'Test 2' }]
    const mockFetch = vi.fn().mockResolvedValue(mockData)
    
    const { load, items, total, loading } = useDataTable(mockFetch)
    
    const loadPromise = load()
    expect(loading.value).toBe(true) 
    
    await loadPromise
    
    expect(loading.value).toBe(false)
    expect(items.value).toEqual(mockData)
    expect(total.value).toBe(2)
  })

  it('Корректно меняет направление сортировки', () => {
    const mockFetch = vi.fn().mockResolvedValue([])
    const { handleSort, params } = useDataTable(mockFetch)

    handleSort('name')
    expect(params.sort).toBe('name')
    expect(params.order).toBe('asc')

    handleSort('name')
    expect(params.sort).toBe('name')
    expect(params.order).toBe('desc')

    handleSort('date')
    expect(params.sort).toBe('date')
    expect(params.order).toBe('asc')
  })
})
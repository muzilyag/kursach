import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ReportsView from '@/views/ReportsView.vue'
import { ApiService } from '@/services/api'
import { Utils } from '@/utils'

vi.mock('chart.js/auto', () => ({
  default: class Chart {
    destroy = vi.fn()
    resize = vi.fn()
    constructor() {}
  }
}))

vi.mock('@/services/api', () => ({
  ApiService: {
    getSeasonalityReport: vi.fn(),
    getActivityReport: vi.fn(),
    getRevenueReport: vi.fn(),
    exportSeasonalityReport: vi.fn(),
    exportActivityReport: vi.fn(),
    exportRevenueReport: vi.fn()
  }
}))

vi.mock('@/utils', () => ({
  Utils: { downloadFile: vi.fn() }
}))

describe('Компонент ReportsView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.alert = vi.fn()
    HTMLCanvasElement.prototype.getContext = vi.fn() as any
  })

  it('Успешно загружает и отображает отчет по сезонности', async () => {
    vi.mocked(ApiService.getSeasonalityReport).mockResolvedValueOnce([
      { 'Месяц': 'Январь', 'Драма': 10, 'Комедия': 20 }
    ])

    const wrapper = mount(ReportsView)
    
    await wrapper.find('select').setValue('seasonality')
    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    expect(ApiService.getSeasonalityReport).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Январь')
    expect(wrapper.text()).toContain('Драма')
  })

  it('Отображает alert при ошибке формирования отчета', async () => {
    vi.mocked(ApiService.getActivityReport).mockRejectedValueOnce(new Error('Сбой генерации'))

    const wrapper = mount(ReportsView)
    
    await wrapper.find('select').setValue('activity')
    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка: Сбой генерации')
  })

  it('Успешно скачивает PDF отчет', async () => {
    const mockBlob = new Blob(['mock content'], { type: 'application/pdf' })
    vi.mocked(ApiService.getSeasonalityReport).mockResolvedValueOnce([{ 'Месяц': 'Январь' }])
    vi.mocked(ApiService.exportSeasonalityReport).mockResolvedValueOnce(mockBlob as any)

    const wrapper = mount(ReportsView)
    
    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    const pdfBtn = wrapper.find('.btn-outline-danger')
    await pdfBtn.trigger('click')
    await flushPromises()

    expect(ApiService.exportSeasonalityReport).toHaveBeenCalled()
    expect(Utils.downloadFile).toHaveBeenCalled()
  })

  it('Отображает alert при ошибке скачивания', async () => {
    vi.mocked(ApiService.getSeasonalityReport).mockResolvedValueOnce([{ 'Месяц': 'Январь' }])
    vi.mocked(ApiService.exportSeasonalityReport).mockRejectedValueOnce(new Error('Ошибка сети'))

    const wrapper = mount(ReportsView)
    
    await wrapper.find('.btn-primary').trigger('click')
    await flushPromises()

    await wrapper.find('.btn-outline-success').trigger('click') 
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Ошибка при скачивании: Ошибка сети')
  })
})
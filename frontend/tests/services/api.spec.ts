import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiService } from '@/services/api'

describe('ApiService', () => {
  const originalFetch = global.fetch
  const originalLocalStorage = global.localStorage
  const originalLocation = window.location

  beforeEach(() => {
    global.fetch = vi.fn()
    global.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      length: 0,
      key: vi.fn(),
      clear: vi.fn()
    } as any
  })

  afterEach(() => {
    global.fetch = originalFetch
    global.localStorage = originalLocalStorage
    ;(window as any).location = originalLocation
    vi.clearAllMocks()
  })

  describe('getRoleFromToken', () => {
    it('Возвращает null, если токена нет', () => {
      vi.mocked(global.localStorage.getItem).mockReturnValue(null)
      expect(ApiService.getRoleFromToken()).toBeNull()
    })

    it('Возвращает null, если токен не содержит payload (нет точек)', () => {
      vi.mocked(global.localStorage.getItem).mockReturnValue('invalid_token_without_dots')
      expect(ApiService.getRoleFromToken()).toBeNull()
    })

    it('Корректно извлекает роль из валидного JWT токена', () => {
      const payload = { role: 'superadmin' }
      const base64Url = btoa(JSON.stringify(payload)).replace(/\+/g, '-').replace(/\//g, '_')
      const fakeToken = `header.${base64Url}.signature`
      
      vi.mocked(global.localStorage.getItem).mockReturnValue(fakeToken)
      expect(ApiService.getRoleFromToken()).toBe('superadmin')
    })

    it('Возвращает null при поврежденном токене (ошибка парсинга)', () => {
      vi.mocked(global.localStorage.getItem).mockReturnValue('header.invalid_base64_!@#$.signature')
      expect(ApiService.getRoleFromToken()).toBeNull()
    })
  })

  describe('buildQuery', () => {
    it('Игнорирует пустые, null и undefined значения', () => {
      const params = { page: 1, search: '', role: null, sort: undefined }
      expect(ApiService.buildQuery(params)).toBe('page=1')
    })

    it('Корректно обрабатывает массивы', () => {
      const params = { genre_ids: [1, 2], limit: 10 }
      expect(ApiService.buildQuery(params)).toBe('genre_ids=1&genre_ids=2&limit=10')
    })
  })

  describe('request (основной метод)', () => {
    it('Добавляет Authorization заголовок, если есть токен', async () => {
      vi.mocked(global.localStorage.getItem).mockReturnValue('fake-token')
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true })
      } as any)

      await ApiService.request('/test')

      expect(global.fetch).toHaveBeenCalledWith('/test', expect.objectContaining({
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer fake-token'
        }
      }))
    })

    it('Удаляет токен при ошибке 401 (Unauthorized)', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' })
      } as any)

      await expect(ApiService.request('/test')).rejects.toThrow('Unauthorized')
      expect(global.localStorage.removeItem).toHaveBeenCalledWith('token')
    })

    it('Выбрасывает ошибку Forbidden при 403', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({})
      } as any)

      await expect(ApiService.request('/test')).rejects.toThrow('Forbidden')
    })

    it('Обрабатывает fallback-ошибку из поля error (если нет detail)', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Bad Request Payload' })
      } as any)

      await expect(ApiService.request('/test')).rejects.toThrow('Bad Request Payload')
    })

    it('Обрабатывает fallback-ошибку при нечитаемом JSON (Generic status)', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => Promise.reject(new Error('SyntaxError'))
      } as any)

      await expect(ApiService.request('/test')).rejects.toThrow('Error: 500')
    })
  })

  describe('requestBlob (для скачивания файлов)', () => {
    it('Добавляет Authorization заголовок и возвращает Blob', async () => {
      vi.mocked(global.localStorage.getItem).mockReturnValue('fake-token')
      const mockBlob = new Blob(['test'], { type: 'application/pdf' })
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: async () => mockBlob
      } as any)

      const result = await ApiService.requestBlob('/test-blob')
      expect(result).toBe(mockBlob)
      expect(global.fetch).toHaveBeenCalledWith('/test-blob', expect.objectContaining({
        headers: {
          'Authorization': 'Bearer fake-token'
        }
      }))
    })

    it('Удаляет токен при 401 и пробрасывает ошибку', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 401
      } as any)

      await expect(ApiService.requestBlob('/test')).rejects.toThrow('Ошибка при скачивании файла: 401')
      expect(global.localStorage.removeItem).toHaveBeenCalledWith('token')
    })

    it('Выбрасывает ошибку при любом не-ok статусе', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 404
      } as any)

      await expect(ApiService.requestBlob('/test')).rejects.toThrow('Ошибка при скачивании файла: 404')
    })
  })

  describe('Авторизация (login & logout)', () => {
    it('login: сохраняет токен и возвращает данные', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'new-token', token_type: 'bearer' })
      } as any)

      const result = await ApiService.login({ identifier: 'test', password: '123' })
      expect(global.localStorage.setItem).toHaveBeenCalledWith('token', 'new-token')
      expect(result.access_token).toBe('new-token')
    })

    it('logout: удаляет токен и редиректит на главную', () => {
      delete (window as any).location
      ;(window as any).location = { href: '' }

      ApiService.logout()

      expect(global.localStorage.removeItem).toHaveBeenCalledWith('token')
      expect(window.location.href).toBe('/')
    })
  })

  describe('Обертки API (вызовы эндпоинтов)', () => {
    beforeEach(() => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'ok' }),
        blob: async () => new Blob()
      } as any)
    })

    it('Успешно выполняет все GET запросы', async () => {
      await ApiService.getMe()
      await ApiService.checkHealth()
      await ApiService.getStats()
      await ApiService.getUsers({ page: 1 })
      await ApiService.getFilteredUsers({ active: true })
      await ApiService.getContent({ page: 1 })
      await ApiService.getGenres()
      await ApiService.getTags()
      await ApiService.getPopularTags(10)
      await ApiService.getPopularTags() 
      await ApiService.getTagsDirect()
      await ApiService.getCopyrightHolders()
      await ApiService.getCopyrightHoldersDirect()
      await ApiService.getSubscriptions({})
      await ApiService.getSubscriptionTypes()
      await ApiService.getSeasonalityReport('2023-01', '2023-12')
      await ApiService.getActivityReport()
      await ApiService.getRevenueReport('2023-01-01', '2023-12-31')
      await ApiService.getContentProgress(1)
      await ApiService.getAdvertising({})
      await ApiService.getContentAdvertising(1)
      
      expect(global.fetch).toHaveBeenCalled()
    })

    it('Успешно выполняет все POST запросы', async () => {
      await ApiService.register({ user_name: 'test', user_email: 'test@mail.ru' } as any)
      await ApiService.createUser({ user_name: 'test' } as any)
      await ApiService.createContent({ content_name: 'test' } as any)
      await ApiService.createTag({ tag_name: 'test' })
      await ApiService.createCopyrightHolder({ copyright_holder_name: 'test' })
      await ApiService.createSubscription({})
      await ApiService.changeSubscription({ user_id: 1, subscribe_type_id: 1, payment_method: 'карта' })
      await ApiService.buySubscription({ subscribe_type_id: 1, payment_method: 'карта' })
      await ApiService.createAdvertising({ advertising_name: 'test' } as any)
      
      expect(global.fetch).toHaveBeenCalled()
    })

    it('Успешно выполняет все PUT и PATCH запросы', async () => {
      await ApiService.updateMe({ user_name: 'new' })
      await ApiService.updateUser(1, { user_name: 'new' })
      await ApiService.changePassword({ old_password: '1', new_password: '2' })
      await ApiService.updateContent(1, { content_name: 'new' } as any)
      await ApiService.updateCopyrightHolder(1, { copyright_holder_name: 'new' })
      await ApiService.updateSubscription(1, 1, '2023-01-01', {})
      await ApiService.cancelSubscription(1, 1, '2023-01-01')
      await ApiService.updateContentProgress(1, 100)
      await ApiService.updateAdvertising(1, { advertising_name: 'new' } as any)
      
      expect(global.fetch).toHaveBeenCalled()
    })

    it('Успешно выполняет все DELETE запросы', async () => {
      await ApiService.deleteMe()
      await ApiService.deleteUser(1)
      await ApiService.deleteContent(1)
      await ApiService.deleteTag(1)
      await ApiService.deleteCopyrightHolder(1)
      await ApiService.deleteAdvertising(1)
      
      expect(global.fetch).toHaveBeenCalled()
    })

    it('Успешно выполняет запросы requestBlob', async () => {
      await ApiService.exportSeasonalityReport('2023-01', '2023-12', 'pdf')
      await ApiService.exportActivityReport('csv')
      await ApiService.exportRevenueReport('2023-01-01', '2023-12-31', 'pdf')
      
      expect(global.fetch).toHaveBeenCalled()
    })
  })
})
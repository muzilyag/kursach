import { describe, it, expect } from 'vitest'
import { Utils } from '@/utils/index'

describe('Модуль Utils', () => {
  describe('formatDuration', () => {
    it('Должен правильно форматировать полное время', () => {
      expect(Utils.formatDuration('01:30:15')).toBe('1ч 30мин 15сек')
    })

    it('Должен скрывать нули', () => {
      expect(Utils.formatDuration('00:45:00')).toBe('45мин')
      expect(Utils.formatDuration('02:00:00')).toBe('2ч')
      expect(Utils.formatDuration('00:00:15')).toBe('15сек')
    })

    it('Должен возвращать прочерки при пустой строке или невалидных данных', () => {
      expect(Utils.formatDuration('')).toBe('---')
      expect(Utils.formatDuration('invalid_string')).toBe('---')
      expect(Utils.formatDuration('::')).toBe('---')
    })

    it('Должен корректно работать с неполным форматом', () => {
      expect(Utils.formatDuration('12:34')).toBe('12ч 34мин')
      expect(Utils.formatDuration('45')).toBe('45ч')
    })
  })

  describe('isValidEmail', () => {
    it('Должен пропускать валидные email адреса', () => {
      expect(Utils.isValidEmail('test@example.com')).toBe(true)
      expect(Utils.isValidEmail('user.name+tag@domain.co.uk')).toBe(true)
      expect(Utils.isValidEmail('123@123.com')).toBe(true)
    })

    it('Должен отклонять невалидные email адреса', () => {
      expect(Utils.isValidEmail('')).toBe(false)
      expect(Utils.isValidEmail('invalid-email')).toBe(false)
      expect(Utils.isValidEmail('test@.com')).toBe(false)
      expect(Utils.isValidEmail('@example.com')).toBe(false)
      expect(Utils.isValidEmail('test@example..com')).toBe(false)
      expect(Utils.isValidEmail('test @example.com')).toBe(false)
      expect(Utils.isValidEmail('test@example.c')).toBe(false)
    })
  })

  describe('formatCurrency', () => {
    it('Должен форматировать числа', () => {
      const formatted = Utils.formatCurrency(1500)
      const normalized = formatted.replace(/\s|\u00A0/g, ' ')
      expect(normalized).toContain('1 500')
      expect(normalized).toContain('₽')
    })

    it('Должен корректно форматировать ноль и отрицательные числа', () => {
      const zeroFormatted = Utils.formatCurrency(0).replace(/\s|\u00A0/g, ' ')
      expect(zeroFormatted).toContain('0')
      
      const negativeFormatted = Utils.formatCurrency(-5000).replace(/\s|\u00A0/g, ' ')
      expect(negativeFormatted).toContain('-5 000')
    })

    it('Должен форматировать огромные числа', () => {
      const hugeFormatted = Utils.formatCurrency(1000000000).replace(/\s|\u00A0/g, ' ')
      expect(hugeFormatted).toContain('1 000 000 000')
    })
  })

  describe('calculateAge', () => {
    it('Должен корректно высчитывать возраст', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 20
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      const birthDate = `${birthYear}-${month}-${day}`
      
      expect(Utils.calculateAge(birthDate)).toBe(20)
    })

    it('Должен учитывать, если день рождения в этом году еще не наступил', () => {
      const today = new Date()
      const birthYear = today.getFullYear() - 20
      const futureDate = new Date(today)
      futureDate.setDate(today.getDate() + 1)
      
      const month = String(futureDate.getMonth() + 1).padStart(2, '0')
      const day = String(futureDate.getDate()).padStart(2, '0')
      const birthDate = `${birthYear}-${month}-${day}`
      
      expect(Utils.calculateAge(birthDate)).toBe(19)
    })

    it('Должен возвращать 0 для дат из будущего', () => {
      const today = new Date()
      const futureYear = today.getFullYear() + 5
      expect(Utils.calculateAge(`${futureYear}-01-01`)).toBe(0)
    })

    it('Должен возвращать 0 при пустой или невалидной строке', () => {
      expect(Utils.calculateAge('')).toBe(0)
      expect(Utils.calculateAge('invalid-date')).toBe(0)
    })
  })
})
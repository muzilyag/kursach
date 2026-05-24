export const Utils = {
  formatDate(dateString: string | null, options: Intl.DateTimeFormatOptions = {}): string {
    if (!dateString) return 'Не указана'
    const date = new Date(dateString)
    const defaultOptions: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }
    return date.toLocaleDateString('ru-RU', { ...defaultOptions, ...options })
  },

  calculateAge(birthDateString: string): number {
    if (!birthDateString) return 0
    const birth = new Date(birthDateString)
    if (isNaN(birth.getTime())) return 0

    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    
    const m = today.getMonth() - birth.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--
    }

    return age < 0 ? 0 : age
  },

  formatDuration(duration: string): string {
    if (!duration || typeof duration !== 'string') return '---'

    if (!/^(\d+)(:\d+){0,2}$/.test(duration)) {
      return '---'
    }

    const parts = duration.split(':').map(Number)
    
    let h = 0, m = 0, s = 0

    if (parts.length === 3) {
      h = parts[0] ?? 0
      m = parts[1] ?? 0
      s = parts[2] ?? 0
    } else if (parts.length === 2) {
      h = parts[0] ?? 0
      m = parts[1] ?? 0
    } else if (parts.length === 1) {
      h = parts[0] ?? 0
    }

    const result = []
    if (h > 0) result.push(`${h}ч`)
    if (m > 0) result.push(`${m}мин`)
    if (s > 0) result.push(`${s}сек`)

    return result.length > 0 ? result.join(' ') : '---'
  },

  getDateDaysAgo(days: number): string {
    const date = new Date()
    date.setDate(date.getDate() - days)
    return date.toISOString().split('T')[0] ?? ''
  },

  isValidEmail(email: string): boolean {
    if (!email || typeof email !== 'string') return false
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
    if (!emailRegex.test(email)) return false
    
    if (email.includes('..')) return false
    
    return true
  },

  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }
}
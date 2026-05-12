export const Utils = {
    formatDate(dateString: string | null, options: Intl.DateTimeFormatOptions = {}): string {
        if (!dateString) return 'Не указана';
        const date = new Date(dateString);
        const defaultOptions: Intl.DateTimeFormatOptions = { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
        };
        return date.toLocaleDateString('ru-RU', { ...defaultOptions, ...options });
    },
    
    calculateAge(birthDateString: string): number {
        const birthDate = new Date(birthDateString);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    },
    
    formatDuration(duration: string): string {
        if (!duration) return '---';
        const parts = duration.split(':');
        const h = parseInt(parts[0] ?? '', 10) || 0;
        const m = parseInt(parts[1] ?? '', 10) || 0;
        const s = parseInt(parts[2] ?? '', 10) || 0;
        
        const result = [];
        if (h > 0) result.push(`${h}ч`);
        if (m > 0) result.push(`${m}мин`);
        if (s > 0 || (h === 0 && m === 0)) result.push(`${s}сек`);
        
        return result.join(' ');
    },
    
    getDateDaysAgo(days: number): string {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date.toISOString().split('T')[0] ?? '';
    },
    
    isValidEmail(email: string): boolean {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    downloadFile(blob: Blob, filename: string) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },

    formatCurrency(value: number): string {
        return new Intl.NumberFormat('ru-RU', { 
            style: 'currency', 
            currency: 'RUB',
            maximumFractionDigits: 0 
        }).format(value);
    }
};
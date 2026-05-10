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
    
    formatDuration(duration: string | null): string {
        if (!duration) return '00:00';
        const time = duration.split(':');
        if (time.length >= 2) {
            return `${time[0]}:${time[1]}`;
        }
        return '00:00';
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
    }
};
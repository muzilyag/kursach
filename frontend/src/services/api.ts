import { Config } from '../config';

export interface StatsResponse {
    users: number;
    content: number;
    totalSubscriptions: number;
    activeSubscriptions: number;
    views: number;
    totalRevenue: number;
}

export interface UsersResponse {
    users: any[];
    total: number;
    page: number;
    pages: number;
    sort: string;
    order: string;
}

export interface ContentResponse {
    content: any[];
    total: number;
    page: number;
    pages: number;
}

export interface SubscriptionsResponse {
    subscriptions: any[];
    total: number;
    page: number;
    pages: number;
    filter?: {
        start_date: string | null;
        end_date: string | null;
    };
}

export const ApiService = {
    async request<T = any>(url: string, options: RequestInit = {}): Promise<T> {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `HTTP ошибка: ${response.status}`);
        }
        
        return await response.json();
    },

    async getUsers(params: Record<string, any> = {}): Promise<UsersResponse> {
        const queryParams = new URLSearchParams({
            page: params.page || '1',
            limit: params.limit || Config.pagination.itemsPerPage.toString(),
            search: params.search || '',
            sort: params.sort || 'user_id',
            order: params.order || 'asc'
        }).toString();
        
        return this.request<UsersResponse>(`${Config.api.users}?${queryParams}`);
    },

    async getUser(id: number | string): Promise<any> {
        return this.request<any>(`${Config.api.users}/${id}`);
    },
    
    async createUser(userData: Record<string, any>): Promise<any> {
        return this.request<any>(Config.api.users, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    async updateUser(id: number | string, userData: Record<string, any>): Promise<any> {
        return this.request<any>(`${Config.api.users}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    },
    
    async deleteUser(id: number | string): Promise<any> {
        return this.request<any>(`${Config.api.users}/${id}`, {
            method: 'DELETE'
        });
    },

    async getContent(page: number = 1): Promise<ContentResponse> {
        return this.request<ContentResponse>(`${Config.api.content}?page=${page}&limit=${Config.pagination.itemsPerPage}`);
    },

    async createContent(contentData: Record<string, any>): Promise<any> {
        return this.request<any>(Config.api.content, {
            method: 'POST',
            body: JSON.stringify(contentData)
        });
    },

    async updateContent(id: number | string, contentData: Record<string, any>): Promise<any> {
        return this.request<any>(`${Config.api.content}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(contentData)
        });
    },
    
    async deleteContent(id: number | string): Promise<any> {
        return this.request<any>(`${Config.api.content}/${id}`, {
            method: 'DELETE'
        });
    },

    async getGenres(): Promise<any[]> {
        return this.request<any[]>(`${Config.api.content}/genres`);
    },

    async getCopyrightHolders(): Promise<any[]> {
        return this.request<any[]>(`${Config.api.content}/copyright-holders`);
    },
    
    async getSubscriptions(params: Record<string, any> = {}): Promise<SubscriptionsResponse> {
        const queryParams = new URLSearchParams({
            page: params.page || '1',
            limit: params.limit || Config.pagination.itemsPerPage.toString(),
            ...(params.startDate && { start_date: params.startDate }),
            ...(params.endDate && { end_date: params.endDate })
               }).toString();
        
        return this.request<SubscriptionsResponse>(`${Config.api.subscriptions}?${queryParams}`);
    },
    
    async getReport(params: { startDate?: string; endDate?: string } = {}): Promise<any[]> {
        if (!params.startDate || !params.endDate) {
            throw new Error('Не указан период для отчёта');
        }
        return this.request<any[]>(`${Config.api.reports}?start_date=${params.startDate}&end_date=${params.endDate}`);
    },
    
    async getStats(): Promise<StatsResponse> {
        return this.request<StatsResponse>(Config.api.stats);
    },

    async checkHealth(): Promise<any> {
        return this.request<any>(`${Config.api.base}/health`);
    }
};
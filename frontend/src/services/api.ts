import { Config } from '../config';

export interface IActiveSubscription {
    subscribe_type_id: number;
    subscribe_type_name: string;
    subscribe_finish: string;
    status: string;
}

export interface IUser {
    user_id: number;
    user_name: string;
    user_email: string;
    user_birth_date: string;
    user_registration_date: string;
    user_role?: string;
    active_subscription: IActiveSubscription | null;
}

export interface IUserCreate extends Omit<IUser, 'user_id' | 'user_registration_date' | 'active_subscription'> {
    user_password?: string;
    user_registration_date?: string;
}

export interface ILoginRequest {
    identifier: string;
    password: string;
}

export interface IAuthResponse {
    access_token: string;
    token_type: string;
}

export interface IPasswordChangeRequest {
    old_password: string;
    new_password: string;
}

export interface ISubscribeType {
    subscribe_type_id: number;
    subscribe_type_name: string;
    subscribe_type_discription: string | null;
    subscribe_type_max_type_quality: number;
    subscribe_type_cost: number;
    subscribe_type_duration: number;
}

export interface ISubscription {
    user_id: number;
    subscribe_type_id: number;
    subscribe_start: string;
    subscribe_finish: string;
    user?: IUser;
    subscribe_type?: ISubscribeType;
    status: 'Активна' | 'Истекла';
}

export interface ISubscriptionChangeRequest {
    user_id: number;
    subscribe_type_id: number;
    payment_method: 'карта' | 'сбп' | 'криптовалюта';
}

export interface IGenre {
    genre_id: number;
    genre_name: string;
}

export interface ITag {
    tag_id: number;
    tag_name: string;
}

export interface IPopularTag {
    tag_name: string;
    views_count: number;
}

export interface ICopyrightHolder {
    copyright_holder_id: number;
    copyright_holder_name: string;
    copyright_holder_phone?: string;
    copyright_holder_email?: string;
}

export interface IContent {
    content_id: number;
    content_name: string;
    content_type: string;
    content_duration: string;
    content_publish_date: string;
    content_discription: string | null;
    genres: IGenre[];
    tags: ITag[];
    copyright_holders: ICopyrightHolder[];
}

export interface IContentCreate {
    content_name: string;
    content_type: string;
    content_duration: string;
    content_publish_date: string;
    content_discription?: string;
    genre_ids: number[];
    tag_ids: number[];
    copyright_holder_ids: number[];
}

export interface IDashboardStats {
    total_users: number;
    total_revenue: string;
    total_content: number;
    total_genres: number;
    total_copyright_holders: number;
    total_tags: number;
    total_viewings: number;
    breakdown: {
        content_types: Array<{ type: string; count: number }>;
        payment_methods: Array<{ method: string; amount: string }>;
    };
}

export interface ISeasonalityReport {
    [key: string]: string | number;
}

export interface IActivityReport {
    'Тариф': string;
    'Среднее время (мин)': number;
    'Уникальный контент': number;
}

export interface IRevenueReport {
    'Тариф': string;
    'Активные подписки': number;
    'Выручка (руб.)': number;
}

export interface IAdvertising {
    advertising_id: number;
    advertising_name: string | null;
    advertising_duration: string;
    advertising_owner: string;
    advertising_start_date: string;
    advertising_finish_date: string;
    is_active: boolean;
    content_ids?: number[];
    tag_ids?: number[];
}

export interface IAdvertisingCreate {
    advertising_name: string | null;
    advertising_duration: string;
    advertising_owner: string;
    advertising_start_date: string;
    advertising_finish_date: string;
    content_ids: number[];
    tag_ids: number[];
}

export const ApiService = {
    getRoleFromToken(): string | null {
        const token = localStorage.getItem('token');
        if (!token) return null;
        try {
            const base64Url = token.split('.')[1];
            if (!base64Url) return null;
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(window.atob(base64));
            return payload.role || null;
        } catch {
            return null;
        }
    },

    buildQuery(params: any): string {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value === undefined || value === null || value === '') return;
            if (Array.isArray(value)) {
                value.forEach(v => searchParams.append(key, v));
            } else {
                searchParams.append(key, value.toString());
            }
        });
        return searchParams.toString();
    },

    async request<T = any>(url: string, options: RequestInit = {}): Promise<T> {
        const token = localStorage.getItem('token');
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string>)
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, { ...options, headers });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
        }

        if (response.status === 403) {
            throw new Error("Forbidden");
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.error || `Error: ${response.status}`);
        }
        
        return response.json();
    },

    async requestBlob(url: string, options: RequestInit = {}): Promise<Blob> {
        const token = localStorage.getItem('token');
        const headers: Record<string, string> = {
            ...(options.headers as Record<string, string>)
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, { ...options, headers });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
        }

        if (!response.ok) {
            throw new Error(`Ошибка при скачивании файла: ${response.status}`);
        }
        
        return response.blob();
    },

    async register(user: IUserCreate): Promise<IUser> {
        return this.request(`${Config.api.auth}/register`, {
            method: 'POST',
            body: JSON.stringify(user)
        });
    },

    async login(credentials: ILoginRequest): Promise<IAuthResponse> {
        const data = await this.request<IAuthResponse>(`${Config.api.auth}/login`, {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        localStorage.setItem('token', data.access_token);
        return data;
    },

    logout() {
        localStorage.removeItem('token');
        window.location.href = '/';
    },

    async getMe(): Promise<IUser> {
        return this.request(`${Config.api.users}/me`);
    },

    async updateMe(user: Partial<IUserCreate>): Promise<any> {
        return this.request(`${Config.api.users}/me`, {
            method: 'PATCH',
            body: JSON.stringify(user)
        });
    },

    async deleteMe(): Promise<any> {
        return this.request(`${Config.api.users}/me`, {
            method: 'DELETE'
        });
    },

    async checkHealth(): Promise<boolean> {
        return this.request(Config.api.health);
    },

    async getStats(): Promise<IDashboardStats> {
        return this.request<IDashboardStats>(Config.api.stats);
    },

    async getUsers(params: any): Promise<{ users: IUser[], total: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.users}?${query}`);
    },

    async getFilteredUsers(params: any): Promise<IUser[]> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.subscriptions}/users-filtered?${query}`);
    },

    async createUser(user: IUserCreate): Promise<any> {
        return this.request(Config.api.users, {
            method: 'POST',
            body: JSON.stringify(user)
        });
    },

    async updateUser(id: number, user: Partial<IUserCreate>): Promise<any> {
        return this.request(`${Config.api.users}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(user)
        });
    },

    async changePassword(payload: IPasswordChangeRequest): Promise<any> {
        return this.request(`${Config.api.users}/me/password`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        });
    },

    async deleteUser(id: number): Promise<any> {
        return this.request(`${Config.api.users}/${id}`, {
            method: 'DELETE'
        });
    },

    async getContent(params: any): Promise<{ items: IContent[], total: number, page: number, pages: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.content}?${query}`);
    },

    async createContent(content: IContentCreate): Promise<any> {
        return this.request(Config.api.content, {
            method: 'POST',
            body: JSON.stringify(content)
        });
    },

    async updateContent(id: number, content: Partial<IContentCreate>): Promise<any> {
        return this.request(`${Config.api.content}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(content)
        });
    },

    async deleteContent(id: number): Promise<any> {
        return this.request(`${Config.api.content}/${id}`, {
            method: 'DELETE'
        });
    },

    async getGenres(): Promise<IGenre[]> {
        return this.request(Config.api.genres);
    },

    async getTags(): Promise<ITag[]> {
        return this.request(Config.api.tags);
    },

    async getPopularTags(limit: number = 50): Promise<IPopularTag[]> {
        return this.request(`${Config.api.tagsDirect}/popular?limit=${limit}`);
    },

    async getTagsDirect(params: any = {}): Promise<{ items: ITag[], total: number, page: number, pages: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.tagsDirect}?${query}`);
    },

    async createTag(tag: { tag_name: string }): Promise<ITag> {
        return this.request(Config.api.tagsDirect, {
            method: 'POST',
            body: JSON.stringify(tag)
        });
    },

    async deleteTag(id: number): Promise<any> {
        return this.request(`${Config.api.tagsDirect}/${id}`, {
            method: 'DELETE'
        });
    },

    async getCopyrightHolders(): Promise<ICopyrightHolder[]> {
        return this.request(Config.api.copyrightHolders);
    },

    async getCopyrightHoldersDirect(params: any = {}): Promise<{ items: ICopyrightHolder[], total: number, page: number, pages: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.copyrightHoldersDirect}?${query}`);
    },

    async createCopyrightHolder(holder: Omit<ICopyrightHolder, 'copyright_holder_id'>): Promise<ICopyrightHolder> {
        return this.request(Config.api.copyrightHoldersDirect, {
            method: 'POST',
            body: JSON.stringify(holder)
        });
    },

    async updateCopyrightHolder(id: number, holder: Partial<ICopyrightHolder>): Promise<ICopyrightHolder> {
        return this.request(`${Config.api.copyrightHoldersDirect}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(holder)
        });
    },

    async deleteCopyrightHolder(id: number): Promise<any> {
        return this.request(`${Config.api.copyrightHoldersDirect}/${id}`, {
            method: 'DELETE'
        });
    },

    async getSubscriptions(params: any): Promise<{ subscriptions: ISubscription[], total: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.subscriptions}?${query}`);
    },

    async getSubscriptionTypes(): Promise<ISubscribeType[]> {
        return this.request(Config.api.subscriptionTypes);
    },

    async createSubscription(payload: any): Promise<any> {
        return this.request(Config.api.subscriptions, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateSubscription(uid: number, tid: number, start: string, payload: any): Promise<any> {
        return this.request(`${Config.api.subscriptions}/${uid}/${tid}/${start}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async changeSubscription(payload: ISubscriptionChangeRequest): Promise<any> {
        return this.request(`${Config.api.subscriptions}/change`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async cancelSubscription(uid: number, tid: number, date: string): Promise<any> {
        return this.request(`${Config.api.subscriptions}/${uid}/${tid}/${date}/cancel`, {
            method: 'PATCH'
        });
    },

    async getSeasonalityReport(startMonth: string, endMonth: string): Promise<ISeasonalityReport[]> {
        return this.request(`${Config.api.reports}/seasonality?start_month=${startMonth}&end_month=${endMonth}`);
    },

    async exportSeasonalityReport(startMonth: string, endMonth: string, format: 'csv' | 'pdf'): Promise<Blob> {
        return this.requestBlob(`${Config.api.reports}/seasonality?start_month=${startMonth}&end_month=${endMonth}&export=true&format=${format}`);
    },

    async getActivityReport(): Promise<IActivityReport[]> {
        return this.request(`${Config.api.reports}/activity`);
    },

    async exportActivityReport(format: 'csv' | 'pdf'): Promise<Blob> {
        return this.requestBlob(`${Config.api.reports}/activity?export=true&format=${format}`);
    },

    async getRevenueReport(startDate: string, endDate: string): Promise<IRevenueReport[]> {
        return this.request(`${Config.api.reports}/revenue?start_date=${startDate}&end_date=${endDate}`);
    },

    async exportRevenueReport(startDate: string, endDate: string, format: 'csv' | 'pdf'): Promise<Blob> {
        return this.requestBlob(`${Config.api.reports}/revenue?start_date=${startDate}&end_date=${endDate}&export=true&format=${format}`);
    },

    async getContentProgress(id: number): Promise<{ progress: number }> {
        return this.request(`${Config.api.content}/${id}/progress`);
    },

    async updateContentProgress(id: number, progress: number): Promise<any> {
        return this.request(`${Config.api.content}/${id}/progress`, {
            method: 'PATCH',
            body: JSON.stringify({ progress })
        });
    },

    async buySubscription(payload: { subscribe_type_id: number, payment_method: string }): Promise<any> {
        return this.request(`${Config.api.subscriptions}/buy`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getAdvertising(params: any): Promise<{ items: IAdvertising[], total: number, page: number, pages: number }> {
        const query = this.buildQuery(params);
        return this.request(`${Config.api.base}/advertising?${query}`);
    },

    async createAdvertising(data: IAdvertisingCreate): Promise<IAdvertising> {
        return this.request(`${Config.api.base}/advertising`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateAdvertising(id: number, data: Partial<IAdvertisingCreate>): Promise<IAdvertising> {
        return this.request(`${Config.api.base}/advertising/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteAdvertising(id: number): Promise<any> {
        return this.request(`${Config.api.base}/advertising/${id}`, {
            method: 'DELETE'
        });
    },

    async getContentAdvertising(contentId: number): Promise<IAdvertising[]> {
        return this.request(`${Config.api.content}/${contentId}/advertising`);
    }
};
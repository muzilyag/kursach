import { Config } from '../config';

export interface IUser {
    user_id: number;
    user_name: string;
    user_email: string;
    user_birth_date: string;
    user_registration_date: string;
    user_role?: string;
}

export interface IUserCreate extends Omit<IUser, 'user_id' | 'user_registration_date'> {
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

export interface ICopyrightHolder {
    copyright_holder_id: number;
    copyright_holder_name: string;
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
    genre_id?: number;
    tag_id?: number;
    copyright_holder_id?: number;
}

export interface IDashboardStats {
    users: number;
    content: number;
    totalSubscriptions: number;
    activeSubscriptions: number;
    views: number;
    totalRevenue: number;
}

export interface ISeasonalityReport {
    month: string;
    genre_name: string;
    total_views: number;
}

export interface IActivityReport {
    user_name: string;
    total_views: number;
    has_active_subscription: boolean;
}

export interface IRevenueReport {
    subscribe_type_name: string;
    subscriptions_count: number;
    total_revenue: number;
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
        } catch (e) {
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

    async getContent(params: any): Promise<{ items: IContent[], total: number }> {
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

    async getCopyrightHolders(): Promise<ICopyrightHolder[]> {
        return this.request(Config.api.copyrightHolders);
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

    async getSeasonalityReport(year: number): Promise<ISeasonalityReport[]> {
        return this.request(`${Config.api.reports}/seasonality?year=${year}`);
    },

    async getActivityReport(): Promise<IActivityReport[]> {
        return this.request(`${Config.api.reports}/activity`);
    },

    async getRevenueReport(date: string): Promise<IRevenueReport[]> {
        return this.request(`${Config.api.reports}/revenue?target_date=${date}`);
    }
};
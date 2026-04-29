import { Config } from '../config';

export interface IUser {
    user_id: number;
    user_name: string;
    user_email: string;
    user_birth_date: string;
    user_registration_date: string;
}

export interface IUserCreate extends Omit<IUser, 'user_id' | 'user_registration_date'> {
    user_registration_date?: string;
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
            throw new Error(error.detail || error.error || `Error: ${response.status}`);
        }
        
        return response.json();
    },

    async checkHealth(): Promise<boolean> {
        return this.request(Config.api.health);
    },

    async getStats(): Promise<IDashboardStats> {
        return this.request<IDashboardStats>(Config.api.stats);
    },

    async getUsers(params: any): Promise<{ users: IUser[], total: number }> {
        const query = new URLSearchParams(params).toString();
        return this.request(`${Config.api.users}?${query}`);
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

    async deleteUser(id: number): Promise<any> {
        return this.request(`${Config.api.users}/${id}`, {
            method: 'DELETE'
        });
    },

    async getContent(params: any): Promise<{ items: IContent[], total: number }> {
        const query = new URLSearchParams(params).toString();
        return this.request(`${Config.api.content}?${query}`);
    },

    async createContent(content: IContentCreate): Promise<any> {
        return this.request(Config.api.content, {
            method: 'POST',
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

    async getSubscriptions(params: any): Promise<{ subscriptions: ISubscription[] }> {
        const query = new URLSearchParams(params).toString();
        return this.request(`${Config.api.subscriptions}?${query}`);
    },

    async getSubscriptionTypes(): Promise<ISubscribeType[]> {
        return this.request(Config.api.subscriptionTypes);
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

    async getReport(params: { startDate: string; endDate: string }): Promise<any[]> {
        return this.request(`${Config.api.reports}?start_date=${params.startDate}&end_date=${params.endDate}`);
    }
};
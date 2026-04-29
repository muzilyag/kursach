const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const Config = {
    pagination: {
        itemsPerPage: 10,
        maxPagesToShow: 5
    },
    genreColors: {
        'драма': 'genre-drama',
        'комедия': 'genre-comedy',
        'боевик': 'genre-action',
        'триллер': 'genre-thriller',
        'ужасы': 'genre-horror',
        'романтика': 'genre-romance',
        'фантастика': 'genre-fantasy',
        'научная фантастика': 'genre-sci-fi',
        'документальный': 'genre-documentary',
        'анимация': 'genre-animation',
        'приключения': 'genre-adventure',
        'детектив': 'genre-mystery'
    } as Record<string, string>,
    statusColors: {
        'Активна': 'success',
        'Истекла': 'secondary'
    } as Record<string, string>,
    api: {
        base: API_BASE,
        users: `${API_BASE}/users`,
        content: `${API_BASE}/content`,
        subscriptions: `${API_BASE}/subscriptions`,
        subscriptionTypes: `${API_BASE}/subscriptions/types`,
        reports: `${API_BASE}/reports/activity`,
        stats: `${API_BASE}/stats`,
        health: `${API_BASE}/health`,
        genres: `${API_BASE}/content/genres`
    }
};
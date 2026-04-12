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
        'Истекла': 'secondary',
        'active': 'success',
        'expired': 'secondary'
    } as Record<string, string>,
    api: {
        base: '/api',
        users: '/api/users',
        content: '/api/content',
        subscriptions: '/api/subscriptions',
        reports: '/api/reports/activity',
        stats: '/api/stats',
        health: '/api/health',
        genres: '/api/genres'
    }
};
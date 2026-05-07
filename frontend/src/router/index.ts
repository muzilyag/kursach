import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'

const getRole = () => {
  const token = localStorage.getItem('token')
  if (!token) return null
  try {
    return JSON.parse(atob(token.split('.')[1] ?? '')).role
  } catch (e) {
    return null
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { public: true }
    },
    {
      path: '/client',
      name: 'client',
      component: () => import('../views/ClientStubView.vue'),
      meta: { allowedRoles: ['user'] }
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { allowedRoles: ['admin'] }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { allowedRoles: ['admin'] }
    },
    {
      path: '/content',
      name: 'content',
      component: () => import('../views/ContentView.vue'),
      meta: { allowedRoles: ['admin', 'content_manager'] }
    },
    {
      path: '/subscriptions',
      name: 'subscriptions',
      component: () => import('../views/SubscriptionsView.vue'),
      meta: { allowedRoles: ['admin'] }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { allowedRoles: ['admin'] }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = getRole()

  if (to.meta.public) {
    if (token) {
      if (role === 'user') return next('/client')
      if (role === 'content_manager') return next('/content')
      return next('/')
    }
    return next()
  }

  if (!token) {
    return next('/login')
  }

  if (to.path === '/' && role === 'content_manager') {
    return next('/content')
  }

  if (to.path === '/' && role === 'user') {
    return next('/client')
  }

  const allowedRoles = to.meta.allowedRoles as string[]
  if (allowedRoles && !allowedRoles.includes(role)) {
    alert(`Доступ запрещен. Ваша роль (${role}) не имеет прав для просмотра этого раздела.`)
    return next(false)
  }

  next()
})

export default router
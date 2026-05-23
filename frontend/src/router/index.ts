import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import CatalogView from '../views/CatalogView.vue'

const getRole = () => {
  const token = localStorage.getItem('token')
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1] ?? ''))
    return payload.role || null
  } catch {
    return null
  }
}

const isAdminRedirect = (role: string | null) => {
  return role === 'admin' || role === 'superadmin'
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
      path: '/catalog',
      name: 'catalog',
      component: CatalogView,
      meta: { allowedRoles: ['user', 'superadmin'] }
    },
    {
      path: '/',
      redirect: () => {
        const role = getRole()
        if (role === 'content_manager') return '/content'
        return isAdminRedirect(role) ? '/admin/dashboard' : '/catalog'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/subscribe',
      name: 'subscribe',
      component: () => import('../views/SubscribeView.vue'),
      meta: { allowedRoles: ['user', 'superadmin'] }
    },
    {
      path: '/admin/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { allowedRoles: ['admin', 'superadmin'] }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { allowedRoles: ['admin', 'superadmin'] }
    },
    {
      path: '/content',
      name: 'content',
      component: () => import('../views/ContentView.vue'),
      meta: { allowedRoles: ['superadmin', 'content_manager'] }
    },
    {
      path: '/tags',
      name: 'tags',
      component: () => import('../views/TagsView.vue'),
      meta: { allowedRoles: ['superadmin', 'content_manager'] }
    },
    {
      path: '/copyright-holders',
      name: 'copyright-holders',
      component: () => import('../views/CopyrightHoldersView.vue'),
      meta: { allowedRoles: ['superadmin', 'content_manager'] }
    },
    {
      path: '/advertising',
      name: 'advertising',
      component: () => import('../views/AdvertisingView.vue'),
      meta: { allowedRoles: ['superadmin', 'content_manager'] }
    },
    {
      path: '/subscriptions',
      name: 'subscriptions',
      component: () => import('../views/SubscriptionsView.vue'),
      meta: { allowedRoles: ['admin', 'superadmin'] }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { allowedRoles: ['admin', 'superadmin'] }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = getRole()

  if (to.meta.public) {
    if (token && (to.name === 'login' || to.name === 'register')) {
      if (role === 'content_manager') return next('/content')
      return next(isAdminRedirect(role) ? '/admin/dashboard' : '/catalog')
    }
    return next()
  }

  if (!token) {
    if (to.name === 'catalog') {
      return next()
    }
    return next('/login')
  }

  const allowedRoles = to.meta.allowedRoles as string[]
  if (allowedRoles && !allowedRoles.includes(role || '')) {
    if (role === 'content_manager') return next('/content')
    if (role === 'admin') return next('/admin/dashboard')
    return next('/catalog')
  }

  next()
})

export default router
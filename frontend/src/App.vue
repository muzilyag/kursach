<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ApiService } from './services/api'
import type { IUser } from './services/api'

const route = useRoute()
const isDbConnected = ref(false)
const currentUser = ref<IUser | null>(null)
const userRole = ref<string | null>(null)

const isAuthPage = computed(() => ['login', 'register'].includes(route.name as string))
const isStaff = computed(() => ['admin', 'content_manager'].includes(userRole.value || ''))

const roleLabels: Record<string, string> = {
  admin: 'Администратор',
  content_manager: 'Контент-менеджер',
  user: 'Пользователь'
}

const displayRole = computed(() => {
  return userRole.value ? (roleLabels[userRole.value] || userRole.value) : ''
})

const initializeApp = async () => {
  const token = localStorage.getItem('token')
  userRole.value = ApiService.getRoleFromToken()
  
  if (isAuthPage.value || !token) {
    currentUser.value = null
    return
  }

  try {
    const [health, user] = await Promise.all([
      ApiService.checkHealth().catch(() => false),
      ApiService.getMe().catch(() => null)
    ])
    
    isDbConnected.value = !!health
    currentUser.value = user
  } catch (e) {
    console.error('Initialization error:', e)
  }
}

watch(() => route.path, () => {
  initializeApp()
}, { immediate: true })

onMounted(() => {
  initializeApp()
})

const handleLogout = () => {
  ApiService.logout()
}
</script>

<template>
  <div v-if="isAuthPage">
    <RouterView />
  </div>

  <div v-else class="d-flex min-vh-100" style="background-color: var(--light-bg);">
    <aside v-if="userRole" class="sidebar d-flex flex-column p-3 vh-100 position-fixed" style="background-color: var(--sidebar-bg); color: var(--sidebar-text-light);">
      <RouterLink to="/catalog" class="d-flex align-items-center mb-4 text-decoration-none" style="color: var(--sidebar-text-light);">
        <i class="bi bi-film fs-3 me-2" style="color: var(--sidebar-primary);"></i>
        <span class="fs-4 fw-bold">MishlenKino</span>
      </RouterLink>
      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item">
          <RouterLink to="/profile" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-person-circle me-2"></i>
            Профиль
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/catalog" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-grid me-2"></i>
            Каталог
          </RouterLink>
        </li>
        <li class="nav-item" v-if="userRole === 'admin'">
          <RouterLink to="/admin/dashboard" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-speedometer2 me-2"></i>
            Дашборд
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/users" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-people me-2"></i>
            Пользователи
          </RouterLink>
        </li>
        <li v-if="isStaff">
          <RouterLink to="/content" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-collection-play me-2"></i>
            Контент
          </RouterLink>
        </li>
        <li v-if="isStaff">
          <RouterLink to="/tags" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-tags me-2"></i>
            Теги
          </RouterLink>
        </li>
        <li v-if="isStaff">
          <RouterLink to="/copyright-holders" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-shield-check me-2"></i>
            Правообладатели
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/subscriptions" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-card-checklist me-2"></i>
            Подписки
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/reports" class="nav-link text-white" active-class="active" style="--bs-nav-pills-link-active-bg: var(--sidebar-primary);">
            <i class="bi bi-bar-chart me-2"></i>
            Отчеты
          </RouterLink>
        </li>
      </ul>
      <hr style="border-color: var(--sidebar-border);">
      <div class="status-indicator">
        <small style="color: var(--sidebar-text-muted);" class="d-block mb-1">Статус БД:</small>
        <div v-if="isDbConnected" style="color: var(--success-color);" class="fw-bold small">
          <i class="bi bi-check-circle me-1"></i>Активна
        </div>
        <div v-else style="color: var(--danger-color);" class="fw-bold small">
          <i class="bi bi-x-circle me-1"></i>Недоступна
        </div>
      </div>
    </aside>

    <main class="main-content flex-grow-1" :style="{ marginLeft: userRole ? '280px' : '0' }">
      <header class="header d-flex justify-content-between align-items-center p-3 mb-4 shadow-sm" style="background-color: var(--card-bg); border-bottom: 1px solid var(--border-color);">
        <RouterLink to="/catalog" class="text-decoration-none d-flex align-items-center">
            <i class="bi bi-film fs-4 me-2" style="color: var(--sidebar-primary);"></i>
            <h4 class="m-0 fw-bold" style="color: var(--text-darker);">MishlenKino</h4>
        </RouterLink>
        
        <div class="user-actions">
          <div v-if="!userRole" class="d-flex gap-2">
            <RouterLink to="/login" class="btn px-4 rounded-pill" style="border: 1px solid var(--sidebar-primary); color: var(--sidebar-primary);">Войти</RouterLink>
            <RouterLink to="/register" class="btn px-4 rounded-pill" style="background-color: var(--sidebar-primary); color: var(--sidebar-text-light);">Регистрация</RouterLink>
          </div>
          <div v-else class="user-profile d-flex align-items-center">
            <div class="text-end me-3 d-none d-md-block">
              <div class="fw-bold" style="color: var(--text-darker);">
                {{ currentUser?.user_name || 'Загрузка...' }}
                <span class="badge ms-1" v-if="userRole" style="background-color: var(--sidebar-primary); color: var(--sidebar-text-light);">{{ displayRole }}</span>
              </div>
              <button @click="handleLogout" class="btn btn-link p-0 text-decoration-none small" style="color: var(--danger-color);">Выйти</button>
            </div>
            <RouterLink to="/profile">
              <img :src="`https://ui-avatars.com/api/?name=${currentUser?.user_name || 'U'}&background=8b7355&color=fff`" width="40" height="40" class="rounded-circle border" style="border-color: var(--border-color) !important;">
            </RouterLink>
          </div>
        </div>
      </header>

      <div class="p-4">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style>
.sidebar { width: 280px; z-index: 1000; }
.main-content { min-height: 100vh; }
</style>
<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ApiService } from './services/api'
import type { IUser } from './services/api'

const route = useRoute()
const isDbConnected = ref(false)
const currentUser = ref<IUser | null>(null)
const userRole = ref<string | null>(null)

const isAuthPage = computed(() => route.meta.public === true)
const isClientPage = computed(() => route.name === 'client')

const roleLabels: Record<string, string> = {
  admin: 'Администратор',
  content_manager: 'Контент-менеджер',
  user: 'Пользователь'
}

const displayRole = computed(() => {
  return userRole.value ? (roleLabels[userRole.value] || userRole.value) : ''
})

const initializeApp = async () => {
  userRole.value = ApiService.getRoleFromToken()
  
  if (isAuthPage.value || isClientPage.value) return

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
  <div v-if="isAuthPage || isClientPage">
    <RouterView />
  </div>

  <div v-else class="d-flex">
    <aside class="sidebar d-flex flex-column p-3 vh-100 position-fixed bg-dark text-white">
      <RouterLink to="/" class="d-flex align-items-center mb-4 text-white text-decoration-none">
        <i class="bi bi-film fs-3 me-2" style="color: var(--primary-color);"></i>
        <span class="fs-4 fw-bold">AdminPanel</span>
      </RouterLink>
      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item" v-if="userRole === 'admin'">
          <RouterLink to="/" class="nav-link text-white" active-class="active">
            <i class="bi bi-speedometer2 me-2"></i>
            Дашборд
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/users" class="nav-link text-white" active-class="active">
            <i class="bi bi-people me-2"></i>
            Пользователи
          </RouterLink>
        </li>
        <li v-if="['admin', 'content_manager'].includes(userRole || '')">
          <RouterLink to="/content" class="nav-link text-white" active-class="active">
            <i class="bi bi-collection-play me-2"></i>
            Контент
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/subscriptions" class="nav-link text-white" active-class="active">
            <i class="bi bi-card-checklist me-2"></i>
            Подписки
          </RouterLink>
        </li>
        <li v-if="userRole === 'admin'">
          <RouterLink to="/reports" class="nav-link text-white" active-class="active">
            <i class="bi bi-bar-chart me-2"></i>
            Отчеты
          </RouterLink>
        </li>
      </ul>
      <hr class="border-secondary">
      <div class="status-indicator">
        <small class="text-muted d-block mb-1">Статус БД:</small>
        <div v-if="isDbConnected" class="text-success fw-bold">
          <i class="bi bi-check-circle me-1"></i>Активна
        </div>
        <div v-else class="text-danger fw-bold">
          <i class="bi bi-x-circle me-1"></i>Недоступна
        </div>
      </div>
    </aside>

    <main class="main-content flex-grow-1" style="margin-left: 280px;">
      <header class="header d-flex justify-content-between align-items-center p-3 mb-4 shadow-sm rounded-3">
        <h4 class="m-0 text-dark">Управление онлайн-кинотеатром</h4>
        <div class="user-profile d-flex align-items-center">
          <div class="text-end me-3 d-none d-md-block">
            <div class="fw-bold text-dark">
              {{ currentUser?.user_name || 'Загрузка профиля...' }}
              <span class="badge bg-primary ms-1" v-if="userRole">{{ displayRole }}</span>
            </div>
            <button @click="handleLogout" class="btn btn-link p-0 text-decoration-none text-danger small">Выйти</button>
          </div>
          <img :src="`https://ui-avatars.com/api/?name=${currentUser?.user_name || 'User'}&background=8b7355&color=fff`" alt="Avatar" width="40" height="40" class="rounded-circle border border-2 border-primary-custom">
        </div>
      </header>

      <RouterView />
    </main>
  </div>
</template>

<style>
.sidebar {
  width: 280px;
  z-index: 1000;
}
.main-content {
  background-color: #f8f9fa;
  min-height: 100vh;
}
.header {
  background: white;
}
</style>
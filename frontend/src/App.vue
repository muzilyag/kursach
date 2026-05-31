<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { ApiService } from './services/api'
import type { IUser } from './services/api'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const isDbConnected = ref(false)
const currentUser = ref<IUser | null>(null)
const userRole = ref<string | null>(null)
const isPinned = ref(true)
const isAuthPage = computed(() => ['login', 'register'].includes(route.name as string))

const roleLabels: Record<string, string> = {
  admin: 'Администратор',
  content_manager: 'Контент-менеджер',
  user: 'Пользователь',
  syperadmin: 'Суперадминистратор'
}

const displayRole = computed(() => {
  return userRole.value ? roleLabels[userRole.value] || userRole.value : ''
})

const initializeApp = async () => {
  console.log(`[App] initializeApp вызвана (route: ${route.path})`)
  const token = localStorage.getItem('token')
  userRole.value = ApiService.getRoleFromToken()

  console.log(`[App] Токен: ${!!token}, Роль: ${userRole.value}, AuthPage: ${isAuthPage.value}`)

  if (isAuthPage.value || !token) {
    currentUser.value = null
    return
  }

  try {
    const [health, user] = await Promise.all([
      ApiService.checkHealth().catch(() => false),
      ApiService.getMe().catch((e) => {
        console.error('[App] Ошибка получения профиля:', e);
        return null;
      })
    ])

    console.log('[App] Профиль загружен:', user?.user_email)
    isDbConnected.value = !!health
    currentUser.value = user
  } catch (e) {
    console.error('[App] Глобальная ошибка инициализации:', e)
  }
}

watch(
  () => route.path,
  () => {
    initializeApp()
  },
  { immediate: true }
)

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

  <div v-else class="d-flex min-vh-100" style="background-color: var(--light-bg)">
    <Sidebar
      :user-role="userRole"
      :current-user="currentUser"
      :is-pinned="isPinned"
      :is-db-connected="isDbConnected"
    />

    <main
      class="main-content flex-grow-1"
      :style="{ marginLeft: userRole ? (isPinned ? '280px' : '76px') : '0' }"
    >
      <header
        class="header d-flex justify-content-between align-items-center p-3 mb-4 shadow-sm"
        style="background-color: var(--card-bg); border-bottom: 1px solid var(--border-color)"
      >
        <div class="d-flex align-items-center">
          <button
            v-if="userRole"
            class="btn text-muted p-0 me-3 fs-4 border-0"
            @click="isPinned = !isPinned"
          >
            <i class="bi bi-list"></i>
          </button>
          <RouterLink to="/catalog" class="text-decoration-none d-flex align-items-center">
            <i class="bi bi-film fs-4 me-2" style="color: var(--sidebar-primary)"></i>
            <h4 class="m-0 fw-bold" style="color: var(--text-darker)">MishlenKino</h4>
          </RouterLink>
        </div>

        <div class="user-actions">
          <div v-if="!userRole" class="d-flex gap-2">
            <RouterLink to="/login" class="btn btn-guest-login px-4">Войти</RouterLink>
            <RouterLink to="/register" class="btn btn-guest-register px-4">Регистрация</RouterLink>
          </div>
          <div v-else class="user-profile d-flex align-items-center">
            <div class="text-end me-3 d-none d-md-block">
              <div class="fw-bold" style="color: var(--text-darker)">
                {{ currentUser?.user_name || 'Загрузка...' }}
                <span
                  class="badge ms-1"
                  v-if="userRole"
                  style="background-color: var(--sidebar-primary); color: var(--sidebar-text-light)"
                  >{{ displayRole }}</span
                >
              </div>
              <button
                @click="handleLogout"
                class="btn btn-link p-0 text-decoration-none small"
                style="color: var(--danger-color)"
              >
                Выйти
              </button>
            </div>
            <RouterLink to="/profile">
              <img
                :src="`https://ui-avatars.com/api/?name=${currentUser?.user_name || 'U'}&background=8b7355&color=fff`"
                width="40"
                height="40"
                class="rounded-circle border"
                style="border-color: var(--border-color) !important"
              />
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
.main-content {
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.btn-guest-login,
.btn-guest-register {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.25s ease-in-out;
  border: 1px solid var(--sidebar-primary);
}

.btn-guest-login {
  color: var(--sidebar-primary);
  background-color: transparent;
}

.btn-guest-login:hover {
  background-color: var(--sidebar-primary);
  color: var(--sidebar-text-light);
}

.btn-guest-register {
  background-color: var(--sidebar-primary);
  color: var(--sidebar-text-light);
}

.btn-guest-register:hover {
  background-color: transparent;
  color: var(--sidebar-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>

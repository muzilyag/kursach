<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { IUser } from '../services/api'

const props = defineProps<{
  userRole: string | null
  currentUser: IUser | null
  isPinned: boolean
  isDbConnected: boolean
}>()

const canSeeUser = computed(() => ['user', 'superadmin'].includes(props.userRole || ''))
const canSeeManagement = computed(() => ['admin', 'superadmin'].includes(props.userRole || ''))
const canSeeContent = computed(() => ['content_manager', 'superadmin'].includes(props.userRole || ''))
</script>

<template>
  <aside
    v-if="userRole"
    class="sidebar d-flex flex-column p-3 vh-100 position-fixed"
    :class="{ 'slim-mode': !isPinned }"
    style="background-color: var(--sidebar-bg); color: var(--sidebar-text-light)"
  >
    <RouterLink
      to="/catalog"
      class="d-flex align-items-center justify-content-center mb-4 text-decoration-none"
      style="color: var(--sidebar-text-light)"
    >
      <i class="bi bi-film fs-3 sidebar-icon" style="color: var(--sidebar-primary)"></i>
      <span class="fs-4 fw-bold sidebar-text ms-2">MishlenKino</span>
    </RouterLink>

    <ul class="nav nav-pills flex-column mb-auto">
      <li class="nav-item mb-2" v-if="userRole === 'user' && !currentUser?.active_subscription">
        <RouterLink
          to="/subscribe"
          class="nav-link text-dark fw-bold d-flex align-items-center rounded-3 shadow-sm"
          style="background-color: #ffc107 !important"
        >
          <i class="bi bi-star-fill sidebar-icon"></i>
          <span class="sidebar-text ms-2">Премиум доступ</span>
        </RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink
          to="/profile"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-person-circle sidebar-icon"></i>
          <span class="sidebar-text ms-2">Профиль</span>
        </RouterLink>
      </li>
      <li class="nav-item" v-if="canSeeUser">
        <RouterLink
          to="/catalog"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-grid sidebar-icon"></i>
          <span class="sidebar-text ms-2">Каталог</span>
        </RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink
          v-if="canSeeManagement"
          to="/admin/dashboard"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-speedometer2 sidebar-icon"></i>
          <span class="sidebar-text ms-2">Дашборд</span>
        </RouterLink>
      </li>
      <li v-if="canSeeManagement">
        <RouterLink
          to="/users"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-people sidebar-icon"></i>
          <span class="sidebar-text ms-2">Пользователи</span>
        </RouterLink>
      </li>
      <li v-if="canSeeContent">
        <RouterLink
          to="/content"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-collection-play sidebar-icon"></i>
          <span class="sidebar-text ms-2">Контент</span>
        </RouterLink>
      </li>
      <li v-if="canSeeContent">
        <RouterLink
          to="/advertising"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-badge-ad sidebar-icon"></i>
          <span class="sidebar-text ms-2">Реклама</span>
        </RouterLink>
      </li>
      <li v-if="canSeeContent">
        <RouterLink
          to="/tags"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-tags sidebar-icon"></i>
          <span class="sidebar-text ms-2">Теги</span>
        </RouterLink>
      </li>
      <li v-if="canSeeContent">
        <RouterLink
          to="/copyright-holders"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-shield-check sidebar-icon"></i>
          <span class="sidebar-text ms-2">Правообладатели</span>
        </RouterLink>
      </li>
      <li v-if="canSeeManagement">
        <RouterLink
          to="/subscriptions"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-card-checklist sidebar-icon"></i>
          <span class="sidebar-text ms-2">Подписки</span>
        </RouterLink>
      </li>
      <li v-if="canSeeManagement">
        <RouterLink
          to="/reports"
          class="nav-link text-white d-flex align-items-center"
          active-class="active"
          style="--bs-nav-pills-link-active-bg: var(--sidebar-primary)"
        >
          <i class="bi bi-bar-chart sidebar-icon"></i>
          <span class="sidebar-text ms-2">Отчеты</span>
        </RouterLink>
      </li>
    </ul>

    <hr style="border-color: var(--sidebar-border)" />

    <div class="status-indicator d-flex flex-column align-items-center align-items-md-start px-2">
      <small style="color: var(--sidebar-text-muted)" class="d-block mb-1 sidebar-text">Статус БД:</small>
      <div
        v-if="isDbConnected"
        style="color: var(--success-color)"
        class="d-flex align-items-center fw-bold small"
      >
        <i class="bi bi-check-circle sidebar-icon"></i>
        <span class="sidebar-text ms-2">Активна</span>
      </div>
      <div
        v-else
        style="color: var(--danger-color)"
        class="d-flex align-items-center fw-bold small"
      >
        <i class="bi bi-x-circle sidebar-icon"></i>
        <span class="sidebar-text ms-2">Недоступна</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  z-index: 65536;
  transition: width 0.3s ease;
  overflow-x: hidden;
  white-space: nowrap;
}

.sidebar.slim-mode:not(:hover) {
  width: 76px;
}

.sidebar.slim-mode:not(:hover) .sidebar-text {
  display: none;
}

.sidebar.slim-mode:not(:hover) .nav-link {
  padding-left: 0;
  padding-right: 0;
  justify-content: center;
}

.sidebar.slim-mode:not(:hover) .sidebar-icon {
  margin: 0 !important;
}

.sidebar.slim-mode:not(:hover) .status-indicator {
  align-items: center !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.sidebar-icon {
  font-size: 1.25rem;
  min-width: 28px;
  text-align: center;
}
</style>
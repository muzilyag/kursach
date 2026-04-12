<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { ApiService } from './services/api'

const isDbConnected = ref(false)

onMounted(async () => {
    try {
        await ApiService.checkHealth()
        isDbConnected.value = true
    } catch {
        isDbConnected.value = false
    }
})
</script>

<template>
  <div class="d-flex">
    <aside class="sidebar d-flex flex-column p-3 vh-100 position-fixed">
      <RouterLink to="/" class="d-flex align-items-center mb-4 text-white text-decoration-none">
        <i class="bi bi-film fs-3 me-2" style="color: var(--primary-color);"></i>
        <span class="fs-4 fw-bold">AdminPanel</span>
      </RouterLink>
      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item">
          <RouterLink to="/" class="nav-link text-white" active-class="active">
            <i class="bi bi-speedometer2 me-2"></i>
            Дашборд
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/users" class="nav-link text-white" active-class="active">
            <i class="bi bi-people me-2"></i>
            Пользователи
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/content" class="nav-link text-white" active-class="active">
            <i class="bi bi-collection-play me-2"></i>
            Контент
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/subscriptions" class="nav-link text-white" active-class="active">
            <i class="bi bi-card-checklist me-2"></i>
            Подписки
          </RouterLink>
        </li>
        <li>
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
            <div class="fw-bold text-dark">Администратор</div>
            <small class="text-muted">admin@cinema.ru</small>
          </div>
          <img src="https://ui-avatars.com/api/?name=Admin&background=8b7355&color=fff" alt="Admin" width="40" height="40" class="rounded-circle border border-2 border-primary-custom">
        </div>
      </header>

      <RouterView />
    </main>
  </div>
</template>
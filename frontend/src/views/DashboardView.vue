<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '../services/api'

const stats = ref({
  users: 0,
  content: 0,
  totalSubscriptions: 0,
  activeSubscriptions: 0,
  views: 0,
  totalRevenue: 0
})

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await ApiService.getStats()
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки статистики'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4">Дашборд</h2>
    
    <div v-if="loading" class="d-flex justify-content-center">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    
    <div v-else class="row g-4">
      <div class="col-md-4">
        <div class="card bg-primary text-white h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-people me-2"></i>Пользователи</h5>
            <h2 class="display-5 fw-bold">{{ stats.users }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-cash-stack me-2"></i>Выручка</h5>
            <h2 class="display-5 fw-bold">{{ stats.totalRevenue }} ₽</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-info text-white h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-play-circle me-2"></i>Всего просмотров</h5>
            <h2 class="display-5 fw-bold">{{ stats.views }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card bg-warning text-dark h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-film me-2"></i>Единиц контента</h5>
            <h2 class="display-5 fw-bold">{{ stats.content }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card bg-danger text-white h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-card-checklist me-2"></i>Активные подписки</h5>
            <h2 class="display-5 fw-bold">{{ stats.activeSubscriptions }} <span class="fs-5 fw-normal opacity-75">/ {{ stats.totalSubscriptions }}</span></h2>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
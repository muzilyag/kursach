<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ApiService, type IDashboardStats } from '../services/api'

const stats = ref<IDashboardStats | null>(null)
const isLoading = ref(true)
const errorMessage = ref('')

const fetchStats = async () => {
  try {
    stats.value = await ApiService.getStats()
  } catch (e: any) {
    errorMessage.value = e.message || 'Ошибка загрузки статистики'
  } finally {
    isLoading.value = false
  }
}

const totalContentCount = computed(() => {
  if (!stats.value?.breakdown?.content_types) return 0
  return stats.value.breakdown.content_types.reduce((acc, item) => acc + item.count, 0)
})

const totalPaymentAmount = computed(() => {
  if (!stats.value?.breakdown?.payment_methods) return 0
  return stats.value.breakdown.payment_methods.reduce((acc, item) => acc + parseFloat(item.amount), 0)
})

const getContentPercentage = (count: number) => {
  if (totalContentCount.value === 0) return 0
  return Math.round((count / totalContentCount.value) * 100)
}

const getPaymentPercentage = (amount: string) => {
  if (totalPaymentAmount.value === 0) return 0
  return Math.round((parseFloat(amount) / totalPaymentAmount.value) * 100)
}

onMounted(fetchStats)
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h3 fw-bold" style="color: var(--text-darker);">Панель управления</h1>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div v-else-if="stats">
      <div class="row g-4 mb-4">
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-3 me-3" style="background-color: rgba(139,115,85,0.1); color: var(--sidebar-primary);">
                <i class="bi bi-people fs-4"></i>
              </div>
              <div>
                <h6 class="text-muted small mb-1 fw-bold">Пользователи</h6>
                <h3 class="m-0 fw-bold" style="color: var(--text-darker);">{{ stats.total_users }}</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-3 me-3" style="background-color: rgba(40,167,69,0.1); color: #28a745;">
                <i class="bi bi-cash-coin fs-4"></i>
              </div>
              <div>
                <h6 class="text-muted small mb-1 fw-bold">Общая выручка</h6>
                <h3 class="m-0 fw-bold" style="color: var(--text-darker);">{{ parseFloat(stats.total_revenue).toLocaleString() }} ₽</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-3 me-3" style="background-color: rgba(0,123,255,0.1); color: #007bff;">
                <i class="bi bi-collection-play fs-4"></i>
              </div>
              <div>
                <h6 class="text-muted small mb-1 fw-bold">Медиаконтент</h6>
                <h3 class="m-0 fw-bold" style="color: var(--text-darker);">{{ stats.total_content }}</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-3 me-3" style="background-color: rgba(255,193,7,0.1); color: #ffc107;">
                <i class="bi bi-eye fs-4"></i>
              </div>
              <div>
                <h6 class="text-muted small mb-1 fw-bold">Всего просмотров</h6>
                <h3 class="m-0 fw-bold" style="color: var(--text-darker);">{{ stats.total_viewings }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-12 col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-2 me-3 bg-light text-dark"><i class="bi bi-bookmark-star fs-5"></i></div>
              <div>
                <h6 class="text-muted small mb-0 fw-bold">Доступные жанры</h6>
                <h4 class="m-0 fw-bold mt-1" style="color: var(--text-darker);">{{ stats.total_genres }}</h4>
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-2 me-3 bg-light text-dark"><i class="bi bi-tags fs-5"></i></div>
              <div>
                <h6 class="text-muted small mb-0 fw-bold">Поисковые теги</h6>
                <h4 class="m-0 fw-bold mt-1" style="color: var(--text-darker);">{{ stats.total_tags }}</h4>
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100" style="background-color: var(--card-bg);">
            <div class="d-flex align-items-center">
              <div class="badge p-2 me-3 bg-light text-dark"><i class="bi bi-shield-check fs-5"></i></div>
              <div>
                <h6 class="text-muted small mb-0 fw-bold">Правообладатели</h6>
                <h4 class="m-0 fw-bold mt-1" style="color: var(--text-darker);">{{ stats.total_copyright_holders }}</h4>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-12 col-lg-6">
          <div class="card border-0 shadow-sm p-4" style="background-color: var(--card-bg); border-radius: 16px;">
            <h5 class="fw-bold mb-4" style="color: var(--text-darker);">Распределение контента</h5>
            <div v-for="item in stats.breakdown.content_types" :key="item.type" class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold text-muted small">{{ item.type }}</span>
                <span class="fw-bold small" style="color: var(--text-darker);">{{ item.count }} шт. ({{ getContentPercentage(item.count) }}%)</span>
              </div>
              <div class="progress" style="height: 10px; background-color: var(--light-bg); border-radius: 5px;">
                <div class="progress-bar" role="progressbar" 
                     :style="{ width: getContentPercentage(item.count) + '%', backgroundColor: 'var(--sidebar-primary)' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="card border-0 shadow-sm p-4" style="background-color: var(--card-bg); border-radius: 16px;">
            <h5 class="fw-bold mb-4" style="color: var(--text-darker);">Методы оплаты</h5>
            <div v-for="item in stats.breakdown.payment_methods" :key="item.method" class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold text-muted small">{{ item.method.toUpperCase() }}</span>
                <span class="fw-bold small" style="color: var(--text-darker);">{{ parseFloat(item.amount).toLocaleString() }} ₽ ({{ getPaymentPercentage(item.amount) }}%)</span>
              </div>
              <div class="progress" style="height: 10px; background-color: var(--light-bg); border-radius: 5px;">
                <div class="progress-bar bg-success" role="progressbar" 
                     :style="{ width: getPaymentPercentage(item.amount) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ApiService } from '../services/api'

const stats = ref<any | null>(null)
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
  return stats.value.breakdown.content_types.reduce((acc: number, item: any) => acc + item.count, 0)
})

const totalPaymentAmount = computed(() => {
  if (!stats.value?.breakdown?.payment_methods) return 0
  return stats.value.breakdown.payment_methods.reduce((acc: number, item: any) => acc + parseFloat(item.amount), 0)
})

const totalTariffAmount = computed(() => {
  if (!stats.value?.breakdown?.revenue_by_tariffs) return 0
  return stats.value.breakdown.revenue_by_tariffs.reduce((acc: number, item: any) => acc + parseFloat(item.amount), 0)
})

const totalSubsCount = computed(() => {
  if (!stats.value?.breakdown?.subscriptions_status) return 0
  return stats.value.breakdown.subscriptions_status.active + stats.value.breakdown.subscriptions_status.expired
})

const maxRegistrationCount = computed(() => {
  if (!stats.value?.breakdown?.registrations_dynamics?.daily) return 1
  const counts = stats.value.breakdown.registrations_dynamics.daily.map((d: any) => d.count)
  return Math.max(...counts, 1)
})

const getContentPercentage = (count: number) => {
  if (totalContentCount.value === 0) return 0
  return Math.round((count / totalContentCount.value) * 100)
}

const getPaymentPercentage = (amount: string) => {
  if (totalPaymentAmount.value === 0) return 0
  return Math.round((parseFloat(amount) / totalPaymentAmount.value) * 100)
}

const getTariffPercentage = (amount: string) => {
  if (totalTariffAmount.value === 0) return 0
  return Math.round((parseFloat(amount) / totalTariffAmount.value) * 100)
}

const getSubPercentage = (count: number) => {
  if (totalSubsCount.value === 0) return 0
  return Math.round((count / totalSubsCount.value) * 100)
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
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

      <div class="row g-4 mb-4">
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

      <div class="row g-4 mb-4">
        <div class="col-12 col-lg-6">
          <div class="card border-0 shadow-sm p-4" style="background-color: var(--card-bg); border-radius: 16px;">
            <h5 class="fw-bold mb-4" style="color: var(--text-darker);">Статус подписок</h5>
            <div v-if="stats.breakdown.subscriptions_status" class="d-flex flex-column gap-3">
              <div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold text-muted small">АКТИВНЫЕ</span>
                  <span class="fw-bold small text-success">{{ stats.breakdown.subscriptions_status.active }} шт. ({{ getSubPercentage(stats.breakdown.subscriptions_status.active) }}%)</span>
                </div>
                <div class="progress" style="height: 10px; background-color: var(--light-bg); border-radius: 5px;">
                  <div class="progress-bar bg-success" role="progressbar" :style="{ width: getSubPercentage(stats.breakdown.subscriptions_status.active) + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold text-muted small">ИСТЕКШИЕ</span>
                  <span class="fw-bold small text-danger">{{ stats.breakdown.subscriptions_status.expired }} шт. ({{ getSubPercentage(stats.breakdown.subscriptions_status.expired) }}%)</span>
                </div>
                <div class="progress" style="height: 10px; background-color: var(--light-bg); border-radius: 5px;">
                  <div class="progress-bar bg-danger" role="progressbar" :style="{ width: getSubPercentage(stats.breakdown.subscriptions_status.expired) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="card border-0 shadow-sm p-4" style="background-color: var(--card-bg); border-radius: 16px;">
            <h5 class="fw-bold mb-4" style="color: var(--text-darker);">Выручка по тарифам</h5>
            <div v-for="item in stats.breakdown.revenue_by_tariffs" :key="item.tariff_name" class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold text-muted small">{{ item.tariff_name }} ({{ item.count }} шт.)</span>
                <span class="fw-bold small" style="color: var(--text-darker);">{{ parseFloat(item.amount).toLocaleString() }} ₽ ({{ getTariffPercentage(item.amount) }}%)</span>
              </div>
              <div class="progress" style="height: 10px; background-color: var(--light-bg); border-radius: 5px;">
                <div class="progress-bar bg-info" role="progressbar" :style="{ width: getTariffPercentage(item.amount) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm p-4" style="background-color: var(--card-bg); border-radius: 16px;">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold m-0" style="color: var(--text-darker);">Динамика регистраций за неделю</h5>
              <div v-if="stats.breakdown.registrations_dynamics" class="text-end">
                <span class="fs-4 fw-bold text-primary">+{{ stats.breakdown.registrations_dynamics.total_new_this_week }}</span>
                <span class="small text-muted ms-2">новых пользователей</span>
                <span v-if="stats.breakdown.registrations_dynamics.growth_percentage !== undefined" 
                      :class="['small ms-2 fw-bold', stats.breakdown.registrations_dynamics.growth_percentage >= 0 ? 'text-success' : 'text-danger']">
                  ({{ stats.breakdown.registrations_dynamics.growth_percentage >= 0 ? '+' : '' }}{{ stats.breakdown.registrations_dynamics.growth_percentage }}%)
                </span>
              </div>
            </div>
            <div v-if="stats.breakdown.registrations_dynamics?.daily" class="d-flex align-items-end justify-content-between pt-3" style="height: 150px;">
              <div v-for="day in stats.breakdown.registrations_dynamics.daily" :key="day.date" class="d-flex flex-column align-items-center flex-grow-1 mx-1">
                <span class="small fw-bold mb-2" style="color: var(--text-darker);">{{ day.count }}</span>
                <div class="w-100 rounded-top" 
                     :style="{ height: ((day.count / maxRegistrationCount) * 100) + 'px', minHeight: day.count > 0 ? '4px' : '0px', backgroundColor: 'var(--sidebar-primary)' }">
                </div>
                <span class="smallest text-muted mt-2 text-nowrap">{{ formatDate(day.date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
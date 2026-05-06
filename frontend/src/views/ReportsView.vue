<script setup lang="ts">
import { ref, computed } from 'vue'
import { ApiService } from '../services/api'

const reportTypes = [
  { id: 'seasonality', name: 'Сезонность спроса на жанры' },
  { id: 'activity', name: 'Активность пользователей' },
  { id: 'revenue', name: 'Доход от подписок' }
]

const selectedReport = ref('seasonality')
const loading = ref(false)
const reportData = ref<any[]>([])

const filterYear = ref(new Date().getFullYear())
const filterDate = ref(new Date().toISOString().split('T')[0])

const columns = computed(() => {
  if (selectedReport.value === 'seasonality') {
    return [
      { key: 'month', label: 'Месяц' },
      { key: 'genre_name', label: 'Жанр' },
      { key: 'total_views', label: 'Кол-во просмотров' }
    ]
  }
  if (selectedReport.value === 'activity') {
    return [
      { key: 'user_name', label: 'Пользователь' },
      { key: 'total_views', label: 'Всего просмотров' },
      { key: 'has_active_subscription', label: 'Статус подписки' }
    ]
  }
  if (selectedReport.value === 'revenue') {
    return [
      { key: 'subscribe_type_name', label: 'Тариф' },
      { key: 'subscriptions_count', label: 'Продано' },
      { key: 'total_revenue', label: 'Выручка' }
    ]
  }
  return []
})

const generate = async () => {
  loading.value = true
  reportData.value = []
  try {
    if (selectedReport.value === 'seasonality') {
      reportData.value = await ApiService.getSeasonalityReport(filterYear.value)
    } else if (selectedReport.value === 'activity') {
      reportData.value = await ApiService.getActivityReport()
    } else if (selectedReport.value === 'revenue') {
      reportData.value = await ApiService.getRevenueReport(filterDate.value ?? '')
    }
  } catch (e: any) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

const downloadCsv = () => {
  if (reportData.value.length === 0) return
  
  const headers = columns.value.map(c => c.label).join(',')
  const rows = reportData.value.map(item => 
    columns.value.map(c => {
      const val = item[c.key]
      return typeof val === 'boolean' ? (val ? 'Активна' : 'Нет') : val
    }).join(',')
  ).join('\n')
  
  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + headers + "\n" + rows
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `report_${selectedReport.value}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Аналитические отчёты</h2>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label small fw-bold text-secondary text-uppercase">Тип отчёта</label>
            <select v-model="selectedReport" class="form-select shadow-none" @change="reportData = []">
              <option v-for="type in reportTypes" :key="type.id" :value="type.id">
                {{ type.name }}
              </option>
            </select>
          </div>

          <div v-if="selectedReport === 'seasonality'" class="col-md-2">
            <label class="form-label small fw-bold text-secondary text-uppercase">Год</label>
            <input v-model.number="filterYear" type="number" class="form-control shadow-none" placeholder="2026">
          </div>

          <div v-if="selectedReport === 'revenue'" class="col-md-3">
            <label class="form-label small fw-bold text-secondary text-uppercase">Месяц (любое число)</label>
            <input v-model="filterDate" type="date" class="form-control shadow-none">
          </div>

          <div class="col-md-auto ms-auto d-flex gap-2">
            <button class="btn btn-primary px-4 shadow-sm" @click="generate" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Сформировать
            </button>
            <button class="btn btn-outline-secondary" @click="downloadCsv" :disabled="!reportData.length">
              <i class="bi bi-download me-2"></i>CSV
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="reportData.length" class="card shadow-sm border-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th v-for="col in columns" :key="col.key" class="py-3 border-0 text-secondary text-uppercase small">
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in reportData" :key="idx">
              <td v-for="col in columns" :key="col.key" class="py-3">
                <template v-if="col.key === 'has_active_subscription'">
                  <span class="badge" :class="row[col.key] ? 'bg-success-subtle text-success' : 'bg-light text-muted'">
                    {{ row[col.key] ? 'Активна' : 'Нет' }}
                  </span>
                </template>
                <template v-else-if="col.key === 'total_revenue'">
                  {{ row[col.key]?.toLocaleString() }} ₽
                </template>
                <template v-else>
                  {{ row[col.key] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="!loading" class="text-center py-5 bg-white rounded shadow-sm border">
      <i class="bi bi-file-earmark-bar-graph h1 text-light"></i>
      <p class="text-muted mt-2">Выберите параметры и нажмите «Сформировать»</p>
    </div>
  </div>
</template>

<style scoped>
.table thead th {
  font-weight: 600;
  letter-spacing: 0.5px;
}
</style>
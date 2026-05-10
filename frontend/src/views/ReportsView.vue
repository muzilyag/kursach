<script setup lang="ts">
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'
import Chart from 'chart.js/auto'

const reportTypes = [
  { id: 'seasonality', name: 'Сезонность спроса на жанры' },
  { id: 'activity', name: 'Активность пользователей' },
  { id: 'revenue', name: 'Доход от подписок' }
]

const selectedReport = ref('seasonality')
const loading = ref(false)
const downloadingFormat = ref<'csv' | 'pdf' | null>(null)
const reportData = ref<any[]>([])

const filterYear = ref(2023)
const startDate = ref('2023-01-01')
const endDate = ref('2023-12-31')

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const columns = computed(() => {
  if (reportData.value.length === 0) return []
  
  if (selectedReport.value === 'seasonality') {
    return Object.keys(reportData.value[0]).map(key => ({
      key: key,
      label: key === 'month' ? 'Месяц' : key
    }))
  }
  
  if (selectedReport.value === 'activity') {
    return [
      { key: 'Subscription', label: 'Тариф' },
      { key: 'Avg Time (min)', label: 'Ср. время (мин)' },
      { key: 'Unique Content', label: 'Контент (ед.)' }
    ]
  }
  
  if (selectedReport.value === 'revenue') {
    return [
      { key: 'Subscription', label: 'Тариф' },
      { key: 'Active Subs', label: 'Активные подписки' },
      { key: 'Revenue (RUB)', label: 'Выручка (₽)' }
    ]
  }
  
  return []
})

const updateChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (!chartCanvas.value || reportData.value.length === 0) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const type = selectedReport.value === 'revenue' ? 'pie' : 'bar'
  
  let data: any = { labels: [], datasets: [] }

  if (selectedReport.value === 'seasonality') {
    const months = reportData.value.map(d => d.month)
    const genres = Object.keys(reportData.value[0]).filter(k => k !== 'month')
    data.labels = months
    data.datasets = genres.map((genre, i) => ({
      label: genre,
      data: reportData.value.map(d => d[genre] || 0),
      backgroundColor: `hsla(${i * 50}, 70%, 60%, 0.8)`
    }))
  } else if (selectedReport.value === 'activity') {
    data.labels = reportData.value.map(d => d.Subscription)
    data.datasets = [{
      label: 'Среднее время (мин)',
      data: reportData.value.map(d => d['Avg Time (min)']),
      backgroundColor: '#3b82f6'
    }]
  } else if (selectedReport.value === 'revenue') {
    data.labels = reportData.value.map(d => d.Subscription)
    data.datasets = [{
      data: reportData.value.map(d => d['Revenue (RUB)']),
      backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']
    }]
  }

  chartInstance = new Chart(ctx, {
    type,
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })
}

const generate = async () => {
  loading.value = true
  reportData.value = []
  try {
    let response: any[] = []
    
    if (selectedReport.value === 'seasonality') {
      response = await ApiService.getSeasonalityReport(filterYear.value)
    } else if (selectedReport.value === 'activity') {
      response = await ApiService.getActivityReport()
    } else if (selectedReport.value === 'revenue') {
      response = await ApiService.getRevenueReport(startDate.value, endDate.value)
    }
    
    reportData.value = response
    await nextTick()
    updateChart()
  } catch (e: any) {
    alert('Ошибка: ' + e.message)
  } finally {
    loading.value = false
  }
}

const downloadReport = async (format: 'csv' | 'pdf') => {
  downloadingFormat.value = format
  try {
    let blob: Blob
    if (selectedReport.value === 'seasonality') {
      blob = await ApiService.exportSeasonalityReport(filterYear.value, format)
    } else if (selectedReport.value === 'activity') {
      blob = await ApiService.exportActivityReport(format)
    } else if (selectedReport.value === 'revenue') {
      blob = await ApiService.exportRevenueReport(startDate.value, endDate.value, format)
    }

    Utils.downloadFile(blob!, `report_${selectedReport.value}.${format}`)
  } catch (e: any) {
    alert('Ошибка при скачивании: ' + e.message)
  } finally {
    downloadingFormat.value = null
  }
}

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Аналитические отчёты</h2>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label small fw-bold text-secondary text-uppercase">Тип отчёта</label>
            <select v-model="selectedReport" class="form-select shadow-none" @change="reportData = []">
              <option v-for="type in reportTypes" :key="type.id" :value="type.id">
                {{ type.name }}
              </option>
            </select>
          </div>

          <div v-if="selectedReport === 'seasonality'" class="col-md-2">
            <label class="form-label small fw-bold text-secondary text-uppercase">Год</label>
            <input v-model.number="filterYear" type="number" class="form-control shadow-none">
          </div>

          <template v-if="selectedReport === 'revenue'">
            <div class="col-md-2">
              <label class="form-label small fw-bold text-secondary text-uppercase">Начало</label>
              <input v-model="startDate" type="date" class="form-control shadow-none">
            </div>
            <div class="col-md-2">
              <label class="form-label small fw-bold text-secondary text-uppercase">Конец</label>
              <input v-model="endDate" type="date" class="form-control shadow-none">
            </div>
          </template>

          <div class="col-md-auto ms-auto d-flex gap-2">
            <button class="btn btn-primary px-4 shadow-sm" @click="generate" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Сформировать
            </button>
            <button class="btn btn-outline-success" @click="downloadReport('csv')" :disabled="!reportData.length || downloadingFormat === 'csv'">
              <span v-if="downloadingFormat === 'csv'" class="spinner-border spinner-border-sm me-2"></span>
              CSV
            </button>
            <button class="btn btn-outline-danger" @click="downloadReport('pdf')" :disabled="!reportData.length || downloadingFormat === 'pdf'">
               <span v-if="downloadingFormat === 'pdf'" class="spinner-border spinner-border-sm me-2"></span>
              PDF
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="reportData.length" class="row">
      <div class="col-lg-7 mb-4">
        <div class="card shadow-sm border-0 overflow-hidden">
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
                    <template v-if="col.key === 'Revenue (RUB)'">
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
      </div>
      <div class="col-lg-5 mb-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-0 py-3">
            <h5 class="h6 mb-0 fw-bold text-secondary text-uppercase">Визуализация данных</h5>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <div style="width: 100%; height: 350px;">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="text-center py-5 bg-white rounded shadow-sm border">
      <i class="bi bi-graph-up h1 text-light"></i>
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
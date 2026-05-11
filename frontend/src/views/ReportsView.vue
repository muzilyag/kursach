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

const today = new Date()
const currentYear = today.getFullYear()
const currentDate = today.toISOString().split('T')[0]
const startOfYear = `${currentYear}-01-01`

const selectedReport = ref('seasonality')
const loading = ref(false)
const downloadingFormat = ref<'csv' | 'pdf' | null>(null)
const reportData = ref<any[]>([])

const filterYear = ref(currentYear)
const startDate = ref(startOfYear)
const endDate = ref(currentDate)

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const tableWidth = ref(60)
const isResizing = ref(false)

const columns = computed(() => {
  if (reportData.value.length === 0) return []
  
  if (selectedReport.value === 'seasonality') {
    return Object.keys(reportData.value[0]).map(key => ({
      key: key,
      label: key
    }))
  }
  
  if (selectedReport.value === 'activity') {
    return [
      { key: 'Подписка', label: 'Тариф' },
      { key: 'Среднее время (мин)', label: 'Ср. время (мин)' },
      { key: 'Уникальный контент', label: 'Контент (ед.)' }
    ]
  }
  
  if (selectedReport.value === 'revenue') {
    return [
      { key: 'Подписка', label: 'Тариф' },
      { key: 'Активные подписки', label: 'Активные подписки' },
      { key: 'Выручка (руб.)', label: 'Выручка (₽)' }
    ]
  }
  
  return []
})

const startResizing = () => {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopResizing)
  document.body.style.cursor = 'col-resize'
}

const stopResizing = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
  document.body.style.cursor = 'default'
  if (chartInstance) chartInstance.resize()
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isResizing.value) return
  const container = document.querySelector('.reports-layout')
  if (container) {
    const containerRect = container.getBoundingClientRect()
    const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100
    if (newWidth > 20 && newWidth < 80) {
      tableWidth.value = newWidth
    }
  }
}

const updateChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (!chartCanvas.value || reportData.value.length === 0) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  let type: any = 'bar'
  if (selectedReport.value === 'revenue') type = 'pie'
  if (selectedReport.value === 'seasonality') type = 'line'
  
  let data: any = { labels: [], datasets: [] }

  if (selectedReport.value === 'seasonality') {
    const months = reportData.value.map(d => d['Месяц'])
    const genres = Object.keys(reportData.value[0]).filter(k => k !== 'Месяц' && k !== 'Год')
    data.labels = months
    data.datasets = genres.map((genre, i) => ({
      label: genre,
      data: reportData.value.map(d => d[genre] || 0),
      backgroundColor: `hsla(${i * 50}, 70%, 60%, 0.5)`,
      borderColor: `hsla(${i * 50}, 70%, 60%, 1)`,
      borderWidth: 2,
      tension: 0.3,
      fill: false
    }))
  } else if (selectedReport.value === 'activity') {
    data.labels = reportData.value.map(d => d['Подписка'])
    data.datasets = [{
      label: 'Среднее время (мин)',
      data: reportData.value.map(d => d['Среднее время (мин)']),
      backgroundColor: '#3b82f6'
    }]
  } else if (selectedReport.value === 'revenue') {
    data.labels = reportData.value.map(d => d['Подписка'])
    data.datasets = [{
      data: reportData.value.map(d => d['Выручка (руб.)']),
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
      response = await ApiService.getRevenueReport(startDate.value || '', endDate.value || '')
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
      blob = await ApiService.exportRevenueReport(startDate.value || '', endDate.value || '', format)
    } else {
      throw new Error('Неизвестный тип отчета')
    }

    Utils.downloadFile(blob, `report_${selectedReport.value}.${format}`)
  } catch (e: any) {
    alert('Ошибка при скачивании: ' + e.message)
  } finally {
    downloadingFormat.value = null
  }
}

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
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

    <div v-if="reportData.length" class="reports-layout d-flex">
      <div class="table-container card shadow-sm border-0 overflow-hidden" :style="{ width: tableWidth + '%' }">
        <div class="table-responsive h-100">
          <table class="table table-hover mb-0 align-middle text-nowrap">
            <thead class="table-light sticky-top">
              <tr>
                <th v-for="col in columns" :key="col.key" class="py-3 border-0 text-secondary text-uppercase small">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportData" :key="idx">
                <td v-for="col in columns" :key="col.key" class="py-3">
                  <template v-if="col.key === 'Выручка (руб.)'">
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

      <div class="resizer" @mousedown="startResizing"></div>

      <div class="chart-container-wrapper card shadow-sm border-0 d-flex flex-column" :style="{ width: (100 - tableWidth) + '%' }">
        <div class="card-header bg-white border-0 py-3 flex-shrink-0">
          <h5 class="h6 mb-0 fw-bold text-secondary text-uppercase">Визуализация данных</h5>
        </div>
        <div class="card-body p-2 flex-grow-1" style="position: relative; min-height: 400px;">
          <div style="position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px;">
            <canvas ref="chartCanvas"></canvas>
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
.reports-layout {
  min-height: 500px;
  gap: 0;
  user-select: none;
}
.table-container {
  min-width: 0;
  height: 600px;
}
.chart-container-wrapper {
  min-width: 0;
  height: 600px;
}
.resizer {
  width: 12px;
  cursor: col-resize;
  background: transparent;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
}
.resizer::after {
  content: "";
  width: 2px;
  height: 40px;
  background: #dee2e6;
  border-radius: 2px;
}
.resizer:hover::after {
  background: #0d6efd;
  width: 4px;
}
.sticky-top {
  top: 0;
  z-index: 1;
}
</style>
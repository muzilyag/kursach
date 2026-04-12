<script setup lang="ts">
import { ref } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'

const reportData = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const startDate = ref(Utils.getDateDaysAgo(30))
const endDate = ref(new Date().toISOString().split('T')[0])

const generateReport = async () => {
  if (!startDate.value || !endDate.value) return
  loading.value = true
  error.value = ''
  try {
    reportData.value = await ApiService.getReport({
      startDate: startDate.value,
      endDate: endDate.value
    })
  } catch (e: any) {
    error.value = e.message || 'Ошибка генерации отчета'
  } finally {
    loading.value = false
  }
}

const exportToPDF = () => {
  const { jsPDF } = (window as any).jspdf
  const doc = new jsPDF()
  
  doc.setFont("helvetica")
  doc.text("Activity Report", 14, 15)
  doc.text(`Period: ${startDate.value} - ${endDate.value}`, 14, 25)

  const rows = reportData.value.map(row => [
    row['Тип подписки'],
    row['Количество пользователей'],
    row['Средний прогресс просмотра (%)'] + '%',
    row['Всего просмотров'],
    row['Среднее время (мин)']
  ])

  if ((window as any).jspdf.plugin.autotable) {
    (doc as any).autoTable({
      startY: 30,
      head: [['Type', 'Users', 'Progress', 'Views', 'Time (min)']],
      body: rows,
    })
    doc.save(`report_${startDate.value}_${endDate.value}.pdf`)
  } else {
    alert("jsPDF AutoTable is not loaded")
  }
}
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4"><i class="bi bi-graph-up me-2"></i>Аналитические отчеты</h2>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3">Отчет по активности пользователей</h5>
        <div class="row align-items-end g-3">
          <div class="col-md-4">
            <label class="form-label">Период с:</label>
            <input type="date" class="form-control" v-model="startDate">
          </div>
          <div class="col-md-4">
            <label class="form-label">По:</label>
            <input type="date" class="form-control" v-model="endDate">
          </div>
          <div class="col-md-4">
            <button class="btn btn-primary w-100" @click="generateReport" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Сформировать отчёт
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="reportData.length > 0" class="card shadow-sm">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h6 class="mb-0">Результаты отчета</h6>
        <button class="btn btn-sm btn-outline-danger" @click="exportToPDF">
          <i class="bi bi-file-earmark-pdf me-2"></i>Экспорт в PDF
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover mb-0" id="report-table">
          <thead class="table-dark">
            <tr>
              <th>Тип подписки</th>
              <th>Пользователи</th>
              <th>Прогресс (%)</th>
              <th>Просмотры</th>
              <th>Время (мин)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in reportData" :key="idx">
              <td class="fw-bold">{{ row['Тип подписки'] }}</td>
              <td>{{ row['Количество пользователей'] }}</td>
              <td>{{ row['Средний прогресс просмотра (%)'] }}%</td>
              <td>{{ row['Всего просмотров'] }}</td>
              <td>{{ row['Среднее время (мин)'] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
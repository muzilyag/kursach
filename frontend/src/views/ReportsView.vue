<script setup lang="ts">
import { ref } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'
import DataTable from '../components/DataTable.vue'

const reportData = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const startDate = ref(Utils.getDateDaysAgo(30))
const endDate = ref(new Date().toISOString().split('T')[0])

const columns = [
  { key: 'Тип подписки', label: 'Тариф' },
  { key: 'Количество пользователей', label: 'Пользователи' },
  { key: 'Средний прогресс просмотра (%)', label: 'Прогресс (%)' },
  { key: 'Всего просмотров', label: 'Просмотры' },
  { key: 'Общее время просмотра (мин)', label: 'Время (мин)' }
]

const generate = async () => {
  loading.value = true
  error.value = ''
  try {
    reportData.value = await ApiService.getReport({ startDate: startDate.value, endDate: endDate.value })
  } catch (e: any) { error.value = e.message }
  finally { loading.value = false }
}

const exportPDF = () => {
  const { jsPDF } = (window as any).jspdf
  const doc = new jsPDF()
  doc.text("Activity Report", 14, 15)
  doc.autoTable({ html: '#report-table', startY: 25 })
  doc.save(`report_${startDate.value}_${endDate.value}.pdf`)
}
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4"><i class="bi bi-bar-chart me-2"></i>Отчеты</h2>
    <div class="card shadow-sm mb-4">
      <div class="card-body d-flex gap-3 align-items-end">
        <div><label class="form-label small">От</label><input type="date" v-model="startDate" class="form-control"></div>
        <div><label class="form-label small">До</label><input type="date" v-model="endDate" class="form-control"></div>
        <button class="btn btn-primary" @click="generate" :disabled="loading">Сформировать</button>
      </div>
    </div>

    <div v-if="reportData.length > 0" class="card shadow-sm">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h6 class="mb-0">Результаты</h6>
        <button class="btn btn-sm btn-outline-danger" @click="exportPDF">PDF</button>
      </div>
      <DataTable :columns="columns" :items="reportData" id="report-table" />
    </div>
  </div>
</template>
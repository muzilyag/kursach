<script setup lang="ts">
import { ref } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'

const reportData = ref<any[]>([])
const loading = ref(false)
const startDate = ref(Utils.getDateDaysAgo(30))
const endDate = ref(new Date().toISOString().split('T')[0] as string)

const generate = async () => {
  loading.value = true
  try {
    reportData.value = await ApiService.getReport({ startDate: startDate.value, endDate: endDate.value })
  } catch (e: any) {
    alert(e.message)
  } finally { loading.value = false }
}
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4">Аналитический отчет</h2>
    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body d-flex gap-3 align-items-end bg-white rounded">
        <div><label class="form-label small fw-bold text-secondary">Начало</label><input type="date" v-model="startDate" class="form-control"></div>
        <div><label class="form-label small fw-bold text-secondary">Конец</label><input type="date" v-model="endDate" class="form-control"></div>
        <button class="btn btn-primary shadow-sm" @click="generate" :disabled="loading">Сформировать</button>
      </div>
    </div>

    <div v-if="reportData.length" class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th v-for="key in Object.keys(reportData[0])" :key="key">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in reportData" :key="idx">
              <td v-for="val in Object.values(row)" :key="val as string">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
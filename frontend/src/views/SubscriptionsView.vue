<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'

const subscriptions = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const filters = reactive({
  startDate: Utils.getDateDaysAgo(30),
  endDate: new Date().toISOString().split('T')[0]
})

const fetchSubscriptions = async () => {
  loading.value = true
  try {
    const response = await ApiService.getSubscriptions({
      startDate: filters.startDate,
      endDate: filters.endDate
    })
    subscriptions.value = response.subscriptions || []
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки подписок'
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  filters.startDate = Utils.getDateDaysAgo(30)
  filters.endDate = new Date().toISOString().split('T')[0]
  fetchSubscriptions()
}

onMounted(() => {
  fetchSubscriptions()
})
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4"><i class="bi bi-credit-card me-2"></i>Управление подписками</h2>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label">Дата начала:</label>
            <input type="date" class="form-control" v-model="filters.startDate">
          </div>
          <div class="col-md-4">
            <label class="form-label">Дата окончания:</label>
            <input type="date" class="form-control" v-model="filters.endDate">
          </div>
          <div class="col-md-4 d-flex">
            <button class="btn btn-primary w-100 me-2" @click="fetchSubscriptions">Применить</button>
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">Сброс</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Пользователь</th>
              <th>Тариф</th>
              <th>Дата начала</th>
              <th>Дата окончания</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(sub, index) in subscriptions" :key="index">
              <td class="fw-medium">{{ sub['Пользователь'] }}</td>
              <td>{{ sub['Тип подписки'] || sub['Тариф'] }}</td>
              <td>{{ Utils.formatDate(sub['Дата начала']) }}</td>
              <td>{{ Utils.formatDate(sub['Дата окончания']) }}</td>
              <td>
                <span class="badge" :class="sub['Статус'] === 'Активна' ? 'bg-success' : 'bg-secondary'">
                  {{ sub['Статус'] }}
                </span>
              </td>
            </tr>
            <tr v-if="subscriptions.length === 0">
              <td colspan="5" class="text-center py-4 text-muted">Ничего не найдено</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
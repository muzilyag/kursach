<script setup lang="ts">
import { ApiService } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'

const columns = [
  { key: 'user_name', label: 'Пользователь', sortable: true },
  { key: 'subscribe_type_name', label: 'Тариф', sortable: true },
  { key: 'subscribe_start', label: 'Начало', sortable: true },
  { key: 'subscribe_finish', label: 'Окончание', sortable: true },
  { key: 'status', label: 'Статус' }
]

const { items, loading, error, params, load, handleSort } = useDataTable(
  ApiService.getSubscriptions.bind(ApiService),
  { 
    startDate: Utils.getDateDaysAgo(30), 
    endDate: new Date().toISOString().split('T')[0],
    sort: 'subscribe_start',
    order: 'desc',
    search: ''
  }
)
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4"><i class="bi bi-credit-card me-2"></i>Управление подписками</h2>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <input v-model="params.search" type="text" class="form-control" placeholder="Поиск пользователя..." @keyup.enter="load">
          </div>
          <div class="col-md-3">
            <input v-model="params.startDate" type="date" class="form-control">
          </div>
          <div class="col-md-3">
            <input v-model="params.endDate" type="date" class="form-control">
          </div>
          <div class="col-md-2 d-flex gap-2">
            <button class="btn btn-primary w-100" @click="load">
              Найти
            </button>
            <button class="btn btn-outline-secondary w-100" @click="params.search = ''; params.startDate = ''; params.endDate = ''; load()">
              Сбросить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    
    <div v-else class="card shadow-sm">
      <DataTable 
        :columns="columns" 
        :items="items"
        :sort-config="{ key: params.sort, order: params.order }"
        @sort="handleSort"
      >
        <template #cell-user_name="{ item }">
          <span class="fw-medium">{{ item['Пользователь'] }}</span>
        </template>
        
        <template #cell-subscribe_type_name="{ item }">
          <span class="badge bg-secondary">{{ item['Тип подписки'] }}</span>
        </template>

        <template #cell-subscribe_start="{ item }">
          {{ Utils.formatDate(item['Дата начала']) }}
        </template>
        
        <template #cell-subscribe_finish="{ item }">
          {{ Utils.formatDate(item['Дата окончания']) }}
        </template>
        
        <template #cell-status="{ item }">
          <span class="badge" :class="item['Статус'] === 'Активна' ? 'bg-success' : 'bg-danger'">
            {{ item['Статус'] }}
          </span>
        </template>
      </DataTable>
    </div>
  </div>
</template>
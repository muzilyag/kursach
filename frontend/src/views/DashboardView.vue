<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IDashboardStats } from '../services/api'

const stats = ref<IDashboardStats>({
  users: 0, content: 0, totalSubscriptions: 0, activeSubscriptions: 0, views: 0, totalRevenue: 0
})
const loading = ref(true)

const loadData = async () => {
  loading.value = true
  try {
    stats.value = await ApiService.getStats()
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

onMounted(loadData)
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4" style="color: var(--text-darker);">Обзор платформы</h2>
    
    <div v-if="loading" class="text-center p-5">
      <div class="spinner-border" style="color: var(--sidebar-primary);"></div>
    </div>
    
    <div v-else class="row g-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--sidebar-primary); color: var(--sidebar-text-light);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6>Пользователи</h6>
              <h3>{{ stats.users }}</h3>
            </div>
            <i class="bi bi-people fs-1 opacity-50"></i>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--success-color); color: var(--text-darker);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6>Активные подписки</h6>
              <h3>{{ stats.activeSubscriptions }}</h3>
            </div>
            <i class="bi bi-patch-check fs-1 opacity-50"></i>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100 p-3" style="background-color: var(--sidebar-bg); color: var(--sidebar-text-light);">
          <div class="card-body d-flex justify-content-between">
            <div>
              <h6>Выручка</h6>
              <h3>{{ stats.totalRevenue }} ₽</h3>
            </div>
            <i class="bi bi-currency-dollar fs-1 opacity-50"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
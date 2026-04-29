<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IDashboardStats } from '../services/api'

const stats = ref<IDashboardStats>({
  users: 0,
  content: 0,
  totalSubscriptions: 0,
  activeSubscriptions: 0,
  views: 0,
  totalRevenue: 0
})

const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await ApiService.getStats()
  } catch (e) {}
  finally { loading.value = false }
})
</script>

<template>
  <div class="container-fluid">
    <h2 class="mb-4">Обзор платформы</h2>
    <div v-if="loading" class="text-center p-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-primary text-white">
          <div class="card-body">
            <h6>Пользователи</h6>
            <h3>{{ stats.users }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-success text-white">
          <div class="card-body">
            <h6>Активные подписки</h6>
            <h3>{{ stats.activeSubscriptions }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-dark text-white">
          <div class="card-body">
            <h6>Выручка</h6>
            <h3>{{ stats.totalRevenue }} ₽</h3>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ApiService } from '../services/api'

const handleLogout = () => {
  ApiService.logout()
}
</script>

<template>
  <div
    class="client-stub container d-flex flex-column align-items-center justify-content-center vh-100 text-center"
  >
    <div class="mb-4">
      <i class="bi bi-film text-primary" style="font-size: 5rem"></i>
    </div>
    <h1 class="fw-bold mb-3">Добро пожаловать в Кинотеатр</h1>
    <p class="text-muted fs-5 mb-5" style="max-width: 600px">
      Это клиентская часть приложения. В данный момент она находится в разработке. Админ-панель
      доступна только для администраторов и контент-менеджеров.
    </p>
    <button @click="handleLogout" class="btn btn-outline-danger px-4 py-2 fw-bold">
      <i class="bi bi-box-arrow-right me-2"></i>Выйти из аккаунта
    </button>
  </div>
</template>

<style scoped>
.client-stub {
  background-color: #f8f9fa;
}
</style>

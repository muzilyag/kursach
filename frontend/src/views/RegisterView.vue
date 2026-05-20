<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiService } from '../services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  user_name: '',
  user_email: '',
  user_birth_date: '',
  user_password: '',
  user_role: 'user'
})

const roles = [
  { value: 'user', label: 'Обычный пользователь' },
  { value: 'content_manager', label: 'Контент-менеджер' }
]

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await ApiService.register(form)
    router.push('/login')
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container d-flex align-items-center justify-content-center vh-100">
    <div class="card shadow-lg border-0 p-4" style="max-width: 450px; width: 100%">
      <div class="text-center mb-4">
        <h1 class="h3 fw-bold">Регистрация</h1>
        <p class="text-muted">Создание учетной записи</p>
      </div>

      <div v-if="error" class="alert alert-danger py-2 small mb-3">
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Имя пользователя</label>
          <input
            v-model="form.user_name"
            type="text"
            class="form-control shadow-none"
            required
            placeholder="IvanIvanov"
          />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Email</label>
          <input
            v-model="form.user_email"
            type="email"
            class="form-control shadow-none"
            required
            placeholder="ivan@example.com"
          />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Роль в системе</label>
          <select v-model="form.user_role" class="form-select shadow-none">
            <option v-for="role in roles" :key="role.value" :value="role.value">
              {{ role.label }}
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Дата рождения</label>
          <input
            v-model="form.user_birth_date"
            type="date"
            class="form-control shadow-none"
            required
          />
        </div>
        <div class="mb-4">
          <label class="form-label small fw-bold text-uppercase">Пароль</label>
          <input
            v-model="form.user_password"
            type="password"
            class="form-control shadow-none"
            required
            placeholder="strongpassword123"
          />
        </div>
        <button type="submit" class="btn btn-success w-100 py-2 fw-bold" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Создать аккаунт
        </button>
      </form>

      <div class="text-center mt-4">
        <p class="small text-muted mb-0">
          Уже есть аккаунт?
          <router-link to="/login" class="text-decoration-none fw-bold">Войти</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

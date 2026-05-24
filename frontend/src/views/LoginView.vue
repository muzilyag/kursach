<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiService } from '../services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  identifier: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await ApiService.login(form)
    const role = ApiService.getRoleFromToken()
    if (role === 'superadmin') {
      router.push('/users')
    } else if (role === 'admin') {
      router.push('/dashboard')
    } else if (role === 'content_manager') {
      router.push('/content')
    } else {
      router.push('/catalog')
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container d-flex align-items-center justify-content-center vh-100">
    <div class="card shadow-lg border-0 p-4" style="max-width: 400px; width: 100%">
      <div class="text-center mb-4">
        <h1 class="h3 fw-bold">Вход в систему</h1>
        <p class="text-muted">Панель управления кинотеатром</p>
      </div>

      <div v-if="error" class="alert alert-danger py-2 small mb-3">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Email или Логин</label>
          <input
            v-model="form.identifier"
            type="text"
            class="form-control shadow-none"
            required
            placeholder="example@mail.ru"
          />
        </div>
        <div class="mb-4">
          <label class="form-label small fw-bold text-uppercase">Пароль</label>
          <input
            v-model="form.password"
            type="password"
            class="form-control shadow-none"
            required
            placeholder="••••••••"
          />
        </div>
        <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Войти
        </button>
      </form>

      <div class="text-center mt-4">
        <p class="small text-muted mb-0">
          Нет аккаунта?
          <router-link to="/register" class="text-decoration-none fw-bold"
            >Зарегистрироваться</router-link
          >
        </p>
      </div>
    </div>
  </div>
</template>
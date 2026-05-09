<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService, type IUser } from '../services/api'

const user = ref<IUser | null>(null)
const isLoading = ref(true)
const isSaving = ref(false)
const isChangingPassword = ref(false)
const message = ref({ text: '', type: '' })
const pwdMessage = ref({ text: '', type: '' })

const formData = ref({
  user_name: '',
  user_email: '',
  user_birth_date: ''
})

const pwdData = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const loadProfile = async () => {
  try {
    const data = await ApiService.getMe()
    user.value = data
    formData.value = {
      user_name: data.user_name,
      user_email: data.user_email,
      user_birth_date: data.user_birth_date?.split('T')[0] || ''
    }
  } catch (e: any) {
    message.value = { text: 'Ошибка загрузки профиля', type: 'danger' }
  } finally {
    isLoading.value = false
  }
}

const handleUpdate = async () => {
  if (!user.value) return
  isSaving.value = true
  message.value = { text: '', type: '' }
  try {
    await ApiService.updateMe(formData.value)
    message.value = { text: 'Данные успешно обновлены', type: 'success' }
    await loadProfile()
  } catch (e: any) {
    message.value = { text: e.message || 'Ошибка обновления', type: 'danger' }
  } finally {
    isSaving.value = false
  }
}

const handleChangePassword = async () => {
  if (pwdData.value.new_password !== pwdData.value.confirm_password) {
    pwdMessage.value = { text: 'Пароли не совпадают', type: 'danger' }
    return
  }
  isChangingPassword.value = true
  pwdMessage.value = { text: '', type: '' }
  try {
    await ApiService.changePassword({
      old_password: pwdData.value.old_password,
      new_password: pwdData.value.new_password
    })
    pwdMessage.value = { text: 'Пароль успешно изменен', type: 'success' }
    pwdData.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e: any) {
    pwdMessage.value = { text: e.message || 'Ошибка смены пароля', type: 'danger' }
  } finally {
    isChangingPassword.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="container-fluid">
    <div class="row justify-content-center g-4">
      <div class="col-md-8 col-lg-6">
        <div class="card border-0 shadow-sm mb-4" style="background-color: var(--card-bg);">
          <div class="card-body p-4">
            <div class="d-flex align-items-center mb-4">
              <img :src="`https://ui-avatars.com/api/?name=${user?.user_name || 'U'}&background=8b7355&color=fff&size=128`" 
                   class="rounded-circle me-4 border" width="80" height="80" style="border-color: var(--border-color) !important;">
              <div>
                <h3 class="mb-1" style="color: var(--text-darker);">Личный кабинет</h3>
                <p class="text-muted mb-0">Основные данные</p>
              </div>
            </div>

            <div v-if="message.text" :class="`alert alert-${message.type} mb-4`" role="alert">
              {{ message.text }}
            </div>

            <form v-if="!isLoading" @submit.prevent="handleUpdate">
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Имя пользователя</label>
                <input v-model="formData.user_name" type="text" class="form-control shadow-none" required 
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Email</label>
                <input v-model="formData.user_email" type="email" class="form-control shadow-none" required
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="mb-4">
                <label class="form-label small fw-bold text-muted">Дата рождения</label>
                <input v-model="formData.user_birth_date" type="date" class="form-control shadow-none"
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary py-2 fw-bold" :disabled="isSaving"
                        style="background-color: var(--sidebar-primary); border: none;">
                  <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
                  Сохранить изменения
                </button>
              </div>
            </form>
            <div v-else class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm mb-4" style="background-color: var(--card-bg);">
          <div class="card-body p-4">
            <h5 class="mb-4" style="color: var(--text-darker);">Безопасность</h5>
            <div v-if="pwdMessage.text" :class="`alert alert-${pwdMessage.type} mb-4`" role="alert">
              {{ pwdMessage.text }}
            </div>
            <form @submit.prevent="handleChangePassword">
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Текущий пароль</label>
                <input v-model="pwdData.old_password" type="password" class="form-control shadow-none" required
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Новый пароль</label>
                <input v-model="pwdData.new_password" type="password" class="form-control shadow-none" required
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="mb-4">
                <label class="form-label small fw-bold text-muted">Подтвердите пароль</label>
                <input v-model="pwdData.confirm_password" type="password" class="form-control shadow-none" required
                       style="background-color: var(--light-bg); border-color: var(--border-color);">
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-outline-danger py-2 fw-bold" :disabled="isChangingPassword">
                  <span v-if="isChangingPassword" class="spinner-border spinner-border-sm me-2"></span>
                  Обновить пароль
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="card border-0 shadow-sm mt-4" style="background-color: var(--card-bg);">
          <div class="card-body p-4">
            <h5 class="mb-3" style="color: var(--text-darker);">Данные аккаунта</h5>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">Дата регистрации:</span>
              <span class="fw-bold" style="color: var(--text-darker);">{{ user?.user_registration_date ? new Date(user.user_registration_date).toLocaleDateString() : '—' }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span class="text-muted">Роль:</span>
              <span class="badge" style="background-color: var(--sidebar-primary);">{{ user?.user_role }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
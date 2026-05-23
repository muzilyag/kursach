<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ApiService, type IUser } from '../services/api'

const router = useRouter()
const user = ref<IUser | null>(null)
const isLoading = ref(true)
const isSaving = ref(false)
const isChangingPassword = ref(false)
const isDeleting = ref(false)
const isCancelling = ref(false)
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
  } catch {
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

const handleCancelSubscription = async () => {
  if (!user.value || !user.value.active_subscription) return
  if (confirm('Вы уверены, что хотите отменить подписку? Она будет активна до конца оплаченного периода.')) {
    isCancelling.value = true
    try {
      await ApiService.cancelSubscription(
        user.value.user_id,
        user.value.active_subscription.subscribe_type_id,
        user.value.active_subscription.subscribe_finish
      )
      alert('Подписка успешно отменена!')
      await loadProfile()
    } catch {
      alert('Ошибка при отмене подписки')
    } finally {
      isCancelling.value = false
    }
  }
}

const handleDeleteAccount = async () => {
  if (confirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо.')) {
    isDeleting.value = true
    try {
      await ApiService.deleteMe()
      ApiService.logout()
    } catch {
      alert('Ошибка при удалении аккаунта')
    } finally {
      isDeleting.value = false
    }
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="container-fluid">
    <div class="row justify-content-center g-4">
      <div class="col-md-8 col-lg-6">
        
        <div
          v-if="user?.user_role === 'user' || user?.user_role === 'superadmin'"
          class="card border-0 shadow-sm mb-4 overflow-hidden"
          style="background-color: var(--card-bg); border-radius: 16px"
        >
          <div class="card-body p-0">
            <div
              class="p-4"
              :style="
                user?.active_subscription
                  ? 'background: linear-gradient(45deg, #8b7355, #a68d6d); color: white;'
                  : 'background: #f8f9fa;'
              "
            >
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="mb-1 fw-bold" :class="{ 'text-dark': !user?.active_subscription }">
                    Статус подписки
                  </h5>
                  <div v-if="user?.active_subscription">
                    <span class="badge bg-white text-dark mb-2">{{
                      user.active_subscription.subscribe_type_name
                    }}</span>
                    <p class="small mb-0 opacity-75">
                      Активна до:
                      {{ new Date(user.active_subscription.subscribe_finish).toLocaleDateString() }}
                    </p>
                    <div class="mt-3">
                      <button
                        @click="handleCancelSubscription"
                        :disabled="isCancelling"
                        class="btn btn-sm btn-outline-light px-3 rounded-pill fw-semibold"
                      >
                        <span v-if="isCancelling" class="spinner-border spinner-border-sm me-1"></span>
                        Отменить подписку
                      </button>
                    </div>
                  </div>
                  <div v-else>
                    <p class="text-muted mb-0">Подписка не активна</p>
                  </div>
                </div>
                <div class="d-flex flex-column align-items-end gap-2">
                  <RouterLink
                    to="/subscribe"
                    class="btn btn-light fw-bold rounded-pill px-4 shadow-sm"
                  >
                    {{ user?.active_subscription ? 'Сменить тариф' : 'Оформить' }}
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm mb-4" style="background-color: var(--card-bg)">
          <div class="card-body p-4">
            <div class="d-flex align-items-center mb-4">
              <img
                :src="`https://ui-avatars.com/api/?name=${user?.user_name || 'U'}&background=8b7355&color=fff&size=128`"
                class="rounded-circle me-4 border"
                width="80"
                height="80"
                style="border-color: var(--border-color) !important"
              />
              <div>
                <h3 class="mb-1" style="color: var(--text-darker)">Личный кабинет</h3>
                <p class="text-muted mb-0">Основные данные</p>
              </div>
            </div>

            <div v-if="message.text" :class="`alert alert-${message.type} mb-4`" role="alert">
              {{ message.text }}
            </div>

            <form v-if="!isLoading" @submit.prevent="handleUpdate">
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Имя пользователя</label>
                <input
                  v-model="formData.user_name"
                  type="text"
                  class="form-control shadow-none"
                  required
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Email</label>
                <input
                  v-model="formData.user_email"
                  type="email"
                  class="form-control shadow-none"
                  required
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="mb-4">
                <label class="form-label small fw-bold text-muted">Дата рождения</label>
                <input
                  v-model="formData.user_birth_date"
                  type="date"
                  class="form-control shadow-none"
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-primary py-2 fw-bold"
                  :disabled="isSaving"
                  style="background-color: var(--sidebar-primary); border: none"
                >
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

        <div class="card border-0 shadow-sm mb-4" style="background-color: var(--card-bg)">
          <div class="card-body p-4">
            <h5 class="mb-4" style="color: var(--text-darker)">Безопасность</h5>
            <div v-if="pwdMessage.text" :class="`alert alert-${pwdMessage.type} mb-4`" role="alert">
              {{ pwdMessage.text }}
            </div>
            <form @submit.prevent="handleChangePassword">
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Текущий пароль</label>
                <input
                  v-model="pwdData.old_password"
                  type="password"
                  class="form-control shadow-none"
                  required
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Новый пароль</label>
                <input
                  v-model="pwdData.new_password"
                  type="password"
                  class="form-control shadow-none"
                  required
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="mb-4">
                <label class="form-label small fw-bold text-muted">Подтвердите пароль</label>
                <input
                  v-model="pwdData.confirm_password"
                  type="password"
                  class="form-control shadow-none"
                  required
                  style="background-color: var(--light-bg); border-color: var(--border-color)"
                />
              </div>
              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-outline-danger py-2 fw-bold"
                  :disabled="isChangingPassword"
                >
                  <span
                    v-if="isChangingPassword"
                    class="spinner-border spinner-border-sm me-2"
                  ></span>
                  Обновить пароль
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="card border-0 shadow-sm mt-4 mb-4" style="background-color: var(--card-bg)">
          <div class="card-body p-4">
            <h5 class="mb-4 text-danger">Опасная зона</h5>
            <button class="btn btn-outline-danger w-100" :disabled="isDeleting" @click="handleDeleteAccount">
              {{ isDeleting ? 'Удаление...' : 'Удалить аккаунт' }}
            </button>
          </div>
        </div>

        <div class="card border-0 shadow-sm mt-4" style="background-color: var(--card-bg)">
          <div class="card-body p-4">
            <h5 class="mb-3" style="color: var(--text-darker)">Данные аккаунта</h5>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">Дата регистрации:</span>
              <span class="fw-bold" style="color: var(--text-darker)">{{
                user?.user_registration_date
                  ? new Date(user.user_registration_date).toLocaleDateString()
                  : '—'
              }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span class="text-muted">Роль:</span>
              <span class="badge" style="background-color: var(--sidebar-primary)">{{
                user?.user_role
              }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
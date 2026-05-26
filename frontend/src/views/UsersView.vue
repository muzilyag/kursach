<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { IUser, IUserCreate } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'user_name', label: 'ФИО', sortable: true },
  { key: 'user_email', label: 'Email', sortable: true },
  { key: 'user_role', label: 'Роль', sortable: true },
  { key: 'user_birth_date', label: 'Возраст', sortable: true },
  { key: 'user_registration_date', label: 'Регистрация', sortable: true }
]

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getUsers(p),
  {
    sort: 'user_id',
    order: 'asc',
    roles: ['user'],
    limit: Config.pagination.itemsPerPage
  }
)

const showModal = ref(false)
const isEditing = ref(false)
const currentUserRole = ref<string | null>(null)

const userForm = reactive<IUserCreate & { user_id?: number; user_role: string; user_password?: string }>({
  user_name: '',
  user_email: '',
  user_role: 'user',
  user_birth_date: '',
  user_registration_date: '',
  user_password: ''
})

const openModal = (user: IUser | null = null) => {
  if (user && user.user_role === 'superadmin') return
  if (user && user.user_role === 'admin' && currentUserRole.value !== 'superadmin') return

  isEditing.value = !!user
  if (user) {
    Object.assign(userForm, {
      ...user,
      user_role: user.user_role || 'user',
      user_password: ''
    })
  } else {
    Object.assign(userForm, {
      user_id: undefined,
      user_name: '',
      user_email: '',
      user_role: 'user',
      user_birth_date: '',
      user_registration_date: new Date().toISOString().split('T')[0],
      user_password: ''
    })
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveUser = async () => {
  try {
    if (isEditing.value && userForm.user_id) {
      const { user_password, ...updateData } = userForm
      await ApiService.updateUser(userForm.user_id, updateData)
    } else {
      await ApiService.createUser(userForm)
    }
    closeModal()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteUser = async (user: IUser) => {
  if (user.user_role === 'superadmin') return
  if (user.user_role === 'admin' && currentUserRole.value !== 'superadmin') return

  if (confirm('Удалить пользователя?')) {
    try {
      await ApiService.deleteUser(user.user_id)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

watch(
  () => params.roles,
  () => {
    params.page = 1
    load()
  },
  { deep: true }
)

onMounted(() => {
  currentUserRole.value = ApiService.getRoleFromToken()
  load()
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Пользователи</h2>
      <button class="btn btn-primary d-flex align-items-center" @click="openModal()">
        <i class="bi bi-person-plus me-2"></i>Добавить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3 border-bottom">
        <div class="row g-3 align-items-center">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"
                ><i class="bi bi-search"></i
              ></span>
              <input
                v-model="params.search"
                @input="load"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Поиск..."
              />
            </div>
          </div>

          <div class="col-md-8">
            <div class="d-flex gap-3 flex-wrap align-items-center">
              <span class="small fw-bold text-muted text-uppercase">Фильтр ролей:</span>
              <div class="form-check form-check-inline m-0">
                <input
                  v-model="params.roles"
                  class="form-check-input"
                  type="checkbox"
                  id="roleUser"
                  value="user"
                />
                <label class="form-check-label small" for="roleUser">Пользователи</label>
              </div>
              <div class="form-check form-check-inline m-0">
                <input
                  v-model="params.roles"
                  class="form-check-input"
                  type="checkbox"
                  id="roleManager"
                  value="content_manager"
                />
                <label class="form-check-label small" for="roleManager">Контент-менеджеры</label>
              </div>
              <div class="form-check form-check-inline m-0">
                <input
                  v-model="params.roles"
                  class="form-check-input"
                  type="checkbox"
                  id="roleAdmin"
                  value="admin"
                />
                <label class="form-check-label small" for="roleAdmin">Админы</label>
              </div>
              <div v-if="currentUserRole === 'superadmin'" class="form-check form-check-inline m-0">
                <input
                  v-model="params.roles"
                  class="form-check-input"
                  type="checkbox"
                  id="roleSuperAdmin"
                  value="superadmin"
                />
                <label class="form-check-label small" for="roleSuperAdmin">Суперадмины</label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :items="items"
          :has-actions="true"
          :current-page="params.page"
          :page-size="params.limit"
          :sort-config="{ key: params.sort, order: params.order }"
          @sort="handleSort"
          @edit="(u) => openModal(u)"
          @delete="deleteUser"
        >
          <template #actions="{ item }">
            <span v-if="item.user_role === 'superadmin'" class="text-muted small">Система</span>
            <span v-else-if="item.user_role === 'admin' && currentUserRole !== 'superadmin'" class="text-muted small">Нет действий</span>
            <div v-else class="d-flex gap-2 justify-content-end">
              <button class="btn btn-sm btn-outline-primary" @click="openModal(item)">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteUser(item)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </template>
          <template #cell-user_role="{ item }">
            <span
              class="badge"
              :class="
                item.user_role === 'superadmin'
                  ? 'bg-dark'
                  : item.user_role === 'admin'
                    ? 'bg-danger'
                    : item.user_role === 'content_manager'
                      ? 'bg-info'
                      : 'bg-secondary'
              "
            >
              {{ Utils.getRoleLabel(item.user_role) }}
            </span>
          </template>
          <template #cell-user_birth_date="{ item }">
            {{ Utils.calculateAge(item.user_birth_date) }}
          </template>
          <template #cell-user_registration_date="{ item }">
            {{ Utils.formatDate(item.user_registration_date) }}
          </template>
        </DataTable>
      </div>

      <div class="card-footer bg-white border-top-0">
        <Pagination
          :current-page="params.page"
          :pages="pages"
          :total="total"
          @update:page="
            (p) => {
              params.page = p
              load()
            }
          "
        />
      </div>
    </div>

    <Modal
      :show="showModal"
      :title="isEditing ? 'Редактирование' : 'Новый пользователь'"
      @close="closeModal"
    >
      <form id="userForm" @submit.prevent="saveUser">
        <div class="mb-3">
          <label class="form-label small fw-bold text-muted">ФИО</label>
          <input
            v-model="userForm.user_name"
            class="form-control"
            required
            placeholder="Введите ФИО"
          />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-muted">Email</label>
          <input
            v-model="userForm.user_email"
            type="email"
            class="form-control"
            required
            placeholder="example@mail.com"
          />
        </div>
        <div v-if="!isEditing" class="mb-3">
          <label class="form-label small fw-bold text-muted">Пароль</label>
          <input
            v-model="userForm.user_password"
            type="password"
            class="form-control"
            required
            placeholder="Введите пароль"
          />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-muted">Роль системы</label>
          <select v-model="userForm.user_role" class="form-select" required>
            <option value="user">Пользователь</option>
            <option value="content_manager">Контент-менеджер</option>
            <option v-if="currentUserRole === 'superadmin'" value="admin">Администратор</option>
            <option v-if="currentUserRole === 'superadmin' && userForm.user_role === 'superadmin'" value="superadmin">Суперадминистратор</option>
          </select>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold text-muted">Дата рождения</label>
            <input v-model="userForm.user_birth_date" type="date" class="form-control" required />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold text-muted">Регистрация</label>
            <input v-model="userForm.user_registration_date" type="date" class="form-control" />
          </div>
        </div>
      </form>
      <template #footer>
        <button
          type="button"
          class="btn btn-link text-decoration-none text-muted"
          @click="closeModal"
        >
          Отмена
        </button>
        <button type="submit" form="userForm" class="btn btn-primary px-4">Сохранить</button>
      </template>
    </Modal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IUser, IUserCreate } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'user_id', label: 'ID', sortable: true },
  { key: 'user_name', label: 'ФИО', sortable: true },
  { key: 'user_email', label: 'Email', sortable: true },
  { key: 'user_birth_date', label: 'Возраст', sortable: true },
  { key: 'user_registration_date', label: 'Регистрация', sortable: true }
]

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getUsers(p), 
  { sort: 'user_id', order: 'asc' }
)

const showModal = ref(false)
const isEditing = ref(false)
const userForm = reactive<IUserCreate & { user_id?: number }>({ 
  user_name: '', 
  user_email: '', 
  user_birth_date: '',
  user_registration_date: ''
})

const openModal = (user: IUser | null = null) => {
  isEditing.value = !!user
  if (user) {
    Object.assign(userForm, user)
  } else {
    Object.assign(userForm, { 
      user_id: undefined,
      user_name: '', 
      user_email: '', 
      user_birth_date: '',
      user_registration_date: new Date().toISOString().split('T')[0]
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
      await ApiService.updateUser(userForm.user_id, userForm)
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
  if (confirm('Удалить пользователя?')) {
    try {
      await ApiService.deleteUser(user.user_id)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

onMounted(load)
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
        <div class="row">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-search"></i></span>
              <input v-model="params.search" @input="load" type="text" class="form-control bg-light border-start-0" placeholder="Поиск...">
            </div>
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <DataTable 
          :columns="columns" 
          :items="items" 
          :has-actions="true"
          :sort-config="{ key: params.sort, order: params.order }"
          @sort="handleSort"
          @edit="(u) => openModal(u)"
          @delete="deleteUser"
        >
          <template #cell-user_birth_date="{ item }">
            {{ Utils.calculateAge(item.user_birth_date) }}
          </template>
          <template #cell-user_registration_date="{ item }">
            {{ Utils.formatDate(item.user_registration_date) }}
          </template>
        </DataTable>
      </div>
      <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="(p) => { params.page = p; load(); }" />
    </div>

    <Modal :show="showModal" :title="isEditing ? 'Редактирование' : 'Новый пользователь'" @close="closeModal">
      <form id="userForm" @submit.prevent="saveUser">
        <div class="mb-3">
          <label class="form-label small fw-bold text-muted">ФИО</label>
          <input v-model="userForm.user_name" class="form-control" required placeholder="Введите ФИО">
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold text-muted">Email</label>
          <input v-model="userForm.user_email" type="email" class="form-control" required placeholder="example@mail.com">
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold text-muted">Дата рождения</label>
            <input v-model="userForm.user_birth_date" type="date" class="form-control" required>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold text-muted">Регистрация</label>
            <input v-model="userForm.user_registration_date" type="date" class="form-control">
          </div>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn btn-link text-decoration-none text-muted" @click="closeModal">Отмена</button>
        <button type="submit" form="userForm" class="btn btn-primary px-4">Сохранить</button>
      </template>
    </Modal>
  </div>
</template>
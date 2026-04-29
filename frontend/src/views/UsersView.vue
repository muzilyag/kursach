<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IUser, IUserCreate } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'

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
      user_registration_date: new Date().toISOString().split('T')[0] as string
    })
  }
}

const saveUser = async () => {
  try {
    if (isEditing.value && userForm.user_id) {
      await ApiService.updateUser(userForm.user_id, userForm)
    } else {
      await ApiService.createUser(userForm)
    }
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

const onPageChange = (p: number) => {
  params.page = p
  load()
}

onMounted(load)
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Пользователи</h2>
      <button class="btn btn-primary shadow-sm" @click="openModal()" data-bs-toggle="modal" data-bs-target="#userModal">
        <i class="bi bi-person-plus me-2"></i>Добавить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3 border-bottom">
        <input v-model="params.search" @input="load" type="text" class="form-control w-25" placeholder="Поиск по Email или имени...">
      </div>
      <div class="card-body p-0">
        <DataTable 
          :columns="columns" 
          :items="items" 
          :has-actions="true"
          :sort-config="{ key: params.sort, order: params.order }"
          @sort="handleSort"
          @edit="(u) => { openModal(u); }"
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
      <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="onPageChange" />
    </div>

    <div class="modal fade" id="userModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">{{ isEditing ? 'Редактировать' : 'Новый пользователь' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form id="userForm" @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label text-secondary small fw-bold">ФИО</label>
                <input v-model="userForm.user_name" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label text-secondary small fw-bold">Email</label>
                <input v-model="userForm.user_email" type="email" class="form-control" required>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label text-secondary small fw-bold">Дата рождения</label>
                  <input v-model="userForm.user_birth_date" type="date" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-secondary small fw-bold">Регистрация</label>
                  <input v-model="userForm.user_registration_date" type="date" class="form-control">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
            <button type="submit" form="userForm" class="btn btn-primary px-4" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
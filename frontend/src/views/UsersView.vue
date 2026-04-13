<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'

const columns = [
  { key: 'user_id', label: 'ID', sortable: true },
  { key: 'user_name', label: 'ФИО', sortable: true },
  { key: 'user_email', label: 'Email', sortable: true },
  { key: 'user_birth_date', label: 'Возраст', sortable: true },
  { key: 'user_registration_date', label: 'Регистрация', sortable: true }
]

const { items, total, loading, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getUsers(p), 
  { sort: 'user_id', order: 'asc' }
)

const modalInstance = ref<any>(null)
const isEditing = ref(false)
const userForm = reactive({ user_id: '', user_name: '', user_email: '', user_birth_date: '', user_registration_date: '' })

const openModal = (user: any = null) => {
  isEditing.value = !!user
  if (user) {
    Object.assign(userForm, user)
  } else {
    Object.assign(userForm, {
      user_id: '', user_name: '', user_email: '', user_birth_date: '',
      user_registration_date: new Date().toISOString().split('T')[0]
    })
  }
  const el = document.getElementById('userModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const saveUser = async () => {
  try {
    if (isEditing.value) await ApiService.updateUser(userForm.user_id, userForm)
    else await ApiService.createUser(userForm)
    modalInstance.value?.hide()
    load()
  } catch (e: any) { alert(e.message) }
}

const deleteUser = async (user: any) => {
  if (!confirm('Удалить пользователя?')) return
  try {
    await ApiService.deleteUser(user.user_id)
    load()
  } catch (e: any) { alert(e.message) }
}
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-people me-2"></i>Пользователи</h2>
      <button class="btn btn-primary" @click="openModal()">Добавить</button>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <input v-model="params.search" class="form-control" placeholder="Поиск на сервере...">
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    
    <div v-else class="card shadow-sm">
      <DataTable 
        :columns="columns" :items="items" :has-actions="true"
        :sort-config="{ key: params.sort, order: params.order }"
        @sort="handleSort" @edit="openModal" @delete="deleteUser"
      >
        <template #cell-user_birth_date="{ item }">
          {{ Utils.calculateAge(item.user_birth_date) }} лет
        </template>
        <template #cell-user_registration_date="{ item }">
          {{ Utils.formatDate(item.user_registration_date) }}
        </template>
      </DataTable>

      <div class="card-footer bg-white py-3" v-if="total > params.limit">
        <nav>
          <ul class="pagination justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: params.page === 1 }">
              <button class="page-link" @click="params.page--"><i class="bi bi-chevron-left"></i></button>
            </li>
            <li v-for="p in pages" :key="p" class="page-item" :class="{ active: params.page === p }">
              <button class="page-link" @click="params.page = p">{{ p }}</button>
            </li>
            <li class="page-item" :class="{ disabled: params.page === pages.length }">
              <button class="page-link" @click="params.page++"><i class="bi bi-chevron-right"></i></button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <div class="modal fade" id="userModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Редактировать' : 'Новый' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form id="userForm" @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label">ФИО *</label>
                <input v-model="userForm.user_name" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input v-model="userForm.user_email" type="email" class="form-control" required>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Дата рождения *</label>
                  <input v-model="userForm.user_birth_date" type="date" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Регистрация</label>
                  <input v-model="userForm.user_registration_date" type="date" class="form-control">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="submit" form="userForm" class="btn btn-primary">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
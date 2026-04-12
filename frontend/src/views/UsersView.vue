<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'

interface User {
  user_id?: string | number
  user_name: string
  user_email: string
  user_birth_date: string
  user_registration_date?: string
}

const users = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const totalUsers = ref(0)

const tableParams = reactive({
  page: 1,
  limit: 10,
  search: '',
  sort: 'user_id',
  order: 'asc'
})

const modalInstance = ref<any>(null)
const isEditing = ref(false)
const userForm = reactive<User>({
  user_id: '',
  user_name: '',
  user_email: '',
  user_birth_date: '',
  user_registration_date: ''
})

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await ApiService.getUsers({
      page: tableParams.page,
      limit: tableParams.limit,
      search: tableParams.search,
      sort: tableParams.sort,
      order: tableParams.order
    })
    users.value = response.users || []
    totalUsers.value = response.total || 0
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки пользователей'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  tableParams.page = 1
  fetchUsers()
}

const toggleSortDirection = () => {
  tableParams.order = tableParams.order === 'asc' ? 'desc' : 'asc'
  fetchUsers()
}

const changeSortField = () => {
  tableParams.page = 1
  fetchUsers()
}

const changePage = (newPage: number) => {
  const totalPages = Math.ceil(totalUsers.value / tableParams.limit)
  if (newPage >= 1 && newPage <= totalPages) {
    tableParams.page = newPage
    fetchUsers()
  }
}

const openAddModal = () => {
  isEditing.value = false
  userForm.user_id = ''
  userForm.user_name = ''
  userForm.user_email = ''
  userForm.user_birth_date = ''
  userForm.user_registration_date = new Date().toISOString().split('T')[0]
  
  const el = document.getElementById('userVueModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const openEditModal = (user: any) => {
  isEditing.value = true
  userForm.user_id = user.user_id
  userForm.user_name = user.user_name
  userForm.user_email = user.user_email
  userForm.user_birth_date = user.user_birth_date ? user.user_birth_date.split('T')[0] : ''
  userForm.user_registration_date = user.user_registration_date ? user.user_registration_date.split('T')[0] : ''
  
  const el = document.getElementById('userVueModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const saveUser = async () => {
  if (!userForm.user_name || !userForm.user_email || !userForm.user_birth_date) {
    alert('Заполните все обязательные поля!')
    return
  }

  try {
    const payload: any = { ...userForm }
    if (!payload.user_registration_date) {
      delete payload.user_registration_date
    }

    if (isEditing.value && userForm.user_id) {
      await ApiService.updateUser(Number(userForm.user_id), payload)
    } else {
      await ApiService.createUser(payload)
    }
    
    if (modalInstance.value) modalInstance.value.hide()
    fetchUsers()
  } catch (e: any) {
    alert(e.message || 'Ошибка сохранения')
  }
}

const deleteUser = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
  try {
    await ApiService.deleteUser(id)
    fetchUsers()
  } catch (e: any) {
    alert(e.message || 'Ошибка удаления')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-people me-2"></i>Управление пользователями</h2>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-person-plus me-2"></i>Добавить пользователя
      </button>
    </div>

    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input 
            type="text" 
            class="form-control" 
            v-model="tableParams.search" 
            @keyup.enter="handleSearch"
            placeholder="Поиск по имени или email..."
          >
          <button class="btn btn-outline-primary" @click="handleSearch">Найти</button>
        </div>
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="tableParams.sort" @change="changeSortField">
          <option value="user_id">Сортировка по ID</option>
          <option value="user_name">По имени</option>
          <option value="user_email">По email</option>
          <option value="user_birth_date">По дате рождения</option>
          <option value="user_registration_date">По дате регистрации</option>
        </select>
      </div>
      <div class="col-md-3">
        <button class="btn btn-outline-secondary w-100" @click="toggleSortDirection">
          <i class="bi" :class="tableParams.order === 'asc' ? 'bi-sort-down' : 'bi-sort-up'"></i> 
          {{ tableParams.order === 'asc' ? 'По возрастанию' : 'По убыванию' }}
        </button>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>#</th>
              <th>ФИО</th>
              <th>Email</th>
              <th>Дата рождения</th>
              <th>Дата регистрации</th>
              <th>Возраст</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4">
                <div class="spinner-border text-primary" role="status"></div>
              </td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">Пользователи не найдены</td>
            </tr>
            <tr v-for="(user, index) in users" :key="user.user_id" v-else>
              <td>{{ (tableParams.page - 1) * tableParams.limit + index + 1 }}</td>
              <td>{{ user.user_name }}</td>
              <td>{{ user.user_email }}</td>
              <td>{{ Utils.formatDate(user.user_birth_date) }}</td>
              <td>{{ Utils.formatDate(user.user_registration_date) }}</td>
              <td>{{ Utils.calculateAge(user.user_birth_date) }} лет</td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-2" @click="openEditModal(user)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteUser(user.user_id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="card-footer bg-white border-top-0 pt-3 pb-3" v-if="totalUsers > tableParams.limit">
        <nav aria-label="Навигация по страницам">
          <ul class="pagination justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: tableParams.page === 1 }">
              <a class="page-link" href="#" @click.prevent="changePage(tableParams.page - 1)">Назад</a>
            </li>
            <li class="page-item" v-for="p in Math.ceil(totalUsers / tableParams.limit)" :key="p" :class="{ active: tableParams.page === p }">
              <a class="page-link" href="#" @click.prevent="changePage(p)">{{ p }}</a>
            </li>
            <li class="page-item" :class="{ disabled: tableParams.page === Math.ceil(totalUsers / tableParams.limit) }">
              <a class="page-link" href="#" @click.prevent="changePage(tableParams.page + 1)">Вперёд</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <div class="modal fade" id="userVueModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Редактирование пользователя' : 'Добавление пользователя' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label">ФИО *</label>
                <input type="text" class="form-control" v-model="userForm.user_name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input type="email" class="form-control" v-model="userForm.user_email" required>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Дата рождения *</label>
                  <input type="date" class="form-control" v-model="userForm.user_birth_date" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Дата регистрации</label>
                  <input type="date" class="form-control" v-model="userForm.user_registration_date">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-primary" @click="saveUser">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'

const contentList = ref<any[]>([])
const genres = ref<any[]>([])
const holders = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const totalContent = ref(0)
const currentPage = ref(1)

const modalInstance = ref<any>(null)
const isEditing = ref(false)
const currentId = ref<number | null>(null)

const contentForm = reactive({
  content_name: '',
  content_type: 'Фильм',
  content_duration: '01:30:00',
  content_publish_date: new Date().toISOString().split('T')[0],
  content_discription: '',
  genre_id: '',
  copyright_holder_id: ''
})

const fetchContent = async (page = 1) => {
  loading.value = true
  try {
    const response = await ApiService.getContent(page)
    contentList.value = response.content || []
    totalContent.value = response.total || 0
    currentPage.value = page
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки контента'
  } finally {
    loading.value = false
  }
}

const fetchDictionaries = async () => {
  try {
    genres.value = await ApiService.getGenres()
    holders.value = await ApiService.getCopyrightHolders()
  } catch (e) {
    console.error('Ошибка загрузки справочников', e)
  }
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  contentForm.content_name = ''
  contentForm.content_type = 'Фильм'
  contentForm.content_duration = '01:30:00'
  contentForm.content_publish_date = new Date().toISOString().split('T')[0]
  contentForm.content_discription = ''
  contentForm.genre_id = genres.value.length > 0 ? genres.value[0].value : ''
  contentForm.copyright_holder_id = holders.value.length > 0 ? holders.value[0].value : ''
  
  const el = document.getElementById('contentVueModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const openEditModal = (item: any) => {
  isEditing.value = true
  currentId.value = item.content_id
  contentForm.content_name = item['Название']
  contentForm.content_type = item['Тип']
  contentForm.content_duration = item['Длительность']
  contentForm.content_publish_date = item['Дата выпуска'] !== 'Не указана' ? item['Дата выпуска'] : ''
  contentForm.content_discription = item['Описание'] || ''

  const firstGenre = item['Жанры'] ? item['Жанры'].split(', ')[0] : ''
  const genreMatch = genres.value.find(g => g.label === firstGenre)
  contentForm.genre_id = genreMatch ? genreMatch.value : (genres.value.length > 0 ? genres.value[0].value : '')

  const firstHolder = item['Правообладатели'] ? item['Правообладатели'].split(', ')[0] : ''
  const holderMatch = holders.value.find(h => h.label === firstHolder)
  contentForm.copyright_holder_id = holderMatch ? holderMatch.value : (holders.value.length > 0 ? holders.value[0].value : '')

  const el = document.getElementById('contentVueModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const saveContent = async () => {
  if (!contentForm.content_name) {
    alert('Заполните обязательные поля!')
    return
  }
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.updateContent(currentId.value, { ...contentForm })
    } else {
      await ApiService.createContent({ ...contentForm })
    }
    if (modalInstance.value) modalInstance.value.hide()
    fetchContent(currentPage.value)
  } catch (e: any) {
    alert(e.message || 'Ошибка сохранения')
  }
}

const deleteContent = async (id: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот контент?')) return
  try {
    await ApiService.deleteContent(id)
    fetchContent(currentPage.value)
  } catch (e: any) {
    alert(e.message || 'Ошибка удаления')
  }
}

const changePage = (newPage: number) => {
  const limit = 10
  const totalPages = Math.ceil(totalContent.value / limit)
  if (newPage >= 1 && newPage <= totalPages) {
    fetchContent(newPage)
  }
}

onMounted(() => {
  fetchContent()
  fetchDictionaries()
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-film me-2"></i>Каталог контента</h2>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Добавить контент
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Название</th>
              <th>Тип</th>
              <th>Длительность</th>
              <th>Жанры</th>
              <th>Правообладатели</th>
              <th>Дата выпуска</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in contentList" :key="item.content_id">
              <td class="fw-medium">{{ item['Название'] }}</td>
              <td><span class="badge bg-info">{{ item['Тип'] }}</span></td>
              <td>{{ Utils.formatDuration(item['Длительность']) }}</td>
              <td>{{ item['Жанры'] }}</td>
              <td>{{ item['Правообладатели'] }}</td>
              <td>{{ Utils.formatDate(item['Дата выпуска']) }}</td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-2" @click="openEditModal(item)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteContent(item.content_id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="contentList.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">Контент не найден</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="card-footer bg-white border-top-0 pt-3 pb-3" v-if="totalContent > 10">
        <nav aria-label="Навигация">
          <ul class="pagination justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Назад</a>
            </li>
            <li class="page-item" v-for="p in Math.ceil(totalContent / 10)" :key="p" :class="{ active: currentPage === p }">
              <a class="page-link" href="#" @click.prevent="changePage(p)">{{ p }}</a>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === Math.ceil(totalContent / 10) }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Вперёд</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <div class="modal fade" id="contentVueModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Редактирование контента' : 'Новый контент' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveContent">
              <div class="mb-3">
                <label class="form-label">Название *</label>
                <input type="text" class="form-control" v-model="contentForm.content_name" required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Описание</label>
                <textarea class="form-control" rows="3" v-model="contentForm.content_discription"></textarea>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Тип *</label>
                  <select class="form-select" v-model="contentForm.content_type" required>
                    <option value="Фильм">Фильм</option>
                    <option value="Сериал">Сериал</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Жанр</label>
                  <select class="form-select" v-model="contentForm.genre_id">
                    <option value="">Не выбран</option>
                    <option v-for="g in genres" :key="g.value" :value="g.value">{{ g.label }}</option>
                  </select>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Правообладатель</label>
                  <select class="form-select" v-model="contentForm.copyright_holder_id">
                    <option value="">Не выбран</option>
                    <option v-for="h in holders" :key="h.value" :value="h.value">{{ h.label }}</option>
                  </select>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Длительность *</label>
                  <input type="time" step="1" class="form-control" v-model="contentForm.content_duration" required>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Дата выпуска</label>
                  <input type="date" class="form-control" v-model="contentForm.content_publish_date">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-primary" @click="saveContent">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
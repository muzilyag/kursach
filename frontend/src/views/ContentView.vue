<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'

const columns = [
  { key: 'content_name', label: 'Название', sortable: true },
  { key: 'genres', label: 'Жанры' },
  { key: 'tags', label: 'Теги' },
  { key: 'content_duration', label: 'Длительность', sortable: true },
  { key: 'content_publish_date', label: 'Выпуск', sortable: true }
]

const genres = ref<any[]>([])
const tags = ref<any[]>([])
const holders = ref<any[]>([])

const { items, total, loading, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getContent(p), 
  { sort: 'content_id', order: 'desc' }
)

const modalInstance = ref<any>(null)
const isEditing = ref(false)
const currentId = ref<number | null>(null)
const contentForm = reactive({
  content_name: '',
  content_type: 'Фильм',
  content_duration: '01:30:00',
  content_publish_date: '',
  content_discription: '',
  genre_id: '',
  tag_id: '',
  copyright_holder_id: ''
})

const initOptions = async () => {
  try {
    const [g, t, h] = await Promise.all([
      ApiService.getGenres(),
      ApiService.getTags(),
      ApiService.getCopyrightHolders()
    ])
    genres.value = g
    tags.value = t
    holders.value = h
  } catch (e: any) { console.error(e) }
}

const openModal = (item: any = null) => {
  isEditing.value = !!item
  if (item) {
    currentId.value = item.content_id
    contentForm.content_name = item['Название'] as string
    contentForm.content_duration = item['Длительность'] as string
    contentForm.content_publish_date = (item['Дата выпуска'] && item['Дата выпуска'] !== 'None') ? item['Дата выпуска'] as string : ''
    contentForm.content_discription = item['Описание'] as string
    contentForm.genre_id = item.genre_id as string
    contentForm.tag_id = item.tag_id as string
    contentForm.copyright_holder_id = item.copyright_holder_id as string
  } else {
    currentId.value = null
    Object.assign(contentForm, {
      content_name: '', content_duration: '01:30:00',
      content_publish_date: new Date().toISOString().split('T')[0],
      content_discription: '', genre_id: '', tag_id: '', copyright_holder_id: ''
    })
  }
  const el = document.getElementById('contentModal')
  if (el && (window as any).bootstrap) {
    modalInstance.value = new (window as any).bootstrap.Modal(el)
    modalInstance.value.show()
  }
}

const formatDuration = (val: string) => {
  if (!val) {
    return '0ч 0м'
  }
  const parts = val.split(':')
  if (parts.length < 2) { 
    return val
  }
  const h = parseInt(parts[0] ?? '0', 10) || 0
  const m = parseInt(parts[1] ?? '0', 10) || 0
  return `${h}ч ${m}м`
}

const save = async () => {
  try {
    const payload = {
      ...contentForm,
      genre_id: contentForm.genre_id ? Number(contentForm.genre_id) : null,
      tag_id: contentForm.tag_id ? Number(contentForm.tag_id) : null,
      copyright_holder_id: contentForm.copyright_holder_id ? Number(contentForm.copyright_holder_id) : null,
      content_discription: contentForm.content_discription || null
    }

    if (isEditing.value && currentId.value) {
      await ApiService.updateContent(currentId.value, payload)
    } else {
      await ApiService.createContent(payload)
    }

    modalInstance.value?.hide()
    load()
  } catch (e: any) { 
    alert(e.message) 
  }
}

const remove = async (item: any) => {
  if (!confirm('Удалить контент?')) {
    return
  }
  try {
    await ApiService.deleteContent(item.content_id)
    load()
  } catch (e: any) { 
    alert(e.message) 
  }
}

onMounted(initOptions)
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="bi bi-film me-2"></i>Контент</h2>
      <button class="btn btn-primary" @click="openModal(null)">Добавить</button>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="input-group">
          <input v-model="params.search" @keyup.enter="load" class="form-control" placeholder="Поиск по названию или описанию...">
          <button class="btn btn-primary px-4" @click="load">
            <i class="bi bi-search me-1"></i> Найти
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    
    <div v-else class="card shadow-sm">
      <DataTable 
        :columns="columns" :items="items" :has-actions="true"
        :sort-config="{ key: params.sort, order: params.order }"
        @sort="handleSort" @edit="openModal" @delete="remove"
      >
        <template #cell-content_name="{ item }">{{ item['Название'] }}</template>
        <template #cell-genres="{ item }">{{ item['Жанры'] }}</template>
        
        <template #cell-tags="{ item }">
          <div class="d-flex flex-wrap gap-1">
            <template v-if="item['Теги']">
              <span v-for="(tag, index) in String(item['Теги']).split(', ')" :key="index" class="badge rounded-pill bg-primary text-white shadow-sm px-2 py-1">
                <i class="bi bi-tag-fill me-1"></i>{{ tag }}
              </span>
            </template>
            <span v-else class="text-muted small">—</span>
          </div>
        </template>
        
        <template #cell-content_duration="{ item }">
          {{ formatDuration(item['Длительность'] ? String(item['Длительность']) : '00:00:00') }}
        </template>
        <template #cell-content_publish_date="{ item }">
          {{ Utils.formatDate(item['Дата выпуска'] ? String(item['Дата выпуска']) : '') }}
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

    <div class="modal fade" id="contentModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Редактирование' : 'Новый контент' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form id="contentForm" @submit.prevent="save">
              <div class="mb-3">
                <label class="form-label">Название</label>
                <input v-model="contentForm.content_name" class="form-control" required>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Жанр</label>
                  <select v-model="contentForm.genre_id" class="form-select">
                    <option value="">Не выбран</option>
                    <option v-for="g in genres" :key="g.value" :value="g.value">{{ g.label }}</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Тег</label>
                  <select v-model="contentForm.tag_id" class="form-select">
                    <option value="">Не выбран</option>
                    <option v-for="t in tags" :key="t.value" :value="t.value">{{ t.label }}</option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Длительность</label>
                  <input v-model="contentForm.content_duration" type="time" step="1" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Дата выпуска</label>
                  <input v-model="contentForm.content_publish_date" type="date" class="form-control">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Тип контента</label>
                  <select v-model="contentForm.content_type" class="form-select" required>
                    <option value="Фильм">Фильм</option>
                    <option value="Шоу">Шоу</option>
                    <option value="Сериал">Сериал</option>
                    <option value="Мультфильм">Мультфильм</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Правообладатель</label>
                  <select v-model="contentForm.copyright_holder_id" class="form-select">
                    <option value="">Не выбран</option>
                    <option v-for="h in holders" :key="h.value" :value="h.value">{{ h.label }}</option>
                  </select>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Описание</label>
                <textarea v-model="contentForm.content_discription" class="form-control" rows="3"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="submit" form="contentForm" class="btn btn-primary">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
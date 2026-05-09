<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IContent, IContentCreate, IGenre, ITag, ICopyrightHolder } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'content_name', label: 'Название', sortable: true },
  { key: 'genres', label: 'Жанры' },
  { key: 'tags', label: 'Теги' },
  { key: 'content_duration', label: 'Длительность', sortable: true },
  { key: 'content_publish_date', label: 'Выпуск', sortable: true }
]

const genresList = ref<IGenre[]>([])
const tagsList = ref<ITag[]>([])
const holdersList = ref<ICopyrightHolder[]>([])
const showModal = ref(false)
const isEditing = ref(false)
const currentId = ref<number | null>(null)

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getContent(p), 
  { sort: 'content_id', order: 'desc', limit: 10 }
)

const contentForm = reactive<IContentCreate>({
  content_name: '',
  content_type: 'Фильм',
  content_duration: '01:30:00',
  content_publish_date: new Date().toISOString().split('T')[0] ?? '',
  content_discription: '',
  genre_id: undefined,
  tag_id: undefined,
  copyright_holder_id: undefined
})

const openModal = (item: IContent | null = null) => {
  isEditing.value = !!item
  if (item) {
    currentId.value = item.content_id
    Object.assign(contentForm, {
      content_name: item.content_name,
      content_type: item.content_type,
      content_duration: item.content_duration,
      content_publish_date: item.content_publish_date,
      content_discription: item.content_discription || '',
      genre_id: item.genres?.[0]?.genre_id,
      tag_id: item.tags?.[0]?.tag_id,
      copyright_holder_id: item.copyright_holders?.[0]?.copyright_holder_id
    })
  } else {
    currentId.value = null
    Object.assign(contentForm, {
      content_name: '',
      content_type: 'Фильм',
      content_duration: '01:30:00',
      content_publish_date: new Date().toISOString().split('T')[0],
      content_discription: '',
      genre_id: undefined,
      tag_id: undefined,
      copyright_holder_id: undefined
    })
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveContent = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.updateContent(currentId.value, contentForm as any)
    } else {
      await ApiService.createContent(contentForm)
    }
    closeModal()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteItem = async (item: IContent) => {
  if (confirm('Удалить контент?')) {
    try {
      await ApiService.deleteContent(item.content_id)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

onMounted(async () => {
  load()
  try {
    const [g, t, h] = await Promise.all([
      ApiService.getGenres(),
      ApiService.getTags(),
      ApiService.getCopyrightHolders()
    ])
    genresList.value = g
    tagsList.value = t
    holdersList.value = h
  } catch (e) {}
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Контент</h2>
      <button class="btn btn-primary" @click="openModal()">
        <i class="bi bi-plus-lg me-2"></i>Добавить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3">
        <input v-model="params.search" @input="load" type="text" class="form-control w-25" placeholder="Поиск...">
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
          @edit="openModal"
          @delete="deleteItem"
        >
          <template #cell-genres="{ item }">
            <span v-for="g in item.genres" :key="g.genre_id" class="badge bg-light text-dark border me-1">
              {{ g.genre_name }}
            </span>
          </template>
          <template #cell-tags="{ item }">
            <span v-for="t in item.tags" :key="t.tag_id" class="text-muted small me-1">
              #{{ t.tag_name }}
            </span>
          </template>
          <template #cell-content_duration="{ item }">
            {{ Utils.formatDuration(item.content_duration) }}
          </template>
          <template #cell-content_publish_date="{ item }">
            {{ Utils.formatDate(item.content_publish_date) }}
          </template>
        </DataTable>
      </div>
      <div class="card-footer bg-white border-top-0">
        <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="(p) => { params.page = p; load(); }" />
      </div>
    </div>

    <Modal :show="showModal" :title="isEditing ? 'Редактировать контент' : 'Новый контент'" @close="closeModal">
      <form @submit.prevent="saveContent" id="contentForm" class="row g-3">
        <div class="col-12">
          <label class="form-label small fw-bold">Название</label>
          <input v-model="contentForm.content_name" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Тип</label>
          <select v-model="contentForm.content_type" class="form-select">
            <option value="Фильм">Фильм</option>
            <option value="Сериал">Сериал</option>
            <option value="Шоу">Шоу</option>
            <option value="Мультфильм">Мультфильм</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Жанр</label>
          <select v-model="contentForm.genre_id" class="form-select">
            <option :value="undefined">Не выбран</option>
            <option v-for="g in genresList" :key="g.genre_id" :value="g.genre_id">{{ g.genre_name }}</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Дата выпуска</label>
          <input v-model="contentForm.content_publish_date" type="date" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Длительность</label>
          <input v-model="contentForm.content_duration" class="form-control" placeholder="00:00:00">
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Тег</label>
          <select v-model="contentForm.tag_id" class="form-select">
            <option :value="undefined">Не выбран</option>
            <option v-for="t in tagsList" :key="t.tag_id" :value="t.tag_id">{{ t.tag_name }}</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Правообладатель</label>
          <select v-model="contentForm.copyright_holder_id" class="form-select">
            <option :value="undefined">Не выбран</option>
            <option v-for="h in holdersList" :key="h.copyright_holder_id" :value="h.copyright_holder_id">{{ h.copyright_holder_name }}</option>
          </select>
        </div>
        <div class="col-12">
          <label class="form-label small fw-bold">Описание</label>
          <textarea v-model="contentForm.content_discription" class="form-control" rows="3"></textarea>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn btn-light" @click="closeModal">Отмена</button>
        <button type="submit" form="contentForm" class="btn btn-primary px-4">Сохранить</button>
      </template>
    </Modal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { IContent, IContentCreate, IGenre } from '../services/api'
import { Config } from '../config'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'

const columns = [
  { key: 'content_name', label: 'Название', sortable: true },
  { key: 'genres', label: 'Жанры' },
  { key: 'content_duration', label: 'Длительность', sortable: true },
  { key: 'content_publish_date', label: 'Выпуск', sortable: true }
]

const genresList = ref<IGenre[]>([])
const isEditing = ref(false)
const currentId = ref<number | null>(null)

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getContent(p), 
  { sort: 'content_id', order: 'desc' }
)

const contentForm = reactive<IContentCreate>({
  content_name: '',
  content_type: 'Фильм',
  content_duration: '01:30:00',
  content_publish_date: new Date().toISOString().split('T')[0] as string,
  content_discription: '',
  genre_id: undefined
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
      genre_id: item.genres.length > 0 ? item.genres[0]?.genre_id : undefined
    })
  } else {
    currentId.value = null
    Object.assign(contentForm, {
      content_name: '',
      content_type: 'Фильм',
      content_duration: '01:30:00',
      content_publish_date: new Date().toISOString().split('T')[0] as string,
      content_discription: '',
      genre_id: undefined
    })
  }
}

const saveContent = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.request(`${Config.api.content}/${currentId.value}`, {
        method: 'PUT',
        body: JSON.stringify(contentForm)
      })
    } else {
      await ApiService.createContent(contentForm)
    }
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

const onPageChange = (p: number) => {
  params.page = p
  load()
}

onMounted(async () => {
  load()
  try {
    genresList.value = await ApiService.getGenres()
  } catch (e) {}
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Контент-менеджмент</h2>
      <button class="btn btn-primary shadow-sm" @click="openModal()" data-bs-toggle="modal" data-bs-target="#contentModal">
        <i class="bi bi-plus-lg me-2"></i>Добавить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3 border-bottom">
        <input v-model="params.search" @input="load" type="text" class="form-control w-25" placeholder="Поиск контента...">
      </div>
      <div class="card-body p-0">
        <DataTable 
          :columns="columns" 
          :items="items" 
          :has-actions="true"
          :sort-config="{ key: params.sort, order: params.order }"
          @sort="handleSort"
          @edit="(i) => { openModal(i); }"
          @delete="deleteItem"
        >
          <template #cell-genres="{ item }">
            <span v-for="g in item.genres" :key="g.genre_id" class="badge bg-info-subtle text-info me-1">
              {{ g.genre_name }}
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
      <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="onPageChange" />
    </div>

    <div class="modal fade" id="contentModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">{{ isEditing ? 'Редактировать' : 'Новый контент' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveContent" id="contentForm">
              <div class="row g-3">
                <div class="col-md-12">
                  <label class="form-label text-secondary small fw-bold">Название</label>
                  <input v-model="contentForm.content_name" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-secondary small fw-bold">Тип</label>
                  <select v-model="contentForm.content_type" class="form-select">
                    <option value="Фильм">Фильм</option>
                    <option value="Сериал">Сериал</option>
                    <option value="Шоу">Шоу</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-secondary small fw-bold">Жанр</label>
                  <select v-model="contentForm.genre_id" class="form-select">
                    <option :value="undefined">Не указан</option>
                    <option v-for="g in genresList" :key="g.genre_id" :value="g.genre_id">
                      {{ g.genre_name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-secondary small fw-bold">Дата выпуска</label>
                  <input v-model="contentForm.content_publish_date" type="date" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-secondary small fw-bold">Длительность (HH:mm:ss)</label>
                  <input v-model="contentForm.content_duration" class="form-control" placeholder="01:30:00" required>
                </div>
                <div class="col-md-12">
                  <label class="form-label text-secondary small fw-bold">Описание</label>
                  <textarea v-model="contentForm.content_discription" class="form-control" rows="3"></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
            <button type="submit" form="contentForm" class="btn btn-primary px-4" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
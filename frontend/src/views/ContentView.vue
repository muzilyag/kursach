<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { IContent, IContentCreate, IGenre, ITag, ICopyrightHolder } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'content_name', label: 'Название', sortable: true },
  { key: 'content_type', label: 'Тип', sortable: true },
  { key: 'genres', label: 'Жанры' },
  { key: 'tags', label: 'Теги' },
  { key: 'copyright_holders', label: 'Правообладатели' },
  { key: 'content_duration', label: 'Длительность', sortable: true },
  { key: 'content_publish_date', label: 'Выпуск', sortable: true }
]

const genresList = ref<IGenre[]>([])
const tagsList = ref<ITag[]>([])
const holdersList = ref<ICopyrightHolder[]>([])
const showModal = ref(false)
const isEditing = ref(false)
const currentId = ref<number | null>(null)

const durationInput = reactive({
  h: 0,
  m: 0,
  s: 0
})

const validateTime = (field: 'h' | 'm' | 's') => {
  if (field === 'h') {
    durationInput.h = Math.max(0, durationInput.h)
  } else {
    if (durationInput[field] > 59) durationInput[field] = 59
    if (durationInput[field] < 0) durationInput[field] = 0
  }
}

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getContent(p), 
  { sort: 'content_id', order: 'desc', limit: Config.pagination.itemsPerPage }
)

const contentForm = reactive({
  content_name: '',
  content_type: 'фильм',
  content_publish_date: new Date().toISOString().split('T')[0],
  content_discription: '',
  genre_ids: [] as number[],
  tag_ids: [] as number[],
  copyright_holder_ids: [] as number[]
})

const genreColorMap: Record<string, string> = {
  'Драма': 'var(--genre-drama)',
  'Комедия': 'var(--genre-comedy)',
  'Боевик': 'var(--genre-action)',
  'Триллер': 'var(--genre-thriller)',
  'Ужасы': 'var(--genre-horror)',
  'Мелодрама': 'var(--genre-romance)',
  'Фэнтези': 'var(--genre-fantasy)',
  'Фантастика': 'var(--genre-sci-fi)',
  'Документальный': 'var(--genre-documentary)',
  'Мультфильм': 'var(--genre-animation)',
  'Приключения': 'var(--genre-adventure)',
  'Детектив': 'var(--genre-mystery)'
}

const getGenreStyle = (name: string) => {
  const color = genreColorMap[name] || '#f8f9fa'
  return { backgroundColor: color, border: 'none', color: '#333' }
}

const openModal = (item: IContent | null = null) => {
  isEditing.value = !!item
  if (item) {
    currentId.value = item.content_id
    const [h, m, s] = (item.content_duration || '00:00:00').split(':').map(Number)
    durationInput.h = h ?? 0
    durationInput.m = m ?? 0
    durationInput.s = s ?? 0
    
    Object.assign(contentForm, {
      content_name: item.content_name,
      content_type: item.content_type,
      content_publish_date: item.content_publish_date ? item.content_publish_date.split('T')[0] : '',
      content_discription: item.content_discription || '',
      genre_ids: item.genres?.map(g => g.genre_id) || [],
      tag_ids: item.tags?.map(t => t.tag_id) || [],
      copyright_holder_ids: item.copyright_holders?.map(h => h.copyright_holder_id) || []
    })
  } else {
    currentId.value = null
    durationInput.h = 1
    durationInput.m = 30
    durationInput.s = 0
    Object.assign(contentForm, {
      content_name: '',
      content_type: 'фильм',
      content_publish_date: new Date().toISOString().split('T')[0],
      content_discription: '',
      genre_ids: [],
      tag_ids: [],
      copyright_holder_ids: []
    })
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveContent = async () => {
  try {
    const pad = (n: number) => String(n).padStart(2, '0')
    const durationString = `${pad(durationInput.h)}:${pad(durationInput.m)}:${pad(durationInput.s)}`

    const payload: IContentCreate = {
      content_name: contentForm.content_name,
      content_type: contentForm.content_type,
      content_duration: durationString,
      content_publish_date: contentForm.content_publish_date ?? '',
      content_discription: contentForm.content_discription,
      tag_ids: contentForm.tag_ids,
      genre_ids: contentForm.genre_ids,
      copyright_holder_ids: contentForm.copyright_holder_ids
    }

    if (isEditing.value && currentId.value) {
      await ApiService.updateContent(currentId.value, payload as any)
    } else {
      await ApiService.createContent(payload)
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
          <template #cell-content_name="{ item }">
            <div class="cursor-help" :title="item.content_name">
              {{ item.content_name.length > 17 ? item.content_name.slice(0, 17) + '...' : item.content_name }}
            </div>
          </template>

          <template #cell-content_type="{ item }">
            <span class="badge rounded-pill bg-secondary text-white opacity-75 small" :title="item.content_type">
              {{ item.content_type.length > 6 ? item.content_type.slice(0, 5) + '...' : item.content_type }}
            </span>
          </template>

          <template #cell-genres="{ item }">
            <div class="d-flex align-items-center" v-if="item.genres?.length">
              <span class="badge" :style="getGenreStyle(item.genres[0].genre_name)">
                {{ item.genres[0].genre_name }}
              </span>
              <div v-if="item.genres.length > 1" class="dropdown d-inline ms-1">
                <button class="btn btn-link btn-sm p-0 text-decoration-none small fw-bold text-dark" type="button" data-bs-toggle="dropdown">
                  +{{ item.genres.length - 1 }}
                </button>
                <ul class="dropdown-menu shadow-sm border-0 p-2">
                  <li v-for="g in item.genres.slice(1)" :key="g.genre_id" class="py-1">
                    <span class="badge w-100" :style="getGenreStyle(g.genre_name)">{{ g.genre_name }}</span>
                  </li>
                </ul>
              </div>
            </div>
            <span v-else class="text-muted small">---</span>
          </template>
          
          <template #cell-tags="{ item }">
            <div class="d-flex align-items-center" v-if="item.tags?.length">
              <span class="text-muted small me-1">#{{ item.tags[0].tag_name }}</span>
              <div v-if="item.tags.length > 1" class="dropdown d-inline">
                <button class="btn btn-link btn-sm p-0 text-decoration-none small fw-bold text-dark" type="button" data-bs-toggle="dropdown">
                  +{{ item.tags.length - 1 }}
                </button>
                <ul class="dropdown-menu shadow-sm border-0 p-2">
                  <li v-for="t in item.tags.slice(1)" :key="t.tag_id" class="small text-muted py-1 px-2">
                    #{{ t.tag_name }}
                  </li>
                </ul>
              </div>
            </div>
            <span v-else class="text-muted small">---</span>
          </template>

          <template #cell-copyright_holders="{ item }">
            <div class="d-flex align-items-center" v-if="item.copyright_holders?.length">
              <span class="small text-truncate cursor-help" 
                    style="max-width: 130px;" 
                    :title="item.copyright_holders.map((h: ICopyrightHolder) => h.copyright_holder_name).join(', ')">
                {{ item.copyright_holders[0].copyright_holder_name }}
              </span>
              <div v-if="item.copyright_holders.length > 1" class="dropdown d-inline ms-1">
                <button class="btn btn-link btn-sm p-0 text-decoration-none small fw-bold text-dark" type="button" data-bs-toggle="dropdown">
                  +{{ item.copyright_holders.length - 1 }}
                </button>
                <ul class="dropdown-menu shadow-sm border-0 p-2" style="min-width: 200px;">
                  <li v-for="h in item.copyright_holders.slice(1)" :key="h.copyright_holder_id" class="small py-1 px-2 border-bottom last-child-0">
                    {{ h.copyright_holder_name }}
                  </li>
                </ul>
              </div>
            </div>
            <span v-else class="text-muted small">---</span>
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
            <option value="фильм">фильм</option>
            <option value="сериал">сериал</option>
            <option value="шоу">шоу</option>
            <option value="мультфильм">мультфильм</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Жанры</label>
          <div class="border rounded p-2 bg-white form-control checkbox-list-container">
            <div class="form-check mb-1" v-for="g in genresList" :key="g.genre_id">
              <input class="form-check-input" type="checkbox" :value="g.genre_id" :id="'genre-'+g.genre_id" v-model="contentForm.genre_ids">
              <label class="form-check-label small" :for="'genre-'+g.genre_id">
                {{ g.genre_name }}
              </label>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Дата выпуска</label>
          <input v-model="contentForm.content_publish_date" type="date" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Длительность</label>
          <div class="d-flex align-items-center gap-2">
            <div class="flex-grow-1">
              <input type="number" v-model.number="durationInput.h" @change="validateTime('h')" class="form-control form-control-sm text-center" placeholder="Ч">
              <div class="text-center x-small text-muted">час</div>
            </div>
            <div class="flex-grow-1">
              <input type="number" v-model.number="durationInput.m" @change="validateTime('m')" class="form-control form-control-sm text-center" placeholder="М">
              <div class="text-center x-small text-muted">мин</div>
            </div>
            <div class="flex-grow-1">
              <input type="number" v-model.number="durationInput.s" @change="validateTime('s')" class="form-control form-control-sm text-center" placeholder="С">
              <div class="text-center x-small text-muted">сек</div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Теги</label>
          <div class="border rounded p-2 bg-white form-control checkbox-list-container">
            <div class="form-check mb-1" v-for="t in tagsList" :key="t.tag_id">
              <input class="form-check-input" type="checkbox" :value="t.tag_id" :id="'tag-'+t.tag_id" v-model="contentForm.tag_ids">
              <label class="form-check-label small" :for="'tag-'+t.tag_id">
                {{ t.tag_name }}
              </label>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Правообладатели</label>
          <div class="border rounded p-2 bg-white form-control checkbox-list-container">
            <div class="form-check mb-1" v-for="h in holdersList" :key="h.copyright_holder_id">
              <input class="form-check-input" type="checkbox" :value="h.copyright_holder_id" :id="'holder-'+h.copyright_holder_id" v-model="contentForm.copyright_holder_ids">
              <label class="form-check-label small" :for="'holder-'+h.copyright_holder_id">
                {{ h.copyright_holder_name }}
              </label>
            </div>
          </div>
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

<style scoped>
.last-child-0:last-child {
  border-bottom: 0 !important;
}
.badge {
  font-weight: 500;
}
.x-small {
  font-size: 0.7rem;
}
.cursor-help {
  cursor: help;
}
.checkbox-list-container {
  max-height: 140px;
  overflow-y: auto;
}
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
</style>
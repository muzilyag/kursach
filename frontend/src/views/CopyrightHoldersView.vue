<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { ICopyrightHolder } from '../services/api'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'

const columns = [
  { key: 'copyright_holder_name', label: 'Правообладатель', sortable: true },
  { key: 'contacts', label: 'Контактные данные' }
]

const isEditing = ref(false)
const currentId = ref<number | null>(null)
const holderForm = reactive({
  copyright_holder_name: '',
  copyright_holder_phone: '',
  copyright_holder_email: ''
})

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getCopyrightHoldersDirect(p),
  { sort: 'copyright_holder_id', order: 'desc', limit: 10 }
)

const setEdit = (item: ICopyrightHolder) => {
  isEditing.value = true
  currentId.value = item.copyright_holder_id
  holderForm.copyright_holder_name = item.copyright_holder_name
  holderForm.copyright_holder_phone = item.copyright_holder_phone || ''
  holderForm.copyright_holder_email = item.copyright_holder_email || ''
}

const resetForm = () => {
  isEditing.value = false
  currentId.value = null
  holderForm.copyright_holder_name = ''
  holderForm.copyright_holder_phone = ''
  holderForm.copyright_holder_email = ''
}

const saveHolder = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.updateCopyrightHolder(currentId.value, holderForm)
    } else {
      await ApiService.createCopyrightHolder(holderForm)
    }
    resetForm()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteItem = async (item: ICopyrightHolder) => {
  if (confirm('Удалить правообладателя?')) {
    try {
      await ApiService.deleteCopyrightHolder(item.copyright_holder_id)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

onMounted(load)
</script>

<template>
  <div class="container-fluid py-4">
    <div class="row mb-4 align-items-center">
      <div class="col">
        <h2 class="h3 mb-0 fw-bold">Правообладатели</h2>
      </div>
      <div class="col-md-4">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input v-model="params.search" @input="load" type="text" class="form-control border-start-0" placeholder="Поиск...">
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 sticky-top" style="top: 20px;">
          <div class="card-header bg-white py-3 border-0">
            <h5 class="card-title mb-0 fw-bold">{{ isEditing ? 'Редактировать' : 'Добавить' }}</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveHolder">
              <div class="mb-3">
                <label class="form-label small fw-bold">Название / ФИО</label>
                <input v-model="holderForm.copyright_holder_name" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Телефон</label>
                <input v-model="holderForm.copyright_holder_phone" type="text" class="form-control" placeholder="+7 (___) ___ - __ - __">
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Email</label>
                <input v-model="holderForm.copyright_holder_email" type="email" class="form-control" placeholder="example@mail.com">
              </div>
              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary flex-grow-1">
                  {{ isEditing ? 'Обновить' : 'Сохранить' }}
                </button>
                <button v-if="isEditing" type="button" class="btn btn-light" @click="resetForm">Отмена</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-body p-0">
            <DataTable 
              :columns="columns" 
              :items="items" 
              :has-actions="true"
              :current-page="params.page"
              :page-size="params.limit"
              :sort-config="{ key: params.sort, order: params.order }"
              @sort="handleSort"
              @edit="setEdit"
              @delete="deleteItem"
            >
              <template #cell-copyright_holder_name="{ item }">
                <div class="fw-bold text-dark">{{ item.copyright_holder_name }}</div>
                <div class="text-muted smallest">ID: {{ item.copyright_holder_id }}</div>
              </template>

              <template #cell-contacts="{ item }">
                <div class="d-flex flex-column gap-1">
                  <div v-if="item.copyright_holder_phone" class="small">
                    <i class="bi bi-telephone text-primary me-2"></i>{{ item.copyright_holder_phone }}
                  </div>
                  <div v-if="item.copyright_holder_email" class="small">
                    <i class="bi bi-envelope text-primary me-2"></i>{{ item.copyright_holder_email }}
                  </div>
                  <div v-if="!item.copyright_holder_phone && !item.copyright_holder_email" class="text-muted small italic">
                    Контактные данные не указаны
                  </div>
                </div>
              </template>
            </DataTable>
          </div>
          <div class="card-footer bg-white border-top-0 py-3">
            <Pagination 
              :current-page="params.page" 
              :pages="pages" 
              :total="total" 
              @update:page="(p) => { params.page = p; load(); }" 
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.smallest { font-size: 0.75rem; }
.italic { font-style: italic; }
</style>
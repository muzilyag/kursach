<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { ITag } from '../services/api'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'tag_name', label: 'Название тега', sortable: true }
]

const showModal = ref(false)
const isEditing = ref(false)
const currentId = ref<number | null>(null)
const tagForm = reactive({ tag_name: '' })

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getTagsDirect(p),
  { sort: 'tag_id', order: 'desc', limit: 10 }
)

const openModal = (item: ITag | null = null) => {
  isEditing.value = !!item
  if (item) {
    currentId.value = item.tag_id
    tagForm.tag_name = item.tag_name
  } else {
    currentId.value = null
    tagForm.tag_name = ''
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveTag = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.request(`${Config.api.tagsDirect}/${currentId.value}`, {
        method: 'PUT',
        body: JSON.stringify(tagForm)
      })
    } else {
      await ApiService.createTag(tagForm)
    }
    closeModal()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteItem = async (item: ITag) => {
  if (confirm('Удалить этот тег?')) {
    try {
      await ApiService.deleteTag(item.tag_id)
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
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0 fw-bold">Теги</h2>
      <button class="btn btn-primary" @click="openModal()">
        <i class="bi bi-plus-lg me-2"></i>Добавить тег
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3">
        <div class="row align-items-center">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
              <input v-model="params.search" @input="load" type="text" class="form-control bg-light border-start-0" placeholder="Поиск по названию...">
            </div>
          </div>
        </div>
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
        />
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

    <Modal :show="showModal" :title="isEditing ? 'Редактировать тег' : 'Новый тег'" @close="closeModal">
      <form @submit.prevent="saveTag" id="tagForm">
        <div class="mb-3">
          <label class="form-label small fw-bold">Название тега</label>
          <input v-model="tagForm.tag_name" class="form-control" placeholder="Напр: боевик" required>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn btn-light" @click="closeModal">Отмена</button>
        <button type="submit" form="tagForm" class="btn btn-primary px-4">Сохранить</button>
      </template>
    </Modal>
  </div>
</template>
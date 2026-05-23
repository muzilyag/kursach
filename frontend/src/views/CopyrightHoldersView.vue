<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { ICopyrightHolder } from '../services/api'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'

const columns = [
  { key: 'copyright_holder_name', label: 'Правообладатель', sortable: true },
  { key: 'contacts', label: 'Контакты' },
  { key: 'content_count', label: 'Контент', sortable: true }
]

const isEditing = ref(false)
const currentId = ref<number | null>(null)
const isPanelOpen = ref(false)
const holderForm = reactive({
  copyright_holder_name: '',
  copyright_holder_phone: '',
  copyright_holder_email: '',
  content_ids: [] as number[]
})

const allContent = ref<any[]>([])

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getCopyrightHoldersDirect(p),
  { sort: 'copyright_holder_name', order: 'desc', limit: Config.pagination.itemsPerPage }
)

const loadContent = async () => {
  try {
    const data = await ApiService.getContent({ limit: 10000 })
    allContent.value = data.items
  } catch {}
}

const openPanel = () => {
  isPanelOpen.value = true
}

const closePanel = () => {
  isPanelOpen.value = false
  resetForm()
}

const setEdit = (item: ICopyrightHolder) => {
  isEditing.value = true
  currentId.value = item.copyright_holder_id
  holderForm.copyright_holder_name = item.copyright_holder_name
  holderForm.copyright_holder_phone = item.copyright_holder_phone || ''
  holderForm.copyright_holder_email = item.copyright_holder_email || ''
  holderForm.content_ids = allContent.value
    .filter((c) =>
      c.copyright_holders?.some((h: any) => h.copyright_holder_id === item.copyright_holder_id)
    )
    .map((c) => c.content_id)
  openPanel()
}

const resetForm = () => {
  isEditing.value = false
  currentId.value = null
  holderForm.copyright_holder_name = ''
  holderForm.copyright_holder_phone = ''
  holderForm.copyright_holder_email = ''
  holderForm.content_ids = []
}

const saveHolder = async () => {
  try {
    if (isEditing.value && currentId.value) {
      await ApiService.updateCopyrightHolder(currentId.value, holderForm)
    } else {
      await ApiService.createCopyrightHolder(holderForm)
    }
    closePanel()
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

onMounted(() => {
  load()
  loadContent()
})
</script>

<template>
  <div class="container-fluid py-4">
    <div class="row mb-4 align-items-center">
      <div class="col">
        <h2 class="h3 mb-0 fw-bold">Правообладатели</h2>
      </div>
      <div class="col-md-4 d-flex justify-content-end gap-3">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0"
            ><i class="bi bi-search text-muted"></i
          ></span>
          <input
            v-model="params.search"
            @input="load"
            type="text"
            class="form-control border-start-0"
            placeholder="Поиск..."
          />
        </div>
        <button class="btn btn-primary fw-bold px-4" @click="openPanel()">Добавить</button>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
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
              </template>

              <template #cell-contacts="{ item }">
                <div class="d-flex flex-column gap-1">
                  <div v-if="item.copyright_holder_phone" class="small">
                    <i class="bi bi-telephone text-primary me-2"></i
                    >{{ item.copyright_holder_phone }}
                  </div>
                  <div v-if="item.copyright_holder_email" class="small">
                    <i class="bi bi-envelope text-primary me-2"></i
                    >{{ item.copyright_holder_email }}
                  </div>
                  <div
                    v-if="!item.copyright_holder_phone && !item.copyright_holder_email"
                    class="text-muted small italic"
                  >
                    Контактные данные не указаны
                  </div>
                </div>
              </template>

              <template #cell-content_count="{ item }">
                <div class="fw-semibold text-dark">{{ item.content_count ?? 0 }}</div>
              </template>

              <template #actions="{ item }">
                <button 
                  class="btn btn-sm btn-outline-primary me-2" 
                  @click="setEdit(item)"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-danger" 
                  :disabled="isEditing && currentId === item.copyright_holder_id"
                  @click="deleteItem(item)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </template>
            </DataTable>
          </div>
          <div class="card-footer bg-white border-top-0 py-3">
            <Pagination
              :current-page="params.page"
              :pages="pages"
              :total="total"
              @update:page="
                (p) => {
                  params.page = p
                  load()
                }
              "
            />
          </div>
        </div>
      </div>
    </div>

    <div v-if="isPanelOpen" class="panel-overlay" @click="closePanel"></div>
    <div class="side-panel" :class="{ open: isPanelOpen }">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="mb-0 fw-bold">{{ isEditing ? 'Редактировать' : 'Добавить' }}</h5>
        <button type="button" class="btn-close shadow-none" @click="closePanel"></button>
      </div>

      <form @submit.prevent="saveHolder" class="d-flex flex-column h-100">
        <div class="flex-grow-1">
          <div class="mb-3">
            <label class="form-label small fw-bold">Название / ФИО</label>
            <input
              v-model="holderForm.copyright_holder_name"
              type="text"
              class="form-control"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-bold">Телефон</label>
            <input
              v-model="holderForm.copyright_holder_phone"
              type="text"
              class="form-control"
              placeholder="+7 (___) ___ - __ - __"
            />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-bold">Email</label>
            <input
              v-model="holderForm.copyright_holder_email"
              type="email"
              class="form-control"
              placeholder="example@mail.com"
            />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-bold">Связанный контент</label>
            <div class="border rounded p-2 bg-light form-control checkbox-list-container">
              <div class="form-check mb-1" v-for="c in allContent" :key="c.content_id">
                <input
                  class="form-check-input"
                  type="checkbox"
                  :value="c.content_id"
                  :id="'content-' + c.content_id"
                  v-model="holderForm.content_ids"
                />
                <label class="form-check-label small" :for="'content-' + c.content_id">
                  {{ c.content_name }}
                </label>
              </div>
              <div v-if="allContent.length === 0" class="text-muted small">Контент не найден</div>
            </div>
          </div>
        </div>
        
        <div class="d-flex gap-2 mt-4 pb-4">
          <button type="submit" class="btn btn-primary flex-grow-1 fw-bold">
            {{ isEditing ? 'Обновить' : 'Сохранить' }}
          </button>
          <button type="button" class="btn btn-light fw-bold" @click="closePanel">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.italic {
  font-style: italic;
}
.checkbox-list-container {
  max-height: 250px;
  overflow-y: auto;
}

.panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  z-index: 1040;
}

.side-panel {
  position: fixed;
  top: 0;
  right: -450px;
  width: 450px;
  height: 100vh;
  background: #fff;
  z-index: 1050;
  transition: right 0.3s cubic-bezier(0.82, 0.085, 0.395, 0.895);
  box-shadow: -5px 0 25px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
}

.side-panel.open {
  right: 0;
}
</style>
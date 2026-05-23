<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type { IAdvertising, IAdvertisingCreate, ITag } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'advertising_name', label: 'Название', sortable: true },
  { key: 'advertising_owner', label: 'Заказчик', sortable: true },
  { key: 'dates', label: 'Период показа' },
  { key: 'advertising_duration', label: 'Длительность', sortable: true },
  { key: 'is_active', label: 'Статус' }
]

const tagsList = ref<ITag[]>([])
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
  (p) => ApiService.getAdvertising(p),
  { 
    sort: 'advertising_id', 
    order: 'desc', 
    limit: Config.pagination.itemsPerPage, 
    owner: '',
    show_expired: false
  }
)

const form = reactive<IAdvertisingCreate>({
  advertising_name: '',
  advertising_duration: '00:00:00',
  advertising_owner: '',
  advertising_start_date: new Date().toISOString().split('T')[0] ?? '',
  advertising_finish_date: new Date().toISOString().split('T')[0] ?? '',
  content_ids: [],
  tag_ids: []
})

const openModal = (item: IAdvertising | null = null) => {
  isEditing.value = !!item
  if (item) {
    currentId.value = item.advertising_id
    const [h, m, s] = (item.advertising_duration || '00:00:00').split(':').map(Number)
    durationInput.h = h ?? 0
    durationInput.m = m ?? 0
    durationInput.s = s ?? 0

    Object.assign(form, {
      advertising_name: item.advertising_name || '',
      advertising_owner: item.advertising_owner,
      advertising_start_date: item.advertising_start_date.split('T')[0],
      advertising_finish_date: item.advertising_finish_date.split('T')[0],
      content_ids: item.content_ids || [],
      tag_ids: item.tag_ids || []
    })
  } else {
    currentId.value = null
    durationInput.h = 0
    durationInput.m = 0
    durationInput.s = 15
    Object.assign(form, {
      advertising_name: '',
      advertising_owner: '',
      advertising_start_date: new Date().toISOString().split('T')[0],
      advertising_finish_date: new Date().toISOString().split('T')[0],
      content_ids: [],
      tag_ids: []
    })
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveItem = async () => {
  try {
    const pad = (n: number) => String(n).padStart(2, '0')
    form.advertising_duration = `${pad(durationInput.h)}:${pad(durationInput.m)}:${pad(durationInput.s)}`

    if (isEditing.value && currentId.value) {
      await ApiService.updateAdvertising(currentId.value, form)
    } else {
      await ApiService.createAdvertising(form)
    }
    closeModal()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const deleteItem = async (item: IAdvertising) => {
  if (confirm('Удалить рекламную кампанию?')) {
    try {
      await ApiService.deleteAdvertising(item.advertising_id)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

onMounted(async () => {
  load()
  try {
    const t = await ApiService.getTagsDirect({ limit: 1000 })
    tagsList.value = t.items
  } catch {}
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Реклама</h2>
      <button class="btn btn-primary" @click="openModal()">
        <i class="bi bi-plus-lg me-2"></i>Добавить кампанию
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3">
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <div class="input-group" style="width: 250px">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-search"></i></span>
              <input
                v-model="params.owner"
                @input="load"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="Поиск по заказчику..."
              />
            </div>
            <div class="form-check form-switch mb-0">
              <input
                class="form-check-input"
                type="checkbox"
                id="expiredAdsSwitch"
                v-model="params.show_expired"
              />
              <label class="form-check-label small text-muted" for="expiredAdsSwitch">
                Показать истёкшие
              </label>
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
        >
          <template #cell-advertising_name="{ item }">
            <div class="fw-bold text-dark">{{ item.advertising_name || 'Без названия' }}</div>
          </template>

          <template #cell-dates="{ item }">
            <div class="small">
              <span class="text-muted">От:</span> {{ Utils.formatDate(item.advertising_start_date) }}<br/>
              <span class="text-muted">До:</span> {{ Utils.formatDate(item.advertising_finish_date) }}
            </div>
          </template>

          <template #cell-advertising_duration="{ item }">
            {{ Utils.formatDuration(item.advertising_duration) }}
          </template>

          <template #cell-is_active="{ item }">
            <span
              class="badge"
              :class="item.is_active ? 'bg-success' : 'bg-secondary'"
            >
              {{ item.is_active ? 'Активна' : 'Неактивна' }}
            </span>
          </template>
        </DataTable>
      </div>
      <div class="card-footer bg-white border-top-0">
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

    <Modal
      :show="showModal"
      :title="isEditing ? 'Редактировать кампанию' : 'Новая рекламная кампания'"
      @close="closeModal"
    >
      <form @submit.prevent="saveItem" id="advertisingForm" class="row g-3">
        <div class="col-md-6">
          <label class="form-label small fw-bold">Название кампании</label>
          <input v-model="form.advertising_name" class="form-control" placeholder="Опционально" />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Заказчик</label>
          <input v-model="form.advertising_owner" class="form-control" required />
        </div>
        
        <div class="col-md-6">
          <label class="form-label small fw-bold">Дата начала</label>
          <input v-model="form.advertising_start_date" type="date" class="form-control" required />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-bold">Дата окончания</label>
          <input v-model="form.advertising_finish_date" type="date" class="form-control" required />
        </div>

        <div class="col-12">
          <label class="form-label small fw-bold">Длительность креатива</label>
          <div class="d-flex align-items-center gap-2" style="max-width: 300px;">
            <div class="flex-grow-1">
              <input
                type="number"
                v-model.number="durationInput.h"
                @change="validateTime('h')"
                class="form-control form-control-sm text-center"
                placeholder="Ч"
              />
              <div class="text-center x-small text-muted">час</div>
            </div>
            <div class="flex-grow-1">
              <input
                type="number"
                v-model.number="durationInput.m"
                @change="validateTime('m')"
                class="form-control form-control-sm text-center"
                placeholder="М"
              />
              <div class="text-center x-small text-muted">мин</div>
            </div>
            <div class="flex-grow-1">
              <input
                type="number"
                v-model.number="durationInput.s"
                @change="validateTime('s')"
                class="form-control form-control-sm text-center"
                placeholder="С"
              />
              <div class="text-center x-small text-muted">сек</div>
            </div>
          </div>
        </div>

        <div class="col-12 mt-2">
          <h6 class="fw-bold border-bottom pb-2">Таргетинг показа</h6>
        </div>

        <div class="col-12">
          <label class="form-label small fw-bold">Привязка к тегам</label>
          <div class="border rounded p-2 bg-white form-control checkbox-list-container">
            <div class="form-check mb-1" v-for="t in tagsList" :key="t.tag_id">
              <input
                class="form-check-input"
                type="checkbox"
                :value="t.tag_id"
                :id="'tag-' + t.tag_id"
                v-model="form.tag_ids"
              />
              <label class="form-check-label small" :for="'tag-' + t.tag_id">
                {{ t.tag_name }}
              </label>
            </div>
          </div>
        </div>

      </form>
      <template #footer>
        <button type="button" class="btn btn-light" @click="closeModal">Отмена</button>
        <button type="submit" form="advertisingForm" class="btn btn-primary px-4">Сохранить</button>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.x-small {
  font-size: 0.7rem;
}
.checkbox-list-container {
  max-height: 180px;
  overflow-y: auto;
}
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
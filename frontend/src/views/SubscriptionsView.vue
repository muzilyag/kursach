<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { ISubscription, ISubscribeType, ISubscriptionChangeRequest } from '../services/api'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'
import Modal from '../components/Modal.vue'

const columns = [
  { key: 'user_name', label: 'Пользователь' },
  { key: 'subscribe_type_name', label: 'Тариф' },
  { key: 'subscribe_start', label: 'Начало', sortable: true },
  { key: 'subscribe_finish', label: 'Окончание', sortable: true },
  { key: 'status', label: 'Статус' }
]

const subTypes = ref<ISubscribeType[]>([])
const showModal = ref(false)
const isCreating = ref(false)

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getSubscriptions(p),
  { sort: 'subscribe_start', order: 'desc' }
)

const changeForm = reactive<ISubscriptionChangeRequest>({
  user_id: 0,
  subscribe_type_id: 0,
  payment_method: 'карта'
})

const openModal = (isCreate: boolean, sub: ISubscription | null = null) => {
  isCreating.value = isCreate
  if (sub) {
    changeForm.user_id = sub.user_id
    changeForm.subscribe_type_id = sub.subscribe_type_id
  } else {
    changeForm.user_id = 0
    changeForm.subscribe_type_id = subTypes.value[0]?.subscribe_type_id ?? 0
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const submitForm = async () => {
  try {
    if (isCreating.value) {
      await ApiService.request(`${params.base}/subscriptions`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: changeForm.user_id,
          subscribe_type_id: changeForm.subscribe_type_id,
          subscribe_start: new Date().toISOString().split('T')[0]
        })
      })
    } else {
      await ApiService.changeSubscription(changeForm)
    }
    closeModal()
    load()
  } catch (e: any) {
    alert(e.message)
  }
}

const cancelSub = async (sub: ISubscription) => {
  if (confirm('Отменить подписку пользователя?')) {
    try {
      await ApiService.cancelSubscription(sub.user_id, sub.subscribe_type_id, sub.subscribe_start)
      load()
    } catch (e: any) {
      alert(e.message)
    }
  }
}

onMounted(async () => {
  load()
  try {
    subTypes.value = await ApiService.getSubscriptionTypes()
  } catch (e) {}
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 mb-0">Подписки</h2>
      <button class="btn btn-primary" @click="openModal(true)">
        <i class="bi bi-credit-card me-2"></i>Оформить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3">
        <input v-model="params.search" @input="load" type="text" class="form-control w-25" placeholder="Поиск...">
      </div>
      <div class="card-body p-0">
        <DataTable :columns="columns" :items="items" :has-actions="true" @sort="handleSort">
          <template #cell-user_name="{ item }">{{ item.user?.user_name || `ID: ${item.user_id}` }}</template>
          <template #cell-subscribe_type_name="{ item }">{{ item.subscribe_type?.subscribe_type_name || '—' }}</template>
          <template #cell-subscribe_start="{ item }">{{ Utils.formatDate(item.subscribe_start) }}</template>
          <template #cell-subscribe_finish="{ item }">{{ Utils.formatDate(item.subscribe_finish) }}</template>
          <template #cell-status="{ item }">
            <span class="badge" :class="item.status === 'Активна' ? 'bg-success-subtle text-success' : 'bg-light text-muted'">
              {{ item.status }}
            </span>
          </template>
          <template #actions="{ item }">
             <button class="btn btn-sm btn-outline-primary me-2" @click="openModal(false, item)" title="Сменить тариф">
               <i class="bi bi-arrow-repeat"></i>
             </button>
             <button v-if="item.status === 'Активна'" class="btn btn-sm btn-outline-danger" @click="cancelSub(item)" title="Аннулировать">
               <i class="bi bi-slash-circle"></i>
             </button>
          </template>
        </DataTable>
      </div>
      <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="(p) => { params.page = p; load(); }" />
    </div>

    <Modal :show="showModal" :title="isCreating ? 'Новая подписка' : 'Смена тарифа'" @close="closeModal">
      <form @submit.prevent="submitForm" id="subActionForm">
        <div v-if="isCreating" class="mb-3">
          <label class="form-label small fw-bold">ID Пользователя</label>
          <input v-model="changeForm.user_id" type="number" class="form-control" required>
        </div>
        <div v-else class="mb-3">
          <label class="form-label small fw-bold">Пользователь ID</label>
          <input :value="changeForm.user_id" class="form-control" disabled>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold">Выберите тариф</label>
          <select v-model="changeForm.subscribe_type_id" class="form-select" required>
            <option v-for="t in subTypes" :key="t.subscribe_type_id" :value="t.subscribe_type_id">
              {{ t.subscribe_type_name }} ({{ t.subscribe_type_cost }} ₽)
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-bold">Метод оплаты</label>
          <select v-model="changeForm.payment_method" class="form-select">
            <option value="карта">Банковская карта</option>
            <option value="сбп">СБП</option>
            <option value="криптовалюта">Криптовалюта</option>
          </select>
        </div>
      </form>
      <template #footer>
         <button type="button" class="btn btn-light" @click="closeModal">Отмена</button>
         <button type="submit" form="subActionForm" class="btn btn-primary px-4">Подтвердить</button>
      </template>
    </Modal>
  </div>
</template>
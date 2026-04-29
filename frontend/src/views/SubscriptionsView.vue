<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ApiService } from '../services/api'
import type { ISubscription, ISubscribeType, ISubscriptionChangeRequest } from '../services/api'
import { Config } from '../config'
import { Utils } from '../utils'
import { useDataTable } from '../composables/useDataTable'
import DataTable from '../components/DataTable.vue'
import Pagination from '../components/Pagination.vue'

const columns = [
  { key: 'user_name', label: 'Пользователь' },
  { key: 'subscribe_type_name', label: 'Тариф' },
  { key: 'subscribe_start', label: 'Начало' },
  { key: 'subscribe_finish', label: 'Окончание' },
  { key: 'status', label: 'Статус' }
]

const subTypes = ref<ISubscribeType[]>([])
const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getSubscriptions(p),
  { sort: 'subscribe_start', order: 'desc' }
)

const isCreating = ref(false)
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
    changeForm.subscribe_type_id = subTypes.value.length > 0 ? (subTypes.value[0]?.subscribe_type_id ?? 0) : 0
  }
}

const submitForm = async () => {
  try {
    if (isCreating.value) {
      await ApiService.request(Config.api.subscriptions, {
        method: 'POST',
        body: JSON.stringify({
          user_id: changeForm.user_id,
          subscribe_type_id: changeForm.subscribe_type_id,
          subscribe_start: new Date().toISOString().split('T')[0] as string,
          subscribe_finish: new Date(new Date().setDate(new Date().getDate() + 30)).toISOString().split('T')[0] as string
        })
      })
    } else {
      await ApiService.changeSubscription(changeForm)
    }
    load()
  } catch (e: any) {
    alert(`Ошибка: ${e.message}`)
  }
}

const cancelSub = async (sub: ISubscription) => {
  if (confirm('Отменить подписку?')) {
    try {
      await ApiService.cancelSubscription(sub.user_id, sub.subscribe_type_id, sub.subscribe_start)
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
  subTypes.value = await ApiService.getSubscriptionTypes()
})
</script>

<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Управление подписками</h2>
      <button class="btn btn-primary shadow-sm" @click="openModal(true)" data-bs-toggle="modal" data-bs-target="#actionModal">
        <i class="bi bi-credit-card me-2"></i>Оформить
      </button>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white p-3 border-bottom">
        <input v-model="params.search" @input="load" type="text" class="form-control w-25" placeholder="Поиск подписок...">
      </div>
      <div class="card-body p-0">
        <DataTable :columns="columns" :items="items" :has-actions="true" @sort="handleSort">
          <template #cell-user_name="{ item }">{{ item.user?.user_name || item.user_id }}</template>
          <template #cell-subscribe_type_name="{ item }">{{ item.subscribe_type?.subscribe_type_name || '—' }}</template>
          <template #cell-subscribe_start="{ item }">{{ Utils.formatDate(item.subscribe_start) }}</template>
          <template #cell-subscribe_finish="{ item }">{{ Utils.formatDate(item.subscribe_finish) }}</template>
          <template #cell-status="{ item }">
            <span class="badge" :class="'bg-' + (item.status === 'Активна' ? 'success' : 'secondary')">
              {{ item.status }}
            </span>
          </template>
          <template #cell-actions="{ item }">
             <button title="Сменить тариф" class="btn btn-sm btn-outline-primary me-2" @click="openModal(false, item)" data-bs-toggle="modal" data-bs-target="#actionModal">
               <i class="bi bi-arrow-repeat"></i>
             </button>
             <button title="Отменить" v-if="item.status === 'Активна'" class="btn btn-sm btn-outline-danger" @click="cancelSub(item)">
               <i class="bi bi-x-circle"></i>
             </button>
          </template>
        </DataTable>
      </div>
      <Pagination :current-page="params.page" :pages="pages" :total="total" @update:page="onPageChange" />
    </div>

    <div class="modal fade" id="actionModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">{{ isCreating ? 'Новая подписка' : 'Смена тарифа' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitForm" id="actionForm">
              <div v-if="isCreating" class="mb-3">
                <label class="form-label text-secondary small fw-bold">ID Пользователя</label>
                <input v-model="changeForm.user_id" type="number" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label text-secondary small fw-bold">Тариф</label>
                <select v-model="changeForm.subscribe_type_id" class="form-select">
                  <option v-for="t in subTypes" :key="t.subscribe_type_id" :value="t.subscribe_type_id">
                    {{ t.subscribe_type_name }} ({{ t.subscribe_type_cost }}₽)
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label text-secondary small fw-bold">Метод оплаты</label>
                <select v-model="changeForm.payment_method" class="form-select">
                  <option value="карта">Карта</option>
                  <option value="сбп">СБП</option>
                  <option value="криптовалюта">Криптовалюта</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer border-0">
             <button type="button" class="btn btn-light" data-bs-dismiss="modal">Отмена</button>
             <button type="submit" form="actionForm" class="btn btn-primary px-4" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
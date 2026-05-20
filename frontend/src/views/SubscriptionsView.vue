<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ApiService } from '../services/api'
import { Config } from '../config'
import type {
  ISubscription,
  ISubscribeType,
  ISubscriptionChangeRequest,
  IUser
} from '../services/api'
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
const usersList = ref<IUser[]>([])
const availableUsers = ref<IUser[]>([])
const showModal = ref(false)
const isCreating = ref(false)

const selectedTierName = ref('')
const selectedDuration = ref<number | null>(null)

const { items, total, params, pages, load, handleSort } = useDataTable(
  (p) => ApiService.getSubscriptions(p),
  {
    sort: 'subscribe_start',
    order: 'desc',
    show_expired: false,
    limit: Config.pagination.itemsPerPage
  }
)

const changeForm = reactive<ISubscriptionChangeRequest>({
  user_id: 0,
  subscribe_type_id: 0,
  payment_method: 'карта'
})

const availableTiers = computed(() => {
  const names = subTypes.value.map((t) => t.subscribe_type_name)
  return [...new Set(names)]
})

const availablePeriods = computed(() => {
  if (!selectedTierName.value) return []
  return subTypes.value.filter((t) => t.subscribe_type_name === selectedTierName.value)
})

const selectedFullType = computed(() => {
  return subTypes.value.find(
    (t) =>
      t.subscribe_type_name === selectedTierName.value &&
      t.subscribe_type_duration === selectedDuration.value
  )
})

const calculatedEndDate = computed(() => {
  if (!selectedFullType.value) return null
  const date = new Date()
  date.setDate(date.getDate() + selectedFullType.value.subscribe_type_duration)
  return date.toLocaleDateString('ru-RU')
})

watch(selectedFullType, (newType) => {
  if (newType) {
    changeForm.subscribe_type_id = newType.subscribe_type_id
  }
})

const openModal = async (isCreate: boolean, sub: ISubscription | null = null) => {
  isCreating.value = isCreate

  if (isCreate) {
    try {
      const res = await ApiService.getFilteredUsers({ has_active: false })
      availableUsers.value = res
    } catch (e) {
      console.error(e)
    }
    changeForm.user_id = 0
    selectedTierName.value = availableTiers.value[0] || ''
    selectedDuration.value = null
  } else {
    if (sub) {
      changeForm.user_id = sub.user_id
      selectedTierName.value = sub.subscribe_type?.subscribe_type_name || ''
      selectedDuration.value = sub.subscribe_type?.subscribe_type_duration || null
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedDuration.value = null
}

const submitForm = async () => {
  try {
    if (isCreating.value) {
      const startDate = new Date()
      const finishDate = new Date()
      if (selectedFullType.value) {
        finishDate.setDate(startDate.getDate() + selectedFullType.value.subscribe_type_duration)
      }

      await ApiService.createSubscription({
        user_id: Number(changeForm.user_id),
        subscribe_type_id: changeForm.subscribe_type_id,
        subscribe_start: startDate.toISOString().split('T')[0],
        subscribe_finish: finishDate.toISOString().split('T')[0]
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

const getUserDisplayName = (id: number) => {
  const user = usersList.value.find((u) => u.user_id === id)
  return user ? `${user.user_name} (${user.user_email})` : `ID: ${id}`
}

const formatDuration = (days: number) => {
  if (days === 30) return '1 месяц'
  if (days === 90) return '3 месяца'
  if (days === 180) return 'Полгода'
  if (days === 365) return '1 год'
  return `${days} дн.`
}

onMounted(async () => {
  load()
  try {
    const [typesRes, usersRes] = await Promise.all([
      ApiService.getSubscriptionTypes(),
      ApiService.getUsers({ limit: 1000 })
    ])
    subTypes.value = typesRes
    usersList.value = usersRes.users || []
  } catch {}
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
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <input
              v-model="params.search"
              type="text"
              class="form-control"
              style="width: 250px"
              placeholder="Поиск..."
            />
            <div class="form-check form-switch mb-0">
              <input
                class="form-check-input"
                type="checkbox"
                id="expiredSwitch"
                v-model="params.show_expired"
              />
              <label class="form-check-label small text-muted" for="expiredSwitch"
                >Показать истёкшие</label
              >
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
        >
          <template #cell-user_name="{ item }">{{
            item.user?.user_name || `ID: ${item.user_id}`
          }}</template>
          <template #cell-subscribe_type_name="{ item }">{{
            item.subscribe_type?.subscribe_type_name || '—'
          }}</template>
          <template #cell-subscribe_start="{ item }">{{
            Utils.formatDate(item.subscribe_start)
          }}</template>
          <template #cell-subscribe_finish="{ item }">{{
            Utils.formatDate(item.subscribe_finish)
          }}</template>
          <template #cell-status="{ item }">
            <span
              class="badge"
              :class="
                item.status === 'Активна' ? 'bg-success-subtle text-success' : 'bg-light text-muted'
              "
            >
              {{ item.status }}
            </span>
          </template>

          <template #actions="{ item }">
            <template v-if="item.status === 'Активна'">
              <button
                class="btn btn-sm btn-outline-primary me-2"
                @click="openModal(false, item)"
                title="Сменить тариф"
              >
                <i class="bi bi-arrow-repeat"></i>
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                @click="cancelSub(item)"
                title="Аннулировать"
              >
                <i class="bi bi-slash-circle"></i>
              </button>
            </template>
            <span v-else class="text-muted small italic">Действия недоступны</span>
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
      :title="isCreating ? 'Новая подписка' : 'Смена тарифа'"
      @close="closeModal"
    >
      <form @submit.prevent="submitForm" id="subActionForm">
        <div v-if="isCreating" class="mb-3">
          <label class="form-label small fw-bold">Пользователь</label>
          <select v-model="changeForm.user_id" class="form-select" required>
            <option :value="0" disabled>Выберите пользователя...</option>
            <option v-for="u in availableUsers" :key="u.user_id" :value="u.user_id">
              {{ u.user_name }} ({{ u.user_email || 'Email не указан' }})
            </option>
          </select>
          <div v-if="availableUsers && availableUsers.length === 0" class="form-text text-danger">
            Нет доступных пользователей без активных подписок.
          </div>
        </div>
        <div v-else class="mb-3">
          <label class="form-label small fw-bold">Пользователь</label>
          <input :value="getUserDisplayName(changeForm.user_id)" class="form-control" disabled />
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold">Вид подписки</label>
            <select
              v-model="selectedTierName"
              class="form-select"
              required
              @change="selectedDuration = null"
            >
              <option value="" disabled>Выберите вид...</option>
              <option v-for="name in availableTiers" :key="name" :value="name">{{ name }}</option>
            </select>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label small fw-bold">Период</label>
            <select
              v-model="selectedDuration"
              class="form-select"
              :disabled="!selectedTierName"
              required
            >
              <option :value="null" disabled>Выберите срок...</option>
              <option
                v-for="p in availablePeriods"
                :key="p.subscribe_type_id"
                :value="p.subscribe_type_duration"
              >
                {{ formatDuration(p.subscribe_type_duration) }}
              </option>
            </select>
          </div>
        </div>

        <div
          v-if="selectedFullType"
          class="alert alert-info py-2 px-3 border-0 shadow-sm bg-primary-subtle text-primary-emphasis mb-3"
        >
          <div class="d-flex justify-content-between align-items-center">
            <span
              >Стоимость: <strong>{{ selectedFullType.subscribe_type_cost }} ₽</strong></span
            >
            <span class="small"
              >До: <strong>{{ calculatedEndDate }}</strong></span
            >
          </div>
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
        <button
          type="submit"
          form="subActionForm"
          class="btn btn-primary px-4"
          :disabled="!selectedFullType || changeForm.user_id === 0"
        >
          Подтвердить
        </button>
      </template>
    </Modal>
  </div>
</template>

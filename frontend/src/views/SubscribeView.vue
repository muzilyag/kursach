<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ApiService, type ISubscribeType, type IUser } from '../services/api'
import PlanCard from '../components/PlanCard.vue'

const router = useRouter()
const plans = ref<ISubscribeType[]>([])
const currentUser = ref<IUser | null>(null)
const isLoading = ref(true)
const isProcessing = ref(false)
const selectedPayment = ref<'карта' | 'сбп' | 'криптовалюта'>('карта')

const selectedOptions = ref<Record<string, ISubscribeType>>({})

const loadData = async () => {
  try {
    const [plansData, userData] = await Promise.all([
      ApiService.getSubscriptionTypes(),
      ApiService.getMe().catch(() => null)
    ])
    plans.value = plansData
    currentUser.value = userData

    const activeSub = userData?.active_subscription

    plansData.forEach(plan => {
      const name = plan.subscribe_type_name
      
      if (activeSub && activeSub.status === 'Активна' && activeSub.subscribe_type_id === plan.subscribe_type_id) {
        selectedOptions.value[name] = plan
      } else if (!selectedOptions.value[name]) {
        selectedOptions.value[name] = plan
      } else if (
        (!activeSub || activeSub.subscribe_type_name !== name) && 
        plan.subscribe_type_duration < selectedOptions.value[name]!.subscribe_type_duration
      ) {
        selectedOptions.value[name] = plan
      }
    })
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const demoPlan = computed(() => {
  return plans.value.find(p => p.subscribe_type_cost === 0 || p.subscribe_type_name.toLowerCase().includes('демо'))
})

const groupedPlans = computed(() => {
  const groups: Record<string, {
    name: string
    discription: string | null
    max_quality: number
    options: ISubscribeType[]
  }> = {}

  plans.value.forEach(plan => {
    const isDemo = plan.subscribe_type_cost === 0 || plan.subscribe_type_name.toLowerCase().includes('демо')
    if (isDemo) return

    if (!groups[plan.subscribe_type_name]) {
      groups[plan.subscribe_type_name] = {
        name: plan.subscribe_type_name,
        discription: plan.subscribe_type_discription,
        max_quality: plan.subscribe_type_max_type_quality,
        options: []
      }
    }
    groups[plan.subscribe_type_name]!.options.push(plan)
  })

  Object.values(groups).forEach(g => {
    g.options.sort((a, b) => a.subscribe_type_duration - b.subscribe_type_duration)
  })

  return Object.values(groups)
})

const handleAction = async (planId?: number) => {
  if (!planId) return
  isProcessing.value = true
  try {
    const activeSub = currentUser.value?.active_subscription
    const isRenewing = activeSub?.subscribe_type_id === planId

    if (activeSub && !isRenewing) {
      await ApiService.changeSubscription({
        user_id: currentUser.value!.user_id,
        subscribe_type_id: planId,
        payment_method: selectedPayment.value
      })
      alert('Тариф успешно изменен!')
    } else {
      await ApiService.buySubscription({
        subscribe_type_id: planId,
        payment_method: selectedPayment.value
      })
      alert(isRenewing ? 'Подписка успешно продлена!' : 'Подписка успешно оформлена!')
    }
    router.push('/profile')
  } catch (e: any) {
    alert(e.message || 'Ошибка при обработке операции')
  } finally {
    isProcessing.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="container py-5">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold" style="color: var(--text-darker)">Выберите ваш план</h1>
      <p class="text-muted">
        Откройте доступ к эксклюзивному контенту MishlenKino в лучшем качестве.
      </p>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border" style="color: var(--sidebar-primary)"></div>
    </div>

    <div v-else-if="currentUser && currentUser.user_role !== 'user'" class="text-center py-5">
      <div class="alert alert-info d-inline-block px-5 py-4 shadow-sm border-0 rounded-4">
        <i class="bi bi-shield-check fs-1 text-primary mb-3 d-block"></i>
        <h4 class="fw-bold">Вы — сотрудник платформы</h4>
        <p class="mb-0 text-muted">Сотрудникам платформы подписка не требуется. У вас уже есть неограниченный доступ ко всему контенту!</p>
      </div>
    </div>

    <div v-else class="d-flex flex-column align-items-center gap-4">
      <div v-if="demoPlan && (!currentUser?.had_subscription || currentUser?.active_subscription?.subscribe_type_id === demoPlan.subscribe_type_id)" class="w-100 d-flex justify-content-center mb-2">
        <div class="card border-0 shadow-sm demo-card p-3 text-center">
          <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div class="text-start">
              <span class="badge bg-warning text-dark mb-1 fw-bold text-uppercase smallest-badge">пробный период</span>
              <h5 class="fw-bold m-0 text-dark">{{ demoPlan.subscribe_type_name }}</h5>
              <p class="small text-muted m-0 mt-1">{{ demoPlan.subscribe_type_discription || 'Ознакомительный период для новых пользователей' }}</p>
            </div>
            <div class="d-flex align-items-center gap-4">
              <div class="fs-4 fw-bold text-success text-nowrap">{{ demoPlan.subscribe_type_cost }} ₽<span class="fs-6 text-muted fw-normal">/ {{ demoPlan.subscribe_type_duration }} дн.</span></div>
              <button
                @click="handleAction(demoPlan.subscribe_type_id)"
                :disabled="isProcessing || currentUser?.active_subscription?.subscribe_type_id === demoPlan.subscribe_type_id"
                class="btn btn-sm btn-primary fw-bold px-4 py-2 rounded-3 text-nowrap"
                style="background-color: var(--sidebar-primary); border: none;"
              >
                <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
                {{ currentUser?.active_subscription?.subscribe_type_id === demoPlan.subscribe_type_id ? 'Текущий' : 'Активировать' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <div class="d-flex justify-content-center gap-3">
          <div
            @click="selectedPayment = 'карта'"
            class="payment-badge"
            :class="{ active: selectedPayment === 'карта' }"
          >
            КАРТА
          </div>
          <div
            @click="selectedPayment = 'сбп'"
            class="payment-badge"
            :class="{ active: selectedPayment === 'сбп' }"
          >
            СБП
          </div>
          <div
            @click="selectedPayment = 'криптовалюта'"
            class="payment-badge"
            :class="{ active: selectedPayment === 'криптовалюта' }"
          >
            КРИПТА
          </div>
        </div>
      </div>

      <div class="row g-4 justify-content-center w-100">
        <div v-for="group in groupedPlans" :key="group.name" class="col-md-4">
          <PlanCard
            :group="group"
            v-model:selected-option="selectedOptions[group.name]"
            :current-sub-id="currentUser?.active_subscription?.subscribe_type_id"
            :is-processing="isProcessing"
            :has-active-sub="!!currentUser?.active_subscription"
            @action="handleAction"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.payment-badge {
  padding: 8px 20px;
  border-radius: 50px;
  background: #eee;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s;
  color: #666;
}
.payment-badge.active {
  background: var(--sidebar-primary);
  color: white;
}
.demo-card {
  border-radius: 16px;
  max-width: 650px;
  width: 100%;
  background: var(--card-bg);
  border: 1px dashed var(--sidebar-primary);
}
.smallest-badge {
  font-size: 0.65rem;
}
</style>
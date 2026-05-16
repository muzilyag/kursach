<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ApiService, type ISubscribeType, type IUser } from '../services/api'

const router = useRouter()
const plans = ref<ISubscribeType[]>([])
const currentUser = ref<IUser | null>(null)
const isLoading = ref(true)
const isProcessing = ref(false)
const selectedPayment = ref<'карта' | 'сбп' | 'криптовалюта'>('карта')

const loadData = async () => {
  try {
    const [plansData, userData] = await Promise.all([
      ApiService.getSubscriptionTypes(),
      ApiService.getMe().catch(() => null)
    ])
    plans.value = plansData
    currentUser.value = userData
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const handleAction = async (planId: number) => {
  isProcessing.value = true
  try {
    if (currentUser.value?.active_subscription) {
      await ApiService.changeSubscription({
        user_id: currentUser.value.user_id,
        subscribe_type_id: planId,
        payment_method: selectedPayment.value
      })
      alert('Тариф успешно изменен!')
    } else {
      await ApiService.buySubscription({
        subscribe_type_id: planId,
        payment_method: selectedPayment.value
      })
      alert('Подписка успешно оформлена!')
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
      <h1 class="display-5 fw-bold" style="color: var(--text-darker);">Выберите ваш план</h1>
      <p class="text-muted">Откройте доступ к эксклюзивному контенту MishlenKino в лучшем качестве.</p>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border" style="color: var(--sidebar-primary);"></div>
    </div>

    <div v-else class="row g-4 justify-content-center">
      <div class="col-12 mb-4">
        <div class="d-flex justify-content-center gap-3">
          <div @click="selectedPayment = 'карта'"
               class="payment-badge" :class="{ active: selectedPayment === 'карта' }">
            КАРТА
          </div>
          <div @click="selectedPayment = 'сбп'"
               class="payment-badge" :class="{ active: selectedPayment === 'сбп' }">
            СБП
          </div>
          <div @click="selectedPayment = 'криптовалюта'"
               class="payment-badge" :class="{ active: selectedPayment === 'криптовалюта' }">
            КРИПТА
          </div>
        </div>
      </div>

      <div v-for="plan in plans" :key="plan.subscribe_type_id" class="col-md-4">
        <div class="card h-100 border-0 shadow-sm plan-card" 
             :class="{ 'current-plan-border': currentUser?.active_subscription?.subscribe_type_id === plan.subscribe_type_id }">
          <div class="card-body p-4 text-center d-flex flex-column">
            <h3 class="fw-bold mb-3">{{ plan.subscribe_type_name }}</h3>
            <div class="price mb-4">
              <span class="display-4 fw-bold">{{ plan.subscribe_type_cost }}</span>
              <span class="text-muted"> ₽</span>
            </div>
            <ul class="list-unstyled mb-4 flex-grow-1 text-start">
              <li class="mb-2"><i class="bi bi-check2-circle me-2 text-success"></i> Доступ на {{ plan.subscribe_type_duration }} дней</li>
              <li class="mb-2"><i class="bi bi-check2-circle me-2 text-success"></i> Качество до {{ plan.subscribe_type_max_type_quality }}p</li>
              <li class="text-muted small">{{ plan.subscribe_type_discription }}</li>
            </ul>
            
            <button @click="handleAction(plan.subscribe_type_id)" 
                    :disabled="isProcessing || currentUser?.active_subscription?.subscribe_type_id === plan.subscribe_type_id"
                    class="btn w-100 py-3 fw-bold purchase-btn"
                    :class="currentUser?.active_subscription?.subscribe_type_id === plan.subscribe_type_id ? 'btn-secondary' : 'btn-primary'">
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
              <span v-if="currentUser?.active_subscription?.subscribe_type_id === plan.subscribe_type_id">Текущий тариф</span>
              <span v-else-if="currentUser?.active_subscription">Сменить тариф</span>
              <span v-else>Оформить подписку</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plan-card {
  border-radius: 24px;
  transition: all 0.3s ease;
  background: var(--card-bg);
  border: 1px solid transparent;
}
.plan-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1) !important;
  border: 1px solid var(--sidebar-primary) !important;
}
.current-plan-border {
  border: 2px solid var(--sidebar-primary) !important;
}
.purchase-btn.btn-primary {
  background-color: var(--sidebar-primary);
  border: none;
  border-radius: 12px;
}
.purchase-btn.btn-secondary {
  border-radius: 12px;
  background-color: #6c757d;
  border: none;
}
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
</style>
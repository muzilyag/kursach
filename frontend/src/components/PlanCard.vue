<script setup lang="ts">
import type { ISubscribeType } from '../services/api'

defineProps<{
  group: {
    name: string
    discription: string | null
    max_quality: number
    options: ISubscribeType[]
  }
  selectedOption: ISubscribeType | undefined
  currentSubId: number | null | undefined
  isProcessing: boolean
  hasActiveSub: boolean
}>()

const emit = defineEmits<{
  (e: 'update:selectedOption', option: ISubscribeType): void
  (e: 'action', planId: number): void
}>()

const formatDuration = (days: number) => {
  if (days === 30) return '1 мес.'
  if (days === 90) return '3 мес.'
  if (days === 180) return '6 мес.'
  if (days === 365) return '1 год'
  return `${days} дн.`
}
</script>

<template>
  <div
    class="card border-0 shadow-sm plan-card"
    :class="{
      'current-plan-border':
        currentSubId === selectedOption?.subscribe_type_id
    }"
  >
    <div class="card-body p-4 text-center d-flex flex-column h-100 justify-content-between">
      <div>
        <h3 class="fw-bold mb-3 mt-2" style="color: var(--text-darker);">{{ group.name }}</h3>
        <div class="price mb-4">
          <span class="display-4 fw-bold" style="color: var(--text-darker);">{{ selectedOption?.subscribe_type_cost || 0 }}</span>
          <span class="text-muted fw-bold"> ₽</span>
        </div>

        <div class="mb-4 text-start bg-light p-2 rounded-3 border">
          <label class="form-label smallest-label fw-bold text-secondary text-uppercase d-block mb-2">Длительность тарифа:</label>
          <div class="d-flex flex-wrap gap-2 justify-content-start">
            <button
              v-for="opt in group.options"
              :key="opt.subscribe_type_id"
              type="button"
              class="btn btn-sm duration-btn"
              :class="selectedOption?.subscribe_type_id === opt.subscribe_type_id ? 'active-duration' : 'inactive-duration'"
              @click="emit('update:selectedOption', opt)"
            >
              {{ formatDuration(opt.subscribe_type_duration) }}
            </button>
          </div>
        </div>

        <ul class="list-unstyled mb-4 text-start">
          <li class="mb-3 d-flex align-items-center">
            <i class="bi bi-check2-circle me-2 text-success fs-5"></i>
            <span>Доступ на <strong>{{ selectedOption?.subscribe_type_duration || 0 }} дней</strong></span>
          </li>
          <li class="mb-3 d-flex align-items-center">
            <i class="bi bi-check2-circle me-2 text-success fs-5"></i>
            <span>Качество видео до <strong>{{ group.max_quality }}p</strong></span>
          </li>
          <li class="text-muted small mt-2 ps-1 border-start lh-sm">{{ group.discription }}</li>
        </ul>
      </div>

      <button
        @click="selectedOption && emit('action', selectedOption.subscribe_type_id)"
        :disabled="
          isProcessing ||
          currentSubId === selectedOption?.subscribe_type_id
        "
        class="btn w-100 py-3 fw-bold purchase-btn mt-3"
        :class="
          currentSubId === selectedOption?.subscribe_type_id
            ? 'btn-secondary'
            : 'btn-primary'
        "
      >
        <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
        <span
          v-if="
            currentSubId === selectedOption?.subscribe_type_id
          "
          >Текущий тариф</span
        >
        <span v-else-if="hasActiveSub">Сменить тариф</span>
        <span v-else>Оформить подписку</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.plan-card {
  border-radius: 24px;
  transition: all 0.3s ease;
  background: var(--card-bg);
  border: 1px solid transparent;
  min-height: 580px;
}
.plan-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(139, 115, 85, 0.15) !important;
  border: 1px solid var(--sidebar-primary) !important;
}
.current-plan-border {
  border: 2px solid var(--sidebar-primary) !important;
}
.purchase-btn.btn-primary {
  background-color: var(--sidebar-primary);
  border: none;
  border-radius: 14px;
}
.purchase-btn.btn-secondary {
  border-radius: 14px;
  background-color: #6c757d;
  border: none;
}
.duration-btn {
  border-radius: 8px;
  font-weight: 600;
  padding: 5px 10px;
  transition: 0.2s ease;
  font-size: 0.8rem;
}
.active-duration {
  background-color: var(--sidebar-primary);
  color: white;
  border: 1px solid var(--sidebar-primary);
}
.inactive-duration {
  background-color: var(--card-bg);
  color: var(--text-dark);
  border: 1px solid var(--border-color);
}
.inactive-duration:hover {
  border-color: var(--sidebar-primary);
  color: var(--sidebar-primary);
}
.smallest-label {
  font-size: 0.7rem;
  letter-spacing: 0.5px;
}
</style>
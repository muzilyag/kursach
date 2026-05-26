<script setup lang="ts">
import { computed } from 'vue'
import CheckboxList from './CheckboxList.vue'

const props = withDefaults(
  defineProps<{
    label: string
    items: any[]
    modelValue: (number | string)[]
    valueKey: string
    labelKey: string
    emptyText?: string
  }>(),
  {
    emptyText: 'Список пуст'
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: (number | string)[]): void
}>()

const selectedCount = computed(() => props.modelValue.length)

const displayText = computed(() => {
  return selectedCount.value > 0
    ? `${props.label} (${selectedCount.value})`
    : `Выбрать ${props.label.toLowerCase()}`
})
</script>

<template>
  <div class="dropdown w-100">
    <button
      class="btn w-100 text-start dropdown-toggle d-flex justify-content-between align-items-center shadow-none"
      type="button"
      data-bs-toggle="dropdown"
      data-bs-auto-close="outside"
      style="
        background-color: var(--card-bg);
        color: var(--text-darker);
        border-radius: 10px;
        border: 1px solid var(--border-color);
      "
    >
      <span>{{ displayText }}</span>
    </button>
    <div
      class="dropdown-menu p-2 shadow-sm border mt-2"
      style="width: 280px; border-radius: 12px; background-color: var(--card-bg); border-color: var(--border-color);"
    >
      <CheckboxList
        :model-value="modelValue"
        @update:model-value="emit('update:modelValue', $event)"
        :items="items"
        :value-key="valueKey"
        :label-key="labelKey"
        :empty-text="emptyText"
        max-height="300px"
      />
    </div>
  </div>
</template>

<style scoped>
.dropdown-toggle::after {
  margin-left: auto;
}
</style>
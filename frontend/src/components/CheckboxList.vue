<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    items: any[]
    modelValue: (number | string)[]
    valueKey: string
    labelKey: string
    emptyText?: string
    maxHeight?: string
  }>(),
  {
    emptyText: 'Список пуст',
    maxHeight: '250px'
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: (number | string)[]): void
}>()

const updateSelection = (id: number | string, checked: boolean) => {
  const newValue = [...props.modelValue]
  if (checked) {
    if (!newValue.includes(id)) newValue.push(id)
  } else {
    const index = newValue.indexOf(id)
    if (index !== -1) newValue.splice(index, 1)
  }
  emit('update:modelValue', newValue)
}
</script>

<template>
  <div
    class="border rounded p-2 form-control checkbox-list-container custom-scrollbar"
    :style="{ maxHeight: maxHeight, backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)' }"
  >
    <div v-for="item in items" :key="item[valueKey]" class="form-check custom-check mb-1">
      <input
        class="form-check-input shadow-none"
        type="checkbox"
        :value="item[valueKey]"
        :id="`check-${item[valueKey]}`"
        :checked="modelValue.includes(item[valueKey])"
        @change="(e) => updateSelection(item[valueKey], (e.target as HTMLInputElement).checked)"
      />
      <label class="form-check-label small w-100" :for="`check-${item[valueKey]}`">
        {{ item[labelKey] }}
      </label>
    </div>
    <div v-if="items.length === 0" class="text-muted small italic p-1">
      {{ emptyText }}
    </div>
  </div>
</template>

<style scoped>
.checkbox-list-container {
  overflow-y: auto;
}
.custom-check .form-check-input:checked {
  background-color: var(--sidebar-primary);
  border-color: var(--sidebar-primary);
}
.custom-check .form-check-input:focus {
  border-color: var(--sidebar-primary);
  box-shadow: 0 0 0 0.25rem rgba(139, 115, 85, 0.25);
}
.custom-check .form-check-label {
  cursor: pointer;
  color: var(--text-darker);
  transition: color 0.2s;
}
.custom-check:hover .form-check-label {
  color: var(--sidebar-primary);
}
.italic {
  font-style: italic;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(139, 115, 85, 0.2);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--sidebar-primary);
}
</style>
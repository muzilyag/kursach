<template>
  <div class="table-responsive">
    <table class="table table-hover mb-0">
      <thead class="table-light">
        <tr>
          <th style="width: 50px">#</th>
          <th
            v-for="col in columns"
            :key="col.key"
            :class="{ sortable: col.sortable }"
            @click="() => { if (col.sortable) $emit('sort', col.key) }"
          >
            {{ col.label }}
            <i v-if="col.sortable" class="bi ms-1" :class="getSortIcon(col.key)"></i>
          </th>
          <th v-if="hasActions" class="text-end">Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="item.id || index">
          <td class="text-muted small">
            {{ (currentPage - 1) * pageSize + index + 1 }}
          </td>
          <td v-for="col in columns" :key="col.key">
            <slot :name="'cell-' + col.key" :item="item">
              {{ item[col.key] }}
            </slot>
          </td>
          <td v-if="hasActions" class="text-end">
            <slot name="actions" :item="item">
              <button class="btn btn-sm btn-outline-primary me-2" @click="$emit('edit', item)">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', item)">
                <i class="bi bi-trash"></i>
              </button>
            </slot>
          </td>
        </tr>
        <tr v-if="items.length === 0">
          <td :colspan="columns.length + (hasActions ? 2 : 1)" class="text-center py-4 text-muted">
            Данных не найдено
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
export type SortOrder = 'asc' | 'desc'

const props = withDefaults(
  defineProps<{
    columns: Array<{ key: string; label: string; sortable?: boolean }>
    items: any[]
    sortConfig?: { key: string; order: SortOrder }
    hasActions?: boolean
    currentPage?: number
    pageSize?: number
  }>(),
  {
    currentPage: 1,
    pageSize: 10,
    hasActions: false
  }
)

defineEmits(['sort', 'edit', 'delete'])

const getSortIcon = (key: string) => {
  if (!props.sortConfig || props.sortConfig.key !== key)
    return 'bi-arrow-down-up text-muted opacity-50'
  return props.sortConfig.order === 'asc'
    ? 'bi-arrow-up text-primary'
    : 'bi-arrow-down text-primary'
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}
.sortable:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
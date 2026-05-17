<script setup lang="ts">
import { computed } from 'vue'
import { Config } from '../config'

const props = defineProps<{
  currentPage: number;
  pages: number[];
  total: number;
}>()

defineEmits<{
  (e: 'update:page', page: number): void
}>()

const visiblePages = computed(() => {
  const totalPages = props.pages.length
  const maxPages = Config.pagination.maxPagesToShow

  if (totalPages <= maxPages + 2) {
    return props.pages
  }

  const current = props.currentPage
  const res: (number | string)[] = []
  const edgeCount = maxPages - 1

  if (current <= edgeCount - 1) {
    for (let i = 1; i <= edgeCount; i++) res.push(i)
    res.push('...')
    res.push(totalPages)
  } else if (current >= totalPages - (edgeCount - 2)) {
    res.push(1)
    res.push('...')
    for (let i = totalPages - edgeCount + 1; i <= totalPages; i++) res.push(i)
  } else {
    res.push(1)
    res.push('...')
    const middleSide = Math.floor((maxPages - 2) / 2)
    for (let i = current - middleSide; i <= current + middleSide; i++) {
      res.push(i)
    }
    res.push('...')
    res.push(totalPages)
  }

  return res
})
</script>

<template>
  <div class="d-flex justify-content-between align-items-center mt-3 p-3 border-top bg-white">
    <small class="text-muted fw-medium">Всего записей: {{ total }}</small>
    <nav v-if="pages.length > 1">
      <ul class="pagination pagination-sm m-0 shadow-sm">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="$emit('update:page', currentPage - 1)">«</button>
        </li>
        <li v-for="(p, index) in visiblePages" :key="index" class="page-item" :class="{ active: p === currentPage, disabled: p === '...' }">
          <span v-if="p === '...'" class="page-link">...</span>
          <button v-else class="page-link" @click="$emit('update:page', p as number)">{{ p }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === pages[pages.length - 1] }">
          <button class="page-link" @click="$emit('update:page', currentPage + 1)">»</button>
        </li>
      </ul>
    </nav>
  </div>
</template>
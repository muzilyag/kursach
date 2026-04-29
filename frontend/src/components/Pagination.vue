<script setup lang="ts">
defineProps<{
  currentPage: number;
  pages: number[];
  total: number;
}>()

defineEmits<{
  (e: 'update:page', page: number): void
}>()
</script>

<template>
  <div class="d-flex justify-content-between align-items-center mt-3 p-3 border-top bg-white">
    <small class="text-muted fw-medium">Всего записей: {{ total }}</small>
    <nav v-if="pages.length > 1">
      <ul class="pagination pagination-sm m-0 shadow-sm">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="$emit('update:page', currentPage - 1)">«</button>
        </li>
        <li v-for="p in pages" :key="p" class="page-item" :class="{ active: p === currentPage }">
          <button class="page-link" @click="$emit('update:page', p)">{{ p }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === pages[pages.length - 1] }">
          <button class="page-link" @click="$emit('update:page', currentPage + 1)">»</button>
        </li>
      </ul>
    </nav>
  </div>
</template>
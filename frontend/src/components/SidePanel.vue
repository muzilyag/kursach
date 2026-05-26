<script setup lang="ts">
defineProps<{
  isOpen: boolean
  title: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <div v-if="isOpen" class="panel-overlay" @click="emit('close')"></div>
  <div class="side-panel" :class="{ open: isOpen }">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold">{{ title }}</h5>
      <button type="button" class="btn-close shadow-none" @click="emit('close')"></button>
    </div>
    <slot></slot>
  </div>
</template>

<style scoped>
.panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  z-index: 1040;
}

.side-panel {
  position: fixed;
  top: 0;
  right: -450px;
  width: 450px;
  height: 100vh;
  background: var(--card-bg, #fff);
  z-index: 1050;
  transition: right 0.3s cubic-bezier(0.82, 0.085, 0.395, 0.895);
  box-shadow: -5px 0 25px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
}

.side-panel.open {
  right: 0;
}
</style>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    title: string
    value: string | number
    icon: string
    iconColor?: string
    iconBgColor?: string
    size?: 'md' | 'lg'
  }>(),
  {
    iconColor: 'var(--text-darker)',
    iconBgColor: 'var(--light-bg)',
    size: 'lg'
  }
)
</script>

<template>
  <div class="card border-0 shadow-sm h-100 p-3 stat-card" style="background-color: var(--card-bg)">
    <div class="d-flex align-items-center">
      <div
        class="badge me-3"
        :class="size === 'lg' ? 'p-3' : 'p-2'"
        :style="{ backgroundColor: iconBgColor, color: iconColor }"
      >
        <i :class="[icon, size === 'lg' ? 'fs-4' : 'fs-5']"></i>
      </div>
      <div>
        <h6 class="text-muted fw-bold" :class="size === 'lg' ? 'small mb-1' : 'small mb-0'">
          {{ title }}
        </h6>
        <component
          :is="size === 'lg' ? 'h3' : 'h4'"
          class="fw-bold m-0"
          :class="{ 'mt-1': size === 'md' }"
          style="color: var(--text-darker)"
        >
          {{ value }}
        </component>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(139, 115, 85, 0.1) !important;
}
</style>
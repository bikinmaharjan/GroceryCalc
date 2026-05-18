<template>
  <div v-if="show" :class="['fixed bottom-4 right-4 p-4 rounded-lg shadow-lg border text-white', type === 'success' ? 'bg-emerald-600 border-emerald-700' : 'bg-red-600 border-red-700']">
    {{ message }}
  </div>
</template>

<script setup lang="ts">
defineProps<{ show: boolean; message: string; type: 'success' | 'error' }>()
</script>

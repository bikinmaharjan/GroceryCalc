<template>
  <button :class="[
    'px-4 py-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1',
    variant === 'primary' 
      ? 'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500' 
      : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 focus:ring-slate-400'
  ]">
    <slot />
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ variant?: 'primary' | 'secondary' }>(), { variant: 'primary' })
</script>

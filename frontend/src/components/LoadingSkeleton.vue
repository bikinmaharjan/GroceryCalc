<template>
  <div class="animate-pulse flex flex-col gap-4 w-full">
    <slot>
      <div class="h-8 bg-slate-200 rounded-md w-1/3"></div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-24 bg-slate-200 rounded-xl"></div>
      </div>
      <div class="h-64 bg-slate-200 rounded-xl"></div>
    </slot>
  </div>
</template>

<script setup lang="ts">
</script>

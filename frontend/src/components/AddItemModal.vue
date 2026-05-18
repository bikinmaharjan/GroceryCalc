<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <BaseCard class="w-full max-w-md">
      <h3 class="text-xl font-bold mb-4">Add Expense</h3>
      <form @submit.prevent="$emit('submit', formData)" class="space-y-4">
        <input v-model="formData.description" placeholder="Description" class="w-full p-2 border rounded" required />
        <input v-model.number="formData.cost" type="number" step="0.01" placeholder="Cost" class="w-full p-2 border rounded" required />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click.prevent="$emit('close')">Cancel</BaseButton>
          <BaseButton type="submit">Add</BaseButton>
        </div>
      </form>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseCard from './BaseCard.vue'
import BaseButton from './BaseButton.vue'
defineEmits(['submit', 'close'])
const formData = ref({ description: '', cost: 0 })
</script>

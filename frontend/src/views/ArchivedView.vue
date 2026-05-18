<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold">Archived Lists</h1>
    <div v-for="list in lists" :key="list.id">
      {{ list.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useSelectedGroup } from '../composables/useSelectedGroup';

const { selectedGroup } = useSelectedGroup();
const lists = ref<any[]>([]);

onMounted(async () => {
  if (selectedGroup.value) {
    const res = await axios.get(`/api/lists/archived?group_id=${selectedGroup.value.id}`);
    lists.value = res.data;
  }
});
</script>

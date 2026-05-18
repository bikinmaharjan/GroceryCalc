<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold">Analytics</h1>
    <div v-if="analytics">
      <div v-for="cat in analytics.category_totals" :key="cat.category">
        {{ cat.category }}: {{ cat.total }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useSelectedGroup } from '../composables/useSelectedGroup';

const { selectedGroup } = useSelectedGroup();
const analytics = ref<any>(null);

onMounted(async () => {
  if (selectedGroup.value) {
    const res = await axios.get(`/api/analytics?group_id=${selectedGroup.value.id}`);
    analytics.value = res.data;
  }
});
</script>

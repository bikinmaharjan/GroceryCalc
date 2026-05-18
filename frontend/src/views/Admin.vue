<template>
  <AdminLayout>
    <div v-if="$route.path === '/admin'">
      <h2 class="text-2xl font-bold text-slate-800 mb-6">Dashboard</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <BaseCard class="bg-gradient-to-br from-emerald-50 to-white">
          <h3 class="text-slate-500 text-sm font-medium uppercase tracking-wider">Total Users</h3>
          <p class="text-4xl font-bold text-slate-900 mt-2">{{ stats.users }}</p>
        </BaseCard>
        <BaseCard class="bg-gradient-to-br from-blue-50 to-white">
          <h3 class="text-slate-500 text-sm font-medium uppercase tracking-wider">Total Groups</h3>
          <p class="text-4xl font-bold text-slate-900 mt-2">{{ stats.groups }}</p>
        </BaseCard>
      </div>

      <BaseCard>
        <h3 class="font-bold text-lg text-slate-800 mb-4">Recent Activity</h3>
        <div class="text-slate-500 text-sm italic">No recent activity recorded.</div>
      </BaseCard>
    </div>
    <RouterView />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '../api/axios'
import AdminLayout from '../components/AdminLayout.vue'
import BaseCard from '../components/BaseCard.vue'
import { useRoute } from 'vue-router'

const stats = ref({ users: 0, groups: 0 })
const route = useRoute()

onMounted(async () => {
  if (route.path === '/admin') {
    try {
        const [usersRes, groupsRes] = await Promise.all([
          apiClient.get('/admin/stats/users'),
          apiClient.get('/admin/stats/groups')
        ])
      stats.value = { users: usersRes.data.count, groups: groupsRes.data.count }
    } catch (e) {
      console.error('Failed to load stats', e)
    }
  }
})
</script>

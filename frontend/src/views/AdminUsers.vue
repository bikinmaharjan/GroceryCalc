<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

interface User { id: number; username: string; display_name: string; is_admin: boolean }

const users = ref<User[]>([])
const auth = useAuthStore()
const newUser = ref({ username: '', display_name: '' })

const loadUsers = async () => {
  const res = await axios.get<User[]>('http://localhost:8080/api/admin/users', {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  users.value = res.data
}

onMounted(loadUsers)

const saveUser = async () => {
  await axios.post('http://localhost:8080/api/admin/users', newUser.value, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  newUser.value = { username: '', display_name: '' }
  loadUsers()
}

const resetPassword = async (userId: number) => {
  if (confirm('Are you sure you want to reset this user\'s password?')) {
    await axios.post(`http://localhost:8080/api/admin/users/${userId}/reset-password`, null, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    alert('Password reset to password123')
  }
}
</script>

<template>
    <div class="mb-8 p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <h2 class="text-xl font-bold text-slate-800 mb-4">Create User</h2>
      <div class="flex gap-4">
        <input v-model="newUser.username" placeholder="Username" class="p-2 border rounded flex-1" />
        <input v-model="newUser.display_name" placeholder="Display Name" class="p-2 border rounded flex-1" />
        <BaseButton @click="saveUser">Create</BaseButton>
      </div>
    </div>
    
    <BaseCard>
      <h2 class="text-xl font-bold text-slate-800 mb-4">Users</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-slate-500 border-b border-slate-200">
              <th class="p-4 font-medium">Username</th>
              <th class="p-4 font-medium">Display Name</th>
              <th class="p-4 font-medium">Admin</th>
              <th class="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50 transition-colors">
              <td class="p-4 font-medium text-slate-800">{{ u.username }}</td>
              <td class="p-4 text-slate-600">{{ u.display_name }}</td>
              <td class="p-4">
                <span :class="u.is_admin ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'" 
                      class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                      {{ u.is_admin ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="p-4 text-right">
                <BaseButton variant="secondary" class="text-sm" @click="resetPassword(u.id)">Reset Pwd</BaseButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>
</template>


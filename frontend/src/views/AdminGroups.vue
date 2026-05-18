<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import AdminLayout from '../components/AdminLayout.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

interface User { id: number; username: string }
interface Group { id: number; name: string }

const groups = ref<Group[]>([])
const allUsers = ref<User[]>([])
const groupMembers = ref<Record<number, User[]>>({})
const auth = useAuthStore()

const editingGroup = ref<Group | null>(null)
const editForm = ref({ name: '', user_ids: [] as number[] })
const newGroupName = ref('')

const loadData = async () => {
  const [gRes, uRes] = await Promise.all([
    axios.get<Group[]>('http://localhost:8080/api/admin/groups', { headers: { Authorization: `Bearer ${auth.token}` } }),
    axios.get<User[]>('http://localhost:8080/api/admin/users', { headers: { Authorization: `Bearer ${auth.token}` } })
  ])
  groups.value = gRes.data
  allUsers.value = uRes.data
  
  for (const group of groups.value) {
      const res = await axios.get(`http://localhost:8080/api/admin/groups/${group.id}/members`, {
        headers: { Authorization: `Bearer ${auth.token}` }
      })
      groupMembers.value[group.id] = res.data
  }
}

onMounted(loadData)

const getMemberNames = (groupId: number) => {
    const members = groupMembers.value[groupId] || []
    // Use user_id to find username from allUsers
    return members.map(m => allUsers.value.find(u => u.id === m.user_id)?.username).filter(Boolean).join(', ')
}

// In the loadData function, the groupMembers fetch:
// Change: 
// res.data.map(m => m.user_id)
// To verify the structure of res.data. 
// Assuming AdminGroups.vue imports:
// interface User { id: number; username: string }
// interface Group { id: number; name: string }
// interface Member { user_id: number }

const startEdit = async (group: Group) => {
  editingGroup.value = group
  const res = await axios.get<{user_id: number}[]>(`http://localhost:8080/api/admin/groups/${group.id}/members`, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  editForm.value = { 
    name: group.name, 
    user_ids: res.data.map(m => m.user_id)
  } 
}

const saveGroup = async () => {
  if (!editingGroup.value) return
  await axios.put(`http://localhost:8080/api/admin/groups/${editingGroup.value.id}`, {
      name: editForm.value.name,
      user_ids: editForm.value.user_ids
  }, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  editingGroup.value = null
  loadData()
}

const createGroup = async () => {
    await axios.post('http://localhost:8080/api/admin/groups', null, {
        params: { name: newGroupName.value },
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    newGroupName.value = ''
    loadData()
}
</script>


<template>
  <AdminLayout>
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-slate-800 mb-4">Create Group</h2>
        <div class="flex gap-2">
            <input v-model="newGroupName" placeholder="New group name" class="p-2 border rounded flex-1" />
            <BaseButton @click="createGroup">Create</BaseButton>
        </div>
      </div>
      
      <h2 class="text-2xl font-bold text-slate-800 mb-4">Manage Groups</h2>
      <BaseCard>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-slate-500 border-b border-slate-200">
                <th class="p-4">Name</th>
                <th class="p-4">Members</th>
                <th class="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <template v-for="g in groups" :key="g.id">
                <tr v-if="editingGroup?.id !== g.id" class="hover:bg-slate-50">
                  <td class="p-4 font-medium">{{ g.name }}</td>
                  <td class="p-4 text-sm text-slate-600">
                      {{ getMemberNames(g.id) }}
                  </td>
                  <td class="p-4 text-right">
                    <BaseButton variant="secondary" class="text-sm" @click="startEdit(g)">Edit</BaseButton>
                  </td>
                </tr>
                <tr v-else class="bg-slate-50">
                  <td class="p-4">
                    <input v-model="editForm.name" class="p-1 border rounded w-full" />
                  </td>
                  <td class="p-4">
                      <div v-for="user in allUsers" :key="user.id" class="text-sm">
                          <input type="checkbox" :value="user.id" v-model="editForm.user_ids" /> {{ user.username }}
                      </div>
                  </td>
                  <td class="p-4 text-right">
                    <BaseButton variant="primary" class="text-sm mr-2" @click="saveGroup">Save</BaseButton>
                    <BaseButton variant="secondary" class="text-sm" @click="editingGroup = null">Cancel</BaseButton>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </BaseCard>
  </AdminLayout>
</template>


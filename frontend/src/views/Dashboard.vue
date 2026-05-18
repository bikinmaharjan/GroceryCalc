<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'
import ToastNotification from '../components/ToastNotification.vue'
import { 
  Edit2, 
  Trash2, 
  ShoppingBag, 
  Users, 
  DollarSign, 
  TrendingUp, 
  ArrowRight,
  PieChart,
  BarChart3,
  Calendar
} from '@lucide/vue'
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  ArcElement 
} from 'chart.js'
import { Bar, Line, Pie } from 'vue-chartjs'

ChartJS.register(
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  ArcElement
)

interface Item { id: number; description: string; cost: number; created_at: string }
interface List { id: number; name: string; is_settling?: boolean; status?: string }
interface Group { id: number; name: string }

const items = ref<Item[]>([])
const activeList = ref<List | null>(null)
const historyLists = ref<List[]>([])
const groups = ref<Group[]>([])
const selectedGroup = ref<Group | null>(null)
const stats = ref({ total_cost: 0, item_count: 0, share_per_user: 0 })
const analytics = ref<any>(null)
const settlementDetails = ref<any>({ settlements: [], transactions: [], member_count: 0 })

const userChartData = computed(() => {
    if (!analytics.value?.user_totals) return null
    return {
        labels: analytics.value.user_totals.map((u: any) => u.user),
        datasets: [{
            label: 'Total Spent ($)',
            backgroundColor: '#10b981',
            data: analytics.value.user_totals.map((u: any) => u.total)
        }]
    }
})

const categoryChartData = computed(() => {
    if (!analytics.value?.category_totals) return null
    return {
        labels: analytics.value.category_totals.map((c: any) => c.category),
        datasets: [{
            backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#64748b'],
            data: analytics.value.category_totals.map((c: any) => c.total)
        }]
    }
})

const trendChartData = computed(() => {
    if (!analytics.value?.monthly_trend) return null
    return {
        labels: analytics.value.monthly_trend.map((t: any) => t.month),
        datasets: [{
            label: 'Spending ($)',
            borderColor: '#10b981',
            backgroundColor: '#10b981',
            data: analytics.value.monthly_trend.map((t: any) => t.total),
            tension: 0.3
        }]
    }
})

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const activeTab = ref('items')
const newListName = ref('')
const editingListName = ref('')
const isRenaming = ref(false)

watch(() => route.path, (newPath) => {
    if (newPath.includes('settlements')) activeTab.value = 'settlements'
    else if (newPath.includes('history')) activeTab.value = 'history'
    else if (newPath.includes('analytics')) activeTab.value = 'analytics'
    else activeTab.value = 'items'
}, { immediate: true })

const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' })
const categories = ref(['grocery', 'electricity bills', 'internet bill', 'gas bill'])
const newItem = ref({ description: '', cost: 0, category: 'grocery' })
const editingItem = ref<Item | null>(null)

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    toast.value = { show: true, message, type }
    setTimeout(() => { toast.value.show = false }, 3000)
}

const loadData = async () => {
  try {
    const groupsRes = await axios.get<Group[]>('http://localhost:8080/api/my-groups', {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    groups.value = groupsRes.data
    if (groups.value.length > 0) {
        selectedGroup.value = groups.value[0]
        await loadListAndData()
    }
  } catch (e) {
    console.error(e)
  }
}

const loadSettlementDetails = async () => {
    if (!activeList.value) return
    const res = await axios.get(`http://localhost:8080/api/lists/${activeList.value.id}/settlements/details`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    settlementDetails.value = res.data
}

const loadHistory = async () => {
    if (!selectedGroup.value) return
    const res = await axios.get<List[]>(`http://localhost:8080/api/lists/archived?group_id=${selectedGroup.value.id}`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    historyLists.value = res.data
}

const loadListAndData = async () => {
    if (!selectedGroup.value) return
    const listRes = await axios.get<List[]>(`http://localhost:8080/api/lists/active?group_id=${selectedGroup.value.id}`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    if (listRes.data.length > 0) {
        activeList.value = listRes.data[0]
        await Promise.all([loadItems(), loadStats(), loadSettlementDetails(), loadHistory(), loadAnalytics()])
    } else {
        activeList.value = null
        items.value = []
        settlementDetails.value = { settlements: [], transactions: [], member_count: 0 }
        await Promise.all([loadHistory(), loadAnalytics()])
    }
}

const loadAnalytics = async () => {
    if (!selectedGroup.value) return
    try {
        const res = await axios.get(`http://localhost:8080/api/analytics?group_id=${selectedGroup.value.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        analytics.value = res.data
    } catch (e) {
        console.error('Failed to load analytics', e)
    }
}

const loadItems = async () => {
  if (!activeList.value) return
  const res = await axios.get<Item[]>(`http://localhost:8080/api/items?list_id=${activeList.value.id}`, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  items.value = res.data
}

const loadStats = async () => {
    if (!activeList.value) return
    const res = await axios.get(`http://localhost:8080/api/lists/${activeList.value.id}/settlements/calculate`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    stats.value = res.data
}

const addItem = async () => {
  if (!activeList.value) return
  
  const cat = newItem.value.category.trim()
  if (cat && !categories.value.includes(cat)) {
    categories.value.push(cat)
  }

  await axios.post(`http://localhost:8080/api/items?list_id=${activeList.value.id}&description=${newItem.value.description}&cost=${newItem.value.cost}&category=${cat}`, null, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  newItem.value = { description: '', cost: 0, category: 'grocery' }
  await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
}

const handleCategoryChange = () => {
    if (newItem.value.category === 'ADD_NEW') {
        const newCat = prompt('Enter new category:')
        if (newCat && newCat.trim()) {
            const cat = newCat.trim()
            if (!categories.value.includes(cat)) {
                categories.value.push(cat)
            }
            newItem.value.category = cat
        } else {
            newItem.value.category = 'grocery'
        }
    }
}

const startEdit = (item: Item) => { editingItem.value = { ...item } }

const saveItem = async () => {
    if (!editingItem.value) return
    await axios.put(`http://localhost:8080/api/items/${editingItem.value.id}`, editingItem.value, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    editingItem.value = null
    await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
}

const deleteItem = async (id: number) => {
    if (confirm('Delete this item?')) {
        await axios.delete(`http://localhost:8080/api/items/${id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
    }
}

const markPaid = async (t: any) => {
    if (!confirm(`Confirm payment of $${t.amount.toFixed(2)} to ${t.to}?`)) return
    try {
        await axios.post(`http://localhost:8080/api/lists/${activeList.value?.id}/settlements/mark-paid`, {
            from_username: t.from,
            to_username: t.to,
            amount: t.amount
        }, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('Payment marked as paid!')
        await loadSettlementDetails()
    } catch (e) {
        showToast('Failed to mark paid', 'error')
    }
}

const startSettlement = async () => {
    if (!activeList.value) return
    try {
        await axios.post(`http://localhost:8080/api/lists/${activeList.value.id}/settle`, null, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        activeList.value.is_settling = true
        showToast('Settlement started. Items are now locked.')
    } catch (e) {
        showToast('Failed to start settlement', 'error')
    }
}

const archiveList = async () => {
    if (!activeList.value) return
    if (!confirm('Archive this list? This will move it to history.')) return
    try {
        await axios.post(`http://localhost:8080/api/lists/${activeList.value.id}/archive`, null, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('List archived successfully!')
        await loadListAndData()
    } catch (e) {
        showToast('Failed to archive list', 'error')
    }
}

const createList = async () => {
    if (!selectedGroup.value) return
    try {
        await axios.post(`http://localhost:8080/api/lists?group_id=${selectedGroup.value.id}&name=${newListName.value}`, null, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('List created successfully!')
        newListName.value = ''
        await loadListAndData()
    } catch (e) {
        showToast('Failed to create list', 'error')
    }
}

const renameList = async () => {
    if (!activeList.value) return
    try {
        await axios.put(`http://localhost:8080/api/lists/${activeList.value.id}?name=${editingListName.value}`, null, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('List renamed successfully!')
        activeList.value.name = editingListName.value
        isRenaming.value = false
    } catch (e) {
        showToast('Failed to rename list', 'error')
    }
}

onMounted(loadData)
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="bg-white shadow-sm p-4 flex justify-between items-center">
      <div class="flex items-center gap-4">
        <span class="font-bold text-xl text-emerald-700">GrocerySplit</span>
        <select v-model="selectedGroup" @change="loadListAndData" class="p-1 border rounded text-sm">
            <option v-for="g in groups" :key="g.id" :value="g">{{ g.name }}</option>
        </select>
      </div>
       <div class="flex gap-4 items-center">
           <RouterLink to="/dashboard/items" :class="{'text-emerald-600 font-medium': activeTab === 'items'}">Items</RouterLink>
           <RouterLink to="/dashboard/settlements" :class="{'text-emerald-600 font-medium': activeTab === 'settlements'}">Settlements</RouterLink>
           <RouterLink to="/dashboard/history" :class="{'text-emerald-600 font-medium': activeTab === 'history'}">History</RouterLink>
           <RouterLink to="/dashboard/analytics" :class="{'text-emerald-600 font-medium': activeTab === 'analytics'}">Analytics</RouterLink>
          <button @click="handleLogout" class="text-slate-600 hover:text-red-600 text-sm ml-4">Logout</button>
       </div>
    </nav>
    <main class="p-6 max-w-5xl mx-auto">
       <ToastNotification :show="toast.show" :message="toast.message" :type="toast.type" />
      
       <div v-if="!activeList" class="text-center mt-10">
         <p class="text-slate-600 mb-4">No active grocery list found.</p>
         <div class="flex justify-center gap-2">
             <input v-model="newListName" placeholder="List name (optional)" class="p-2 border rounded w-64" />
             <BaseButton @click="createList">Create List</BaseButton>
         </div>
       </div>
       
       <div v-else>
         <!-- Items Tab -->
         <div v-if="activeTab === 'items'">
              <!-- Current List Summary -->
              <div class="mb-8">
<div class="flex justify-between items-center mb-6 pb-4 border-b border-slate-200">
                   <div class="flex items-center gap-3">
                     <div class="p-2 bg-emerald-100 rounded-lg text-emerald-700">
                       <ShoppingBag class="w-6 h-6" />
                     </div>
                     <h2 class="font-extrabold text-3xl text-slate-900 tracking-tight">
                       <span v-if="!isRenaming">{{ activeList.name }}</span>
                       <input v-else v-model="editingListName" class="p-1 border rounded text-2xl font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none" />
                     </h2>
                   </div>
                   <div class="flex gap-2">
                     <BaseButton v-if="!isRenaming" variant="secondary" class="text-xs" @click="isRenaming = true; editingListName = activeList.name">Rename</BaseButton>
                     <BaseButton v-if="isRenaming" variant="primary" class="text-xs" @click="renameList">Save</BaseButton>
                     <BaseButton v-if="isRenaming" variant="secondary" class="text-xs" @click="isRenaming = false">Cancel</BaseButton>
                   </div>
                 </div>

                <BaseCard class="grid grid-cols-1 md:grid-cols-4 gap-6">
                   <div>
                       <h3 class="text-slate-500 text-sm">List Total</h3>
                       <p class="text-2xl font-bold">${{ stats.total_cost.toFixed(2) }}</p>
                   </div>
                   <div>
                       <h3 class="text-slate-500 text-sm">Items</h3>
                       <p class="text-2xl font-bold">{{ stats.item_count }}</p>
                   </div>
                   <div>
                       <h3 class="text-slate-500 text-sm">Members</h3>
                       <p class="text-2xl font-bold">{{ settlementDetails.member_count }}</p>
                   </div>
                   <div>
                       <h3 class="text-slate-500 text-sm">Share per User</h3>
                       <p class="text-2xl font-bold text-emerald-600">${{ stats.share_per_user.toFixed(2) }}</p>
                   </div>
               </BaseCard>
             </div>

<div v-if="!activeList?.is_settling" class="mb-8 p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
                 <h3 class="font-bold text-lg text-slate-800 mb-4">Add Item</h3>
                 <div class="flex flex-wrap gap-4">
                     <input v-model="newItem.description" placeholder="Description" class="p-2 border rounded flex-1 min-w-[200px]" />
                     <input v-model.number="newItem.cost" type="number" step="0.01" placeholder="Cost" class="p-2 border rounded w-32" />
                     <div class="flex gap-2">
                       <select v-model="newItem.category" @change="handleCategoryChange" class="p-2 border rounded w-40">
                         <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                         <option value="ADD_NEW">+ Add New...</option>
                       </select>
                     </div>
                     <BaseButton @click="addItem">Add</BaseButton>
                 </div>
             </div>

            <div v-else class="mb-8 p-6 bg-amber-50 rounded-xl border border-amber-200 text-amber-800 text-center">
                <p class="font-medium">Settlement in progress. Adding new items is disabled.</p>
            </div>
            <BaseCard>
              <h2 class="font-bold text-lg text-slate-800 mb-4">Items</h2>
              <div class="overflow-x-auto">
<table class="w-full text-left">
                      <thead>
                        <tr class="text-slate-500 border-b border-slate-200">
                          <th class="p-4">Description</th>
                          <th class="p-4">Category</th>
                          <th class="p-4">Cost</th>
                          <th class="p-4">Date</th>
                          <th class="p-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-100">
                        <template v-for="item in items" :key="item.id">
                            <tr v-if="editingItem?.id !== item.id" class="hover:bg-slate-50">
                              <td class="p-4">{{ item.description }}</td>
                              <td class="p-4"><span class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">{{ item.category || 'grocery' }}</span></td>
                              <td class="p-4">${{ item.cost.toFixed(2) }}</td>
                              <td class="p-4">{{ new Date(item.created_at).toLocaleDateString() }}</td>
                              <td class="p-4 text-right">
                                <div class="flex justify-end gap-2">
                                  <button v-if="!activeList?.is_settling" 
                                    class="p-2 h-8 w-8 flex items-center justify-center rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-all shadow-sm" 
                                    @click="startEdit(item)">
                                    <Edit2 class="w-4 h-4" />
                                  </button>
                                  <button v-if="!activeList?.is_settling" 
                                    class="p-2 h-8 w-8 flex items-center justify-center rounded-lg bg-red-500 text-white hover:bg-red-600 transition-all shadow-sm" 
                                    @click="deleteItem(item.id)">
                                    <Trash2 class="w-4 h-4" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                            <tr v-else class="bg-slate-50">
                                <td class="p-4"><input v-model="editingItem.description" class="p-1 border rounded w-full" /></td>
                                <td class="p-4"><input v-model="editingItem.category" class="p-1 border rounded w-full" /></td>
                                <td class="p-4"><input v-model.number="editingItem.cost" type="number" class="p-1 border rounded w-20" /></td>
                                <td class="p-4">...</td>
                                <td class="p-4 text-right">
                                    <BaseButton variant="primary" class="text-xs mr-2" @click="saveItem">Save</BaseButton>
                                    <BaseButton variant="secondary" class="text-xs" @click="editingItem = null">Cancel</BaseButton>
                                </td>
                            </tr>
                        </template>
                        <tr v-if="items.length === 0">
                            <td colspan="5" class="p-4 text-center text-slate-400 italic">No items added yet.</td>
                        </tr>
                      </tbody>
                    </table>

              </div>
            </BaseCard>
        </div>

        <!-- Settlements Tab -->
        <div v-if="activeTab === 'settlements'" class="space-y-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="font-bold text-2xl text-slate-800">Settlement</h2>
                <div class="flex gap-3">
                    <BaseButton v-if="!activeList?.is_settling" @click="startSettlement" variant="primary">Start Settlement</BaseButton>
                    <BaseButton v-if="activeList?.is_settling" @click="archiveList" variant="secondary">Archive List</BaseButton>
                </div>
            </div>
            <BaseCard class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                    <h3 class="text-slate-500 text-sm">Group Total Spent</h3>
                    <p class="text-2xl font-bold">${{ stats.total_cost.toFixed(2) }}</p>
                </div>
                <div>
                    <h3 class="text-slate-500 text-sm">Total Items</h3>
                    <p class="text-2xl font-bold">{{ stats.item_count }}</p>
                </div>
                <div>
                    <h3 class="text-slate-500 text-sm">Members</h3>
                    <p class="text-2xl font-bold">{{ settlementDetails.member_count }}</p>
                </div>
                <div>
                    <h3 class="text-slate-500 text-sm">Share per User</h3>
                    <p class="text-2xl font-bold text-emerald-600">${{ stats.share_per_user.toFixed(2) }}</p>
                </div>
            </BaseCard>
            
            <BaseCard>
                <h3 class="font-bold text-lg mb-4">Who owes who?</h3>
                <ul class="space-y-2">
                    <li v-for="t in settlementDetails.transactions" :key="t.from" class="bg-slate-100 p-3 rounded flex justify-between items-center">
                        <span class="flex items-center gap-2">
                          <span class="font-bold">{{ t.from_name }}</span> 
                          <ArrowRight class="w-4 h-4 text-slate-400" /> 
                          <span class="font-bold">{{ t.to_name }}</span> 
                          <span class="ml-2 text-slate-600">${{ t.amount.toFixed(2) }}</span>
                        </span>
                        <div class="flex items-center gap-2">
                            <template v-if="t.status === 'paid'">
                                <span class="text-emerald-600 text-xs font-medium uppercase">Paid</span>
                            </template>
                            <template v-else>
                                <span v-if="t.to === auth.user?.username" class="text-amber-600 text-xs font-medium uppercase">
                                    Pending
                                </span>
                                <BaseButton v-if="t.from === auth.user?.username" @click="markPaid(t)" class="text-xs">Mark Paid</BaseButton>
                            </template>
                        </div>
                    </li>
                    <li v-if="settlementDetails.transactions.length === 0" class="text-slate-500 italic">All debts settled.</li>
                </ul>
            </BaseCard>
            
            <BaseCard v-for="s in settlementDetails.settlements" :key="s.user">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-lg">{{ s.user }}</h3>
                    <span :class="s.balance >= 0 ? 'text-emerald-600' : 'text-red-600'" class="font-bold">
                        {{ s.balance >= 0 ? 'Owed: ' : 'Owes: ' }} ${{ Math.abs(s.balance).toFixed(2) }}
                    </span>
                </div>
                <p class="text-sm text-slate-500 mb-2">Paid: ${{ s.total_paid.toFixed(2) }}</p>
                <ul class="text-sm text-slate-600 list-disc ml-4">
                    <li v-for="item in s.items" :key="item.description">
                        {{ item.description }}: ${{ item.cost.toFixed(2) }}
                    </li>
                </ul>
            </BaseCard>
        </div>

         <!-- History Tab -->
         <div v-if="activeTab === 'history'" class="space-y-6">
             <h2 class="font-bold text-2xl text-slate-800 mb-4">Archived Lists</h2>
             <div v-if="historyLists.length === 0" class="text-center p-10 bg-white rounded-xl border border-slate-200 text-slate-500">
                 No archived lists found for this group.
             </div>
             <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <BaseCard v-for="list in historyLists" :key="list.id" class="flex flex-col h-full">
                     <div class="flex justify-between items-start mb-4">
                         <div>
                             <h3 class="font-bold text-lg">{{ list.archived_at ? new Date(list.archived_at).toLocaleDateString() : 'Unknown Date' }}</h3>
                             <p class="text-xs text-slate-500">{{ list.name }}</p>
                         </div>
                         <div class="text-right">
                             <p class="text-sm text-slate-500">Total</p>
                             <p class="font-bold text-emerald-600">${{ list.total_cost.toFixed(2) }}</p>
                         </div>
                     </div>
                     <div class="border-t pt-3 mb-4">
                         <div class="flex justify-between items-center mb-2">
                             <p class="text-xs font-medium text-slate-400 uppercase">Share per Person</p>
                             <p class="text-xs font-bold text-slate-700">${{ list.share_per_user.toFixed(2) }}</p>
                         </div>
                         <div class="space-y-1">
                             <div v-for="p in list.user_payments" :key="p.user" class="flex justify-between text-sm">
                                 <span class="text-slate-600">{{ p.user }}</span>
                                 <span class="font-medium">${{ p.paid.toFixed(2) }}</span>
                             </div>
                             <div v-if="list.user_payments.length === 0" class="text-xs text-slate-400 italic">
                                 No payment data available.
                             </div>
                         </div>
                     </div>
                     <div class="border-t pt-3">
                         <p class="text-xs font-medium text-slate-400 uppercase mb-2">Final Settlements</p>
                         <div class="space-y-1">
                             <div v-for="t in list.transactions" :key="t.from + t.to" class="flex justify-between text-sm">
                                 <span class="text-slate-600">{{ t.from }} <span class="text-emerald-500 mx-1">→</span> {{ t.to }}</span>
                                 <span class="font-medium">${{ t.amount.toFixed(2) }}</span>
                             </div>
                             <div v-if="list.transactions.length === 0" class="text-xs text-slate-400 italic">
                                 No debts were recorded.
                             </div>
                         </div>
                     </div>
                 </BaseCard>
             </div>
         </div>

          <!-- Analytics Tab -->
          <div v-if="activeTab === 'analytics'" class="space-y-6">
               <!-- Current List Summary -->
               <div class="mb-8">
                 <div class="flex justify-between items-center mb-6 pb-4 border-b border-slate-200">
                   <div class="flex items-center gap-3">
                     <div class="p-2 bg-emerald-100 rounded-lg text-emerald-700">
                       <ShoppingBag class="w-6 h-6" />
                     </div>
                     <h2 class="font-extrabold text-3xl text-slate-900 tracking-tight">
                       <span v-if="!isRenaming">{{ activeList.name }}</span>
                       <input v-else v-model="editingListName" class="p-1 border rounded text-2xl font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500 outline-none" />
                     </h2>
                   </div>
                   <div class="flex gap-2">
                     <BaseButton v-if="!isRenaming" variant="secondary" class="text-xs" @click="isRenaming = true; editingListName = activeList.name">Rename</BaseButton>
                     <BaseButton v-if="isRenaming" variant="primary" class="text-xs" @click="renameList">Save</BaseButton>
                     <BaseButton v-if="isRenaming" variant="secondary" class="text-xs" @click="isRenaming = false">Cancel</BaseButton>
                   </div>
                 </div>
                 <BaseCard class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div>
                        <div class="flex items-center gap-2 text-slate-500 text-sm mb-1">
                          <DollarSign class="w-4 h-4" />
                          <h3>List Total</h3>
                        </div>
                        <p class="text-2xl font-bold">${{ stats.total_cost.toFixed(2) }}</p>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 text-slate-500 text-sm mb-1">
                          <ShoppingBag class="w-4 h-4" />
                          <h3>Items</h3>
                        </div>
                        <p class="text-2xl font-bold">{{ stats.item_count }}</p>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 text-slate-500 text-sm mb-1">
                          <Users class="w-4 h-4" />
                          <h3>Members</h3>
                        </div>
                        <p class="text-2xl font-bold">{{ settlementDetails.member_count }}</p>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 text-slate-500 text-sm mb-1">
                          <TrendingUp class="w-4 h-4" />
                          <h3>Share per User</h3>
                        </div>
                        <p class="text-2xl font-bold text-emerald-600">${{ stats.share_per_user.toFixed(2) }}</p>
                    </div>
                </BaseCard>
              </div>
 
              <h2 class="font-bold text-2xl text-slate-800 mb-4 flex items-center gap-2">
                  <BarChart3 class="w-7 h-7 text-emerald-600" />
                  Group Analytics
                </h2>
              <div v-if="analytics" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <BaseCard class="bg-white border-l-4 border-l-blue-500">
                    <p class="text-slate-500 text-xs uppercase font-bold">Group Total Spent</p>
                    <p class="text-2xl font-bold">${{ analytics.total_spent.toFixed(2) }}</p>
                  </BaseCard>
                  <BaseCard class="bg-white border-l-4 border-l-indigo-500">
                    <p class="text-slate-500 text-xs uppercase font-bold">Total Items</p>
                    <p class="text-2xl font-bold">{{ analytics.total_items }}</p>
                  </BaseCard>
                  <BaseCard class="bg-white border-l-4 border-l-purple-500">
                    <p class="text-slate-500 text-xs uppercase font-bold">Top Spender</p>
                    <p class="text-2xl font-bold">{{ analytics.user_totals[0]?.user || 'N/A' }}</p>
                    <p class="text-xs text-slate-500">${{ analytics.user_totals[0]?.total.toFixed(2) || '0.00' }}</p>
                  </BaseCard>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <BaseCard>
                    <h3 class="font-bold text-lg mb-4">Spending per User</h3>
                    <div class="h-64">
                      <Bar v-if="userChartData" :data="userChartData" :options="{ maintainAspectRatio: false }" />
                    </div>
                  </BaseCard>
                  <BaseCard>
                    <h3 class="font-bold text-lg mb-4">Spending by Category</h3>
                    <div class="h-64">
                      <Pie v-if="categoryChartData" :data="categoryChartData" :options="{ maintainAspectRatio: false }" />
                    </div>
                  </BaseCard>
                </div>

                <BaseCard>
                  <h3 class="font-bold text-lg mb-4">Monthly Spending Trend</h3>
                  <div class="h-64">
                    <Line v-if="trendChartData" :data="trendChartData" :options="{ maintainAspectRatio: false }" />
                  </div>
                </BaseCard>

                <BaseCard>
                  <h3 class="font-bold text-lg mb-4">Top 10 Most Expensive Items</h3>
                  <div class="overflow-x-auto">
                    <table class="w-full text-left">
                      <thead>
                        <tr class="text-slate-500 border-b border-slate-200">
                          <th class="p-4">Item</th>
                          <th class="p-4 text-right">Cost</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-100">
                        <tr v-for="item in analytics.top_items" :key="item.description" class="hover:bg-slate-50">
                          <td class="p-4">{{ item.description }}</td>
                          <td class="p-4 text-right font-medium">${{ item.cost.toFixed(2) }}</td>
                        </tr>
                        <tr v-if="!analytics.top_items?.length">
                          <td colspan="2" class="p-4 text-center text-slate-400 italic">No items found.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </BaseCard>
              </div>
              <div v-else class="text-center p-10 bg-white rounded-xl border border-slate-200 text-slate-500">
                  No analytics data available for this group.
              </div>
          </div>

      </div>
    </main>
  </div>
</template>

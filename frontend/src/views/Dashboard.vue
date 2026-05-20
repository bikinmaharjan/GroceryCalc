<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '../api/axios'
import { useAuthStore } from '../stores/auth'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'
import ToastNotification from '../components/ToastNotification.vue'
import LoadingSkeleton from '../components/LoadingSkeleton.vue'
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
  Calendar,
  Sun,
   Moon,
   LogOut,
   ChevronDown,
   Pen,
   User,
   Check,
   X,
   Plus
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

interface Item { id: number; description: string; cost: number; created_at: string; category?: string }
interface List { id: number; name: string; is_settling?: boolean; status?: string; total_cost?: number; archived_at?: string; share_per_user?: number; user_payments?: any[]; transactions?: any[] }
interface Group { id: number; name: string }
interface Transaction { from: string; to: string; from_name: string; to_name: string; amount: number; status: 'pending' | 'paid' }
interface Settlement { user: string; balance: number; total_paid: number; items: Item[] }
interface SettlementDetails { settlements: Settlement[]; transactions: Transaction[]; member_count: number }

const items = ref<Item[]>([])
const activeList = ref<List | null>(null)
const activeLists = ref<List[]>([])
const historyLists = ref<List[]>([])
const groups = ref<Group[]>([])
const selectedGroup = ref<Group | null>(null)
const isLoading = ref(false)
const stats = ref({ total_cost: 0, item_count: 0, share_per_user: 0 })
const analytics = ref<any>(null)
const settlementDetails = ref<SettlementDetails>({ settlements: [], transactions: [], member_count: 0 })
const paymentModal = ref({ show: false, transaction: null as Transaction | null })
const categoryModal = ref({ show: false, itemRef: null as any, newCategory: '' })
const confirmModal = ref({ show: false, title: '', message: '', action: null as (() => Promise<void>) | null })

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
const isDarkMode = ref(true)

watch(isDarkMode, (val) => {
    ChartJS.defaults.color = val ? '#ffffff' : '#64748b'
    ChartJS.defaults.borderColor = val ? 'rgba(255, 255, 255, 0.2)' : 'rgba(226, 232, 240, 0.8)'
    if (val) {
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.classList.remove('dark')
    }
}, { immediate: true })

const router = useRouter()
const route = useRoute()
const activeTab = ref('items')
const newListName = ref('')
const editingListName = ref('')
const isRenaming = ref(false)
const showCreateListModal = ref(false)
const isListDropdownOpen = ref(false)

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

const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    if (isDarkMode.value) {
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.classList.remove('dark')
    }
}

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    toast.value = { show: true, message, type }
    setTimeout(() => { toast.value.show = false }, 3000)
}

const loadData = async () => {
  isLoading.value = true
  try {
    const groupsRes = await apiClient.get<Group[]>('/my-groups', {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    groups.value = groupsRes.data
    if (groups.value.length > 0) {
        selectedGroup.value = groups.value[0]
        await loadListAndData()
    } else {
        router.push('/no-group')
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const loadSettlementDetails = async () => {
    if (!activeList.value) return
    const res = await apiClient.get(`/lists/${activeList.value.id}/settlements/details`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    settlementDetails.value = res.data
}

const loadHistory = async () => {
    if (!selectedGroup.value) return
    const res = await apiClient.get<List[]>(`/lists/archived?group_id=${selectedGroup.value.id}`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    historyLists.value = res.data
}

const loadListAndData = async () => {
    if (!selectedGroup.value) return
    isLoading.value = true
    const listRes = await apiClient.get<List[]>(`/lists/active?group_id=${selectedGroup.value.id}`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    activeLists.value = listRes.data
    if (listRes.data.length > 0) {
        activeList.value = listRes.data[0]
        await Promise.all([loadItems(), loadStats(), loadSettlementDetails(), loadHistory(), loadAnalytics()])
    } else {
        activeList.value = null
        items.value = []
        settlementDetails.value = { settlements: [], transactions: [], member_count: 0 }
        await Promise.all([loadHistory(), loadAnalytics()])
    }
    isLoading.value = false
}

const loadAnalytics = async () => {
    if (!selectedGroup.value) return
    try {
        const res = await apiClient.get(`/analytics?group_id=${selectedGroup.value.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        analytics.value = res.data
    } catch (e) {
        console.error('Failed to load analytics', e)
    }
}

const loadItems = async () => {
  if (!activeList.value) return
  const res = await apiClient.get<Item[]>(`/items?list_id=${activeList.value.id}`, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  items.value = res.data
}

const loadStats = async () => {
    if (!activeList.value) return
    const res = await apiClient.get(`/lists/${activeList.value.id}/settlements/calculate`, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    stats.value = res.data
}

const switchList = async (list: List) => {
    activeList.value = list
    editingListName.value = list.name
    isRenaming.value = false
    await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
}

const addItem = async () => {
  if (!activeList.value) return
  
  const cat = newItem.value.category.trim()
  if (cat && !categories.value.includes(cat)) {
    categories.value.push(cat)
  }

  await apiClient.post(`/items?list_id=${activeList.value.id}&description=${newItem.value.description}&cost=${newItem.value.cost}&category=${cat}`, null, {
    headers: { Authorization: `Bearer ${auth.token}` }
  })
  newItem.value = { description: '', cost: 0, category: 'grocery' }
  await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
}

const handleCategoryChange = (item: any) => {
    if (item.category === 'ADD_NEW') {
        categoryModal.value = { show: true, itemRef: item, newCategory: '' }
    }
}

const saveCategory = () => {
    const cat = categoryModal.value.newCategory.trim()
    if (cat) {
        if (!categories.value.includes(cat)) {
            categories.value.push(cat)
        }
        categoryModal.value.itemRef.category = cat
        showToast('Category added!')
    }
    categoryModal.value.show = false
}

const startEdit = (item: Item) => { editingItem.value = { ...item } }

const saveItem = async () => {
    if (!editingItem.value) return
    await apiClient.put(`/items/${editingItem.value.id}`, editingItem.value, {
        headers: { Authorization: `Bearer ${auth.token}` }
    })
    editingItem.value = null
    await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
}

const deleteItem = async (id: number) => {
    if (confirm('Delete this item?')) {
        await apiClient.delete(`/items/${id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        await Promise.all([loadItems(), loadStats(), loadSettlementDetails()])
    }
}

const markPaid = async (t: any) => {
    paymentModal.value = { show: true, transaction: t }
}

const confirmPayment = async () => {
    const t = paymentModal.value.transaction
    if (!t) return
    try {
        await apiClient.post(`/lists/${activeList.value?.id}/settlements/mark-paid`, {
            from_username: t.from,
            to_username: t.to,
            amount: t.amount
        }, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('Payment marked as paid!')
        paymentModal.value.show = false
        await loadSettlementDetails()
    } catch (e) {
        showToast('Failed to mark paid', 'error')
        paymentModal.value.show = false
    }
}

const startSettlement = async () => {
    confirmModal.value = { 
        show: true, 
        title: 'Start Settlement', 
        message: 'Are you sure you want to start settlement? Items will be locked.', 
        action: async () => {
            if (!activeList.value) return
            try {
                await apiClient.post(`/lists/${activeList.value.id}/settle`, null, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
                activeList.value.is_settling = true
                showToast('Settlement started. Items are now locked.')
            } catch (e) {
                showToast('Failed to start settlement', 'error')
            }
        }
    }
}

const archiveList = async () => {
    confirmModal.value = { 
        show: true, 
        title: 'Archive List', 
        message: 'Are you sure you want to archive this list? This will move it to history.', 
        action: async () => {
            if (!activeList.value) return
            try {
                await apiClient.post(`/lists/${activeList.value.id}/archive`, null, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
                showToast('List archived successfully!')
                await loadListAndData()
            } catch (e) {
                showToast('Failed to archive list', 'error')
            }
        }
    }
}

const cancelSettlement = async () => {
    confirmModal.value = { 
        show: true, 
        title: 'Cancel Settlement', 
        message: 'Are you sure you want to cancel settlement? This will unlock the list for adding new items.', 
        action: async () => {
            if (!activeList.value) return
            try {
                await apiClient.post(`/lists/${activeList.value.id}/cancel-settlement`, null, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
                showToast('Settlement cancelled!')
                await loadListAndData()
            } catch (e) {
                showToast('Failed to cancel settlement', 'error')
            }
        }
    }
}

const confirmAction = async () => {
    if (confirmModal.value.action) {
        await confirmModal.value.action()
    }
    confirmModal.value.show = false
}

const createList = async () => {
    if (!selectedGroup.value) return
    try {
        await apiClient.post(`/lists?group_id=${selectedGroup.value.id}&name=${newListName.value}`, null, {
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
        await apiClient.put(`/lists/${activeList.value.id}?name=${editingListName.value}`, null, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        showToast('List renamed successfully!')
        activeList.value.name = editingListName.value
        isRenaming.value = false
    } catch (e) {
        showToast('Failed to rename list', 'error')
    }
}

onMounted(() => {
  loadData()
  document.addEventListener('click', (e) => {
    const dropdown = (e.target as HTMLElement).closest('.list-dropdown')
    if (!dropdown) isListDropdownOpen.value = false
  })
})
</script>

<template>
  <div :class="['min-h-screen transition-colors duration-300', isDarkMode ? 'bg-slate-900 text-slate-100' : 'bg-slate-50']">
    <nav :class="['shadow-sm p-4 flex justify-between items-center transition-colors duration-300', isDarkMode ? 'bg-slate-800 text-slate-100' : 'bg-white text-slate-900']">
      <div class="flex items-center gap-4">
        <span class="font-bold text-xl text-emerald-600">GrocerySplit</span>
        <select v-model="selectedGroup" @change="loadListAndData" class="p-3 border rounded-xl w-40 focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100">
            <option v-for="g in groups" :key="g.id" :value="g">{{ g.name }}</option>
        </select>
      </div>
        <div class="flex gap-4 items-center">
            <RouterLink to="/dashboard/items" :class="{'text-emerald-600 font-medium': activeTab === 'items'}">Items</RouterLink>
            <RouterLink to="/dashboard/settlements" :class="{'text-emerald-600 font-medium': activeTab === 'settlements'}">Settlements</RouterLink>
            <RouterLink to="/dashboard/history" :class="{'text-emerald-600 font-medium': activeTab === 'history'}">History</RouterLink>
            <RouterLink to="/dashboard/analytics" :class="{'text-emerald-600 font-medium': activeTab === 'analytics'}">Analytics</RouterLink>
            <!-- User Profile Dropdown -->
            <div class="relative group">
              <button class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-700 transition-colors">
                <User class="w-5 h-5 text-slate-400" />
                <span class="text-sm font-medium">{{ auth.user?.display_name || auth.user?.username }}</span>
              </button>
              <div class="absolute right-0 mt-0 hidden group-hover:block bg-slate-800 border border-slate-700 rounded-lg shadow-lg min-w-40 z-10">
                <button @click="toggleDarkMode" class="w-full text-left px-4 py-2 hover:bg-slate-700 transition-colors text-sm text-slate-300 flex items-center gap-2">
                  <Sun v-if="isDarkMode" class="w-4 h-4" />
                  <Moon v-else class="w-4 h-4" />
                  {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
                </button>
                <div class="border-t border-slate-700"></div>
                <button @click="handleLogout" class="w-full text-left px-4 py-2 hover:bg-red-900/20 transition-colors text-sm text-red-400 flex items-center gap-2">
                  <LogOut class="w-4 h-4" />
                  Logout
                </button>
              </div>
            </div>
        </div>

    </nav>
    <main class="p-6 max-w-5xl mx-auto">
       <ToastNotification :show="toast.show" :message="toast.message" :type="toast.type" />
      
        <div v-if="isLoading" class="p-6 max-w-5xl mx-auto">
          <LoadingSkeleton />
        </div>
         <div v-else-if="!activeList" class="text-center mt-20 max-w-md mx-auto">
           <div class="mb-6 inline-flex p-6 bg-emerald-50 dark:bg-emerald-900/30 rounded-full text-emerald-600 dark:text-emerald-400">
             <ShoppingBag class="w-12 h-12" />
           </div>
           <h3 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">No active list found</h3>
           <p class="text-slate-500 dark:text-slate-400 mb-8">It looks like you don't have any active grocery lists. Create one to start splitting costs with your group!</p>
           <div class="flex flex-col sm:flex-row justify-center gap-3">
               <input v-model="newListName" placeholder="List name (optional)" class="p-3 border rounded-xl w-full sm:w-64 focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100" />
               <BaseButton @click="createList" class="px-6">Create List</BaseButton>
           </div>
         </div>


       
        <div v-else>
          <Transition name="fade" mode="out-in">
            <div :key="activeTab">
              <!-- Items Tab -->
              <div v-if="activeTab === 'items'">

               <!-- Current List Summary -->
               <div class="mb-8">
                 <div class="flex items-center gap-3 mb-4">
                   <div class="p-2 bg-emerald-100 rounded-lg text-emerald-700">
                     <ShoppingBag class="w-6 h-6" />
                   </div>
                   
                   <!-- List Selector Dropdown -->
                   <div class="relative flex-1 list-dropdown">
                     <button @click="isListDropdownOpen = !isListDropdownOpen" :class="['w-full flex items-center justify-between px-4 py-3 rounded-xl border transition-all', isListDropdownOpen ? 'border-emerald-500 bg-emerald-50 dark:bg-slate-800 dark:border-emerald-500' : 'border-slate-200 dark:border-slate-700 hover:border-emerald-300', isDarkMode ? 'dark:bg-slate-800 dark:text-slate-100' : 'bg-white text-slate-900']">
                       <span class="font-bold text-lg">{{ activeList?.name }}</span>
                       <ChevronDown :class="['w-5 h-5 transition-transform', isListDropdownOpen ? 'rotate-180' : '']" />
                     </button>
                     
                     <div v-if="isListDropdownOpen" :class="['absolute top-full left-0 right-0 mt-2 rounded-xl border shadow-lg z-20', isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200']">
                       <div class="max-h-64 overflow-y-auto">
                         <button v-for="list in activeLists" :key="list.id" @click="switchList(list); isListDropdownOpen = false" :class="['w-full text-left px-4 py-3 border-b transition-colors', activeList?.id === list.id ? 'bg-emerald-50 dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 font-semibold' : 'hover:bg-slate-50 dark:hover:bg-slate-700', isDarkMode && activeList?.id !== list.id ? 'border-slate-700 text-slate-300' : 'border-slate-100']">
                           {{ list.name }}
                         </button>
                       </div>
                       <button @click="showCreateListModal = true; isListDropdownOpen = false" class="w-full flex items-center gap-2 px-4 py-3 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-slate-700 transition-colors font-medium text-sm">
                         <Plus class="w-4 h-4" />
                         New List
                       </button>
                     </div>
                   </div>

                   <!-- Rename Button -->
                   <div class="flex gap-1 items-center">
                     <button v-if="!isRenaming" @click="isRenaming = true; editingListName = activeList.name" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 transition-colors" title="Rename list">
                       <Pen class="w-4 h-4" />
                     </button>
                     <div v-else class="flex gap-1">
                       <button @click="renameList" class="p-2 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition-colors" title="Save">
                         <Check class="w-4 h-4" />
                       </button>
                       <button @click="isRenaming = false" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 transition-colors" title="Cancel">
                         <X class="w-4 h-4" />
                       </button>
                     </div>
                   </div>
                 </div>

                 <!-- Rename Input (only show when renaming) -->
                 <div v-if="isRenaming" class="mb-4 flex gap-2">
                   <input v-model="editingListName" :class="['flex-1 p-3 border rounded-xl font-bold text-lg focus:ring-2 focus:ring-emerald-500 outline-none', isDarkMode ? 'text-slate-100 bg-slate-800 border-slate-700' : 'text-slate-900 bg-white border-slate-200']" />
                 </div>

                 <BaseCard class="bg-gradient-to-br from-emerald-500 to-emerald-700 text-white border-none shadow-lg p-6 mb-6">
                   <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <div>
                          <div class="flex items-center gap-2 text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">
                            <DollarSign class="w-3 h-3" />
                            <span>List Total</span>
                          </div>
                          <p class="text-3xl font-bold">${{ stats.total_cost.toFixed(2) }}</p>
                      </div>
                      <div>
                          <div class="flex items-center gap-2 text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">
                            <ShoppingBag class="w-3 h-3" />
                            <span>Items</span>
                          </div>
                          <p class="text-3xl font-bold">{{ stats.item_count }}</p>
                      </div>
                      <div>
                          <div class="flex items-center gap-2 text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">
                            <Users class="w-3 h-3" />
                            <span>Members</span>
                          </div>
                          <p class="text-3xl font-bold">{{ settlementDetails.member_count }}</p>
                      </div>
                      <div>
                          <div class="flex items-center gap-2 text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">
                            <TrendingUp class="w-3 h-3" />
                            <span>Share per User</span>
                          </div>
                          <p class="text-3xl font-bold">${{ stats.share_per_user.toFixed(2) }}</p>
                      </div>
                   </div>
                 </BaseCard>

             </div>

<div v-if="!activeList?.is_settling" class="mb-8 p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm transition-all hover:shadow-md">
                 <div class="flex items-center gap-2 mb-4">
                   <div class="p-1.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-lg">
                     <ShoppingBag class="w-5 h-5" />
                   </div>
                   <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">Add New Item</h3>
                 </div>
                 <div class="flex flex-wrap gap-4">
                     <input v-model="newItem.description" placeholder="What did you buy?" class="p-3 border rounded-xl flex-1 min-w-[200px] focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100" />
                     <div class="relative w-32">
                       <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                       <input v-model.number="newItem.cost" type="number" step="0.01" placeholder="0.00" class="p-3 pl-7 border rounded-xl w-full focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100" />
                     </div>
                     <div class="flex gap-2">
                       <select v-model="newItem.category" @change="handleCategoryChange(newItem)" class="p-3 border rounded-xl w-40 focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100">
                         <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                         <option value="ADD_NEW">+ Add New...</option>
                       </select>
                     </div>
                     <BaseButton @click="addItem" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-sm transition-all">Add Item</BaseButton>
                 </div>
             </div>

            <div v-else class="mb-8 p-6 bg-amber-50 rounded-xl border border-amber-200 text-amber-800 text-center">
                <p class="font-medium">Settlement in progress. Adding new items is disabled.</p>
            </div>
             <BaseCard class="overflow-hidden border-none shadow-sm bg-white dark:bg-slate-800">
               <div class="p-6 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
                 <div class="flex items-center gap-2">
                   <ShoppingBag class="w-5 h-5 text-emerald-600" />
                   <h2 class="font-bold text-lg text-slate-800 dark:text-slate-100">Itemized List</h2>
                 </div>
                 <span class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                   {{ items.length }} items
                 </span>
               </div>
               <div class="overflow-x-auto">

<table class="w-full text-left">
                      <thead>
                        <tr class="text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
                          <th class="p-4 font-medium">Description</th>
                          <th class="p-4 font-medium">Category</th>
                          <th class="p-4 font-medium">Cost</th>
                          <th class="p-4 font-medium">Date</th>
                          <th class="p-4 text-right font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                        <template v-for="item in items" :key="item.id">
                            <tr v-if="editingItem?.id !== item.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                              <td class="p-4 text-slate-800 dark:text-slate-200">{{ item.description }}</td>
                              <td class="p-4">
                                <span class="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-1 rounded-full">
                                  {{ item.category || 'grocery' }}
                                </span>
                              </td>
                              <td class="p-4 text-slate-800 dark:text-slate-200 font-medium">${{ item.cost.toFixed(2) }}</td>
                              <td class="p-4 text-slate-500 dark:text-slate-400 text-sm">{{ new Date(item.created_at).toLocaleDateString() }}</td>
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
                            <tr v-else class="bg-slate-50 dark:bg-slate-700/30">
                                <td class="p-4"><input v-model="editingItem.description" class="p-1 border rounded w-full dark:bg-slate-900 dark:border-slate-600 dark:text-slate-100" /></td>
                                <td class="p-4">
                                 <select v-model="editingItem.category" @change="handleCategoryChange(editingItem)" class="p-1 border rounded w-full dark:bg-slate-900 dark:border-slate-600 dark:text-slate-100">
                                   <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                                   <option value="ADD_NEW">+ Add New...</option>
                                 </select>
                               </td>
                                <td class="p-4"><input v-model.number="editingItem.cost" type="number" class="p-1 border rounded w-20 dark:bg-slate-900 dark:border-slate-600 dark:text-slate-100" /></td>
                                <td class="p-4 text-slate-400 dark:text-slate-500">...</td>
                                <td class="p-4 text-right">
                                    <BaseButton variant="primary" class="text-xs mr-2" @click="saveItem">Save</BaseButton>
                                    <BaseButton variant="secondary" class="text-xs" @click="editingItem = null">Cancel</BaseButton>
                                </td>
                            </tr>
                        </template>
                        <tr v-if="items.length === 0">
                            <td colspan="5" class="p-12 text-center">
                              <div class="flex flex-col items-center justify-center space-y-3">
                                <div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-full text-slate-400">
                                  <ShoppingBag class="w-8 h-8" />
                                </div>
                                <p class="text-slate-500 dark:text-slate-400 font-medium">No items added yet.</p>
                                <p class="text-xs text-slate-400 dark:text-slate-500 max-w-xs mx-auto">Add the first item to your list to start calculating costs!</p>
                              </div>
                            </td>
                        </tr>
                      </tbody>
                    </table>


              </div>
            </BaseCard>
        </div>

         <!-- Settlements Tab -->
         <div v-if="activeTab === 'settlements'" class="space-y-6">
              <div class="flex justify-between items-center mb-4">
                  <h2 :class="['font-bold text-2xl', isDarkMode ? 'text-slate-100' : 'text-slate-800']">Settlement</h2>
                  <div class="flex gap-3">
                     <BaseButton v-if="!activeList?.is_settling" @click="startSettlement" variant="primary">Start Settlement</BaseButton>
                      <BaseButton v-if="activeList?.is_settling" @click="archiveList" variant="secondary">Archive List</BaseButton>
                      <BaseButton v-if="activeList?.is_settling" @click="cancelSettlement" variant="secondary" class="border-amber-500 text-amber-600 hover:bg-amber-50">Cancel Settlement</BaseButton>

                 </div>
             </div>

             <!-- Overall Balance Summary -->
             <BaseCard class="bg-gradient-to-br from-emerald-500 to-emerald-700 text-white border-none shadow-lg">
               <div class="flex flex-col md:flex-row justify-between items-center gap-6 p-2">
                 <div class="flex items-center gap-4">
                   <div class="p-3 bg-white/20 rounded-2xl backdrop-blur-md">
                     <DollarSign class="w-8 h-8 text-white" />
                   </div>
                   <div>
                     <p class="text-emerald-100 text-sm font-medium">Total Group Expenditure</p>
                     <p class="text-3xl font-bold">${{ stats.total_cost.toFixed(2) }}</p>
                   </div>
                 </div>
                 <div class="grid grid-cols-2 gap-8">
                   <div class="text-center md:text-left">
                     <p class="text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">Pending Debts</p>
                     <p class="text-2xl font-bold">{{ settlementDetails.transactions.filter(t => t.status === 'pending').length }}</p>
                   </div>
                   <div class="text-center md:text-left">
                     <p class="text-emerald-100 text-xs uppercase font-bold tracking-wider mb-1">Settled</p>
                     <p class="text-2xl font-bold">{{ settlementDetails.transactions.filter(t => t.status === 'paid').length }}</p>
                   </div>
                 </div>
               </div>
             </BaseCard>

              <BaseCard class="grid grid-cols-1 md:grid-cols-4 gap-6 bg-white dark:bg-slate-800">
                <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                    <h3 class="text-slate-500 dark:text-slate-400 text-sm mb-1">Group Total Spent</h3>
                    <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">${{ stats.total_cost.toFixed(2) }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                    <h3 class="text-slate-500 dark:text-slate-400 text-sm mb-1">Total Items</h3>
                    <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">{{ stats.item_count }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                    <h3 class="text-slate-500 dark:text-slate-400 text-sm mb-1">Members</h3>
                    <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">{{ settlementDetails.member_count }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                    <h3 class="text-slate-500 dark:text-slate-400 text-sm mb-1">Share per User</h3>
                    <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">${{ stats.share_per_user.toFixed(2) }}</p>
                </div>
              </BaseCard>

            
             <BaseCard class="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
                 <h3 class="font-bold text-lg mb-4 text-slate-800 dark:text-slate-100">Who owes who?</h3>
                 <ul class="space-y-2">
                     <li v-for="t in settlementDetails.transactions" :key="t.from" class="bg-slate-100 dark:bg-slate-700/50 p-3 rounded flex justify-between items-center transition-colors">
                         <span class="flex items-center gap-2 text-slate-800 dark:text-slate-200">
                           <span class="font-bold">{{ t.from_name }}</span> 
                           <ArrowRight class="w-4 h-4 text-slate-400" /> 
                           <span class="font-bold">{{ t.to_name }}</span> 
                           <span class="ml-2 text-slate-600 dark:text-slate-400">${{ t.amount.toFixed(2) }}</span>
                         </span>
                         <div class="flex items-center gap-2">
                             <template v-if="t.status === 'paid'">
                                 <span class="text-emerald-600 dark:text-emerald-400 text-xs font-medium uppercase">Paid</span>
                             </template>
                             <template v-else>
                                 <span v-if="t.to === auth.user?.username" class="text-amber-600 dark:text-amber-400 text-xs font-medium uppercase">
                                     Pending
                                 </span>
                                 <BaseButton v-if="t.from === auth.user?.username" @click="markPaid(t)" class="text-xs">Mark Paid</BaseButton>
                             </template>
                         </div>
                     </li>
                     <li v-if="settlementDetails.transactions.length === 0" class="text-center p-8 bg-slate-50 dark:bg-slate-700/30 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700">
                         <div class="flex flex-col items-center justify-center space-y-2">
                           <div class="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
                             <DollarSign class="w-6 h-6" />
                           </div>
                           <p class="text-slate-600 dark:text-slate-300 font-medium">All debts settled!</p>
                           <p class="text-xs text-slate-400 dark:text-slate-500">Everyone is squared away. Great job!</p>
                         </div>
                     </li>
                 </ul>
             </BaseCard>

            
             <BaseCard v-for="s in settlementDetails.settlements" :key="s.user" class="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
                 <div class="flex justify-between items-center mb-4">
                     <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">{{ s.user }}</h3>
                     <span :class="s.balance >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'" class="font-bold">
                         {{ s.balance >= 0 ? 'Owed: ' : 'Owes: ' }} ${{ Math.abs(s.balance).toFixed(2) }}
                     </span>
                 </div>
                 <p class="text-sm text-slate-500 dark:text-slate-400 mb-2">Paid: ${{ s.total_paid.toFixed(2) }}</p>
                 <ul class="text-sm text-slate-600 dark:text-slate-300 list-disc ml-4">
                     <li v-for="item in s.items" :key="item.description">
                         {{ item.description }}: ${{ item.cost.toFixed(2) }}
                     </li>
                 </ul>
             </BaseCard>

        </div>

          <!-- History Tab -->
          <div v-if="activeTab === 'history'" class="space-y-6">
               <div :class="['flex justify-between items-center mb-6 pb-4 border-b', isDarkMode ? 'border-slate-700' : 'border-slate-200']">
                 <div class="flex items-center gap-3">
                   <div class="p-2 bg-indigo-100 rounded-lg text-indigo-700">
                     <Calendar class="w-6 h-6" />
                   </div>
                   <h2 :class="['font-extrabold text-3xl tracking-tight', isDarkMode ? 'text-slate-100' : 'text-slate-900']">Archived Lists</h2>
                 </div>
              </div>

              <BaseCard class="bg-gradient-to-br from-indigo-500 to-indigo-700 text-white border-none shadow-lg p-6 mb-6">
                <div class="flex flex-col md:flex-row justify-between items-center gap-6">
                  <div class="flex items-center gap-4">
                    <div class="p-3 bg-white/20 rounded-2xl backdrop-blur-md">
                      <Calendar class="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <p class="text-indigo-100 text-sm font-medium">Total Archived Spending</p>
                      <p class="text-3xl font-bold">${{ historyLists.reduce((sum, list) => sum + (list.total_cost || 0), 0).toFixed(2) }}</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-8">
                    <div class="text-center md:text-left">
                      <p class="text-indigo-100 text-xs uppercase font-bold tracking-wider mb-1">Total Lists</p>
                      <p class="text-2xl font-bold">{{ historyLists.length }}</p>
                    </div>
                    <div class="text-center md:text-left">
                      <p class="text-indigo-100 text-xs uppercase font-bold tracking-wider mb-1">Avg. Per List</p>
                      <p class="text-2xl font-bold">${{ historyLists.length > 0 ? (historyLists.reduce((sum, list) => sum + (list.total_cost || 0), 0) / historyLists.length).toFixed(2) : '0.00' }}</p>
                    </div>
                  </div>
                </div>
              </BaseCard>

              <div v-if="historyLists.length === 0" class="text-center p-16 bg-white rounded-2xl border-2 border-dashed border-slate-200 text-slate-500">

                  <div class="flex flex-col items-center justify-center space-y-3">
                    <div class="p-4 bg-slate-50 rounded-full text-slate-400">
                      <Calendar class="w-10 h-10" />
                    </div>
                    <h3 class="text-lg font-bold text-slate-700">No archived lists</h3>
                    <p class="text-sm max-w-xs mx-auto">Your archived lists will appear here once you start archiving your completed grocery lists.</p>
                  </div>
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <BaseCard v-for="list in historyLists" :key="list.id" class="flex flex-col h-full bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
                      <div class="flex justify-between items-start mb-4">
                          <div>
                              <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">{{ list.archived_at ? new Date(list.archived_at).toLocaleDateString() : 'Unknown Date' }}</h3>
                              <p class="text-xs text-slate-500 dark:text-slate-400">{{ list.name }}</p>
                          </div>
                          <div class="text-right">
                              <p class="text-sm text-slate-500 dark:text-slate-400">Total</p>
                              <p class="font-bold text-emerald-600 dark:text-emerald-400">${{ (list.total_cost || 0).toFixed(2) }}</p>
                          </div>
                      </div>
                      <div class="border-t dark:border-slate-700 pt-3 mb-4">
                          <div class="flex justify-between items-center mb-2">
                              <p class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase">Share per Person</p>
                              <p class="text-xs font-bold text-slate-700 dark:text-slate-300">${{ (list.share_per_user || 0).toFixed(2) }}</p>
                          </div>
                          <div class="space-y-1">
                              <div v-for="p in (list.user_payments || [])" :key="p.user" class="flex justify-between text-sm">
                                  <span class="text-slate-600 dark:text-slate-400">{{ p.user }}</span>
                                  <span class="font-medium text-slate-800 dark:text-slate-200">${{ p.paid.toFixed(2) }}</span>
                              </div>
                              <div v-if="(list.user_payments?.length || 0) === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">
                                  No payment data available.
                              </div>
                          </div>
                      </div>
                      <div class="border-t dark:border-slate-700 pt-3">
                          <p class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase mb-2">Final Settlements</p>
                          <div class="space-y-1">
                              <div v-for="t in (list.transactions || [])" :key="t.from + t.to" class="flex justify-between text-sm">
                                  <span class="text-slate-600 dark:text-slate-400">{{ t.from }} <span class="text-emerald-500 mx-1">→</span> {{ t.to }}</span>
                                  <span class="font-medium text-slate-800 dark:text-slate-200">${{ t.amount.toFixed(2) }}</span>
                              </div>
                              <div v-if="(list.transactions?.length || 0) === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">
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
                <div :class="['flex justify-between items-center mb-6 pb-4 border-b', isDarkMode ? 'border-slate-700' : 'border-slate-200']">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-purple-100 rounded-lg text-purple-700">
                      <BarChart3 class="w-6 h-6" />
                    </div>
                    <h2 :class="['font-extrabold text-3xl tracking-tight', isDarkMode ? 'text-slate-100' : 'text-slate-900']">Group Analytics</h2>
                  </div>
                 </div>
                 
                 <BaseCard class="bg-gradient-to-br from-purple-500 to-purple-700 text-white border-none shadow-lg p-6 mb-6">
                   <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                     <div>
                       <div class="flex items-center gap-2 text-purple-100 text-xs uppercase font-bold tracking-wider mb-1">
                         <DollarSign class="w-3 h-3" />
                         <span>Total Spent</span>
                       </div>
                       <p class="text-3xl font-bold">${{ analytics?.total_spent.toFixed(2) || '0.00' }}</p>
                     </div>
                     <div>
                       <div class="flex items-center gap-2 text-purple-100 text-xs uppercase font-bold tracking-wider mb-1">
                         <ShoppingBag class="w-3 h-3" />
                         <span>Total Items</span>
                       </div>
                       <p class="text-3xl font-bold">{{ analytics?.total_items || 0 }}</p>
                     </div>
                     <div>
                       <div class="flex items-center gap-2 text-purple-100 text-xs uppercase font-bold tracking-wider mb-1">
                         <Users class="w-3 h-3" />
                         <span>Top Spender</span>
                       </div>
                       <p class="text-xl font-bold">{{ analytics?.user_totals[0]?.user || 'N/A' }}</p>
                       <p class="text-sm text-purple-200">${{ analytics?.user_totals[0]?.total.toFixed(2) || '0.00' }}</p>
                     </div>
                   </div>
                 </BaseCard>
               </div>
 
               <h2 :class="['font-bold text-2xl mb-4 flex items-center gap-2', isDarkMode ? 'text-slate-100' : 'text-slate-800']">
                   <BarChart3 class="w-7 h-7 text-emerald-600" />
                   Detailed Insights
                 </h2>
               <div v-if="analytics" class="space-y-6">
                 <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                   <BaseCard class="bg-white dark:bg-slate-800 border-l-4 border-l-blue-500">
                     <p class="text-slate-500 dark:text-slate-400 text-xs uppercase font-bold">Group Total Spent</p>
                     <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">${{ analytics.total_spent.toFixed(2) }}</p>
                   </BaseCard>
                   <BaseCard class="bg-white dark:bg-slate-800 border-l-4 border-l-indigo-500">
                     <p class="text-slate-500 dark:text-slate-400 text-xs uppercase font-bold">Total Items</p>
                     <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">{{ analytics.total_items }}</p>
                   </BaseCard>
                   <BaseCard class="bg-white dark:bg-slate-800 border-l-4 border-l-purple-500">
                     <p class="text-slate-500 dark:text-slate-400 text-xs uppercase font-bold">Top Spender</p>
                     <p class="text-2xl font-bold text-slate-800 dark:text-slate-100">{{ analytics.user_totals[0]?.user || 'N/A' }}</p>
                     <p class="text-xs text-slate-500 dark:text-slate-400">${{ analytics.user_totals[0]?.total.toFixed(2) || '0.00' }}</p>
                   </BaseCard>
                 </div>
 
                 <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <BaseCard class="bg-white dark:bg-slate-800">
                     <h3 class="font-bold text-lg mb-4 text-slate-800 dark:text-slate-100">Spending per User</h3>
                     <div class="h-64">
                        <Bar v-if="userChartData" :data="userChartData" />
                     </div>
                   </BaseCard>
                   <BaseCard class="bg-white dark:bg-slate-800">
                     <h3 class="font-bold text-lg mb-4 text-slate-800 dark:text-slate-100">Spending by Category</h3>
                      <div class="h-64 flex items-center justify-center">
                         <Pie v-if="categoryChartData" :data="categoryChartData" :options="{ plugins: { legend: { position: 'bottom' } } }" />
                      </div>
                   </BaseCard>
                 </div>
 
                 <BaseCard class="bg-white dark:bg-slate-800">
                   <h3 class="font-bold text-lg mb-4 text-slate-800 dark:text-slate-100">Monthly Spending Trend</h3>
                   <div class="h-64">
                       <Line v-if="trendChartData" :data="trendChartData" />
                   </div>
                 </BaseCard>
 
                 <BaseCard class="bg-white dark:bg-slate-800">
                   <h3 class="font-bold text-lg mb-4 text-slate-800 dark:text-slate-100">Top 10 Most Expensive Items</h3>
                   <div class="overflow-x-auto">
                     <table class="w-full text-left">
                       <thead>
                         <tr class="text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
                           <th class="p-4 font-medium">Item</th>
                           <th class="p-4 text-right font-medium">Cost</th>
                         </tr>
                       </thead>
                       <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                         <tr v-for="item in analytics.top_items" :key="item.description" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                           <td class="p-4 text-slate-800 dark:text-slate-200">{{ item.description }}</td>
                           <td class="p-4 text-right font-medium text-slate-800 dark:text-slate-200">${{ item.cost.toFixed(2) }}</td>
                         </tr>
                         <tr v-if="!analytics.top_items?.length">
                           <td colspan="2" class="p-4 text-center text-slate-400 dark:text-slate-500 italic">No items found.</td>
                         </tr>
                       </tbody>
                     </table>
                   </div>
                 </BaseCard>

                </div>
                <div v-else class="text-center p-16 bg-white rounded-2xl border-2 border-dashed border-slate-200 text-slate-500">
                  <div class="flex flex-col items-center justify-center space-y-3">
                    <div class="p-4 bg-slate-50 rounded-full text-slate-400">
                      <PieChart class="w-10 h-10" />
                    </div>
                    <h3 class="text-lg font-bold text-slate-700">No analytics available</h3>
                    <p class="text-sm max-w-xs mx-auto">Add more items and lists to see your spending trends and group insights!</p>
                  </div>
              </div>
          </div>
        </div>
      </Transition>
    </div>
    </main>


      <!-- Create New List Modal -->
      <div v-if="showCreateListModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
              <ShoppingBag class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Create New List</h3>
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">List Name</label>
            <input v-model="newListName" placeholder="e.g. Weekly Groceries" class="p-3 border rounded-xl w-full focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100" />
          </div>
          
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="showCreateListModal = false">Cancel</BaseButton>
            <BaseButton variant="primary" class="flex-1 bg-emerald-600 hover:bg-emerald-700 flex items-center justify-center gap-2" @click="async () => { await createList(); showCreateListModal = false }">
              <Plus class="w-4 h-4" />
              Create List
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Category Addition Modal -->
      <div v-if="categoryModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
              <ShoppingBag class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Add New Category</h3>
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">Category Name</label>
            <input v-model="categoryModal.newCategory" placeholder="e.g. Entertainment" class="p-3 border rounded-xl w-full focus:ring-2 focus:ring-emerald-500 outline-none dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100" />
          </div>
          
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="categoryModal.show = false">Cancel</BaseButton>
            <BaseButton variant="primary" class="flex-1 bg-emerald-600 hover:bg-emerald-700" @click="saveCategory">Save Category</BaseButton>
          </div>
        </div>
      </div>

      <!-- Confirmation Modal -->
      <div v-if="confirmModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-full">
              <DollarSign class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">{{ confirmModal.title }}</h3>
          </div>
          
          <div class="mb-6">
            <p class="text-slate-600 dark:text-slate-300">{{ confirmModal.message }}</p>
          </div>
          
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="confirmModal.show = false">Cancel</BaseButton>
            <BaseButton variant="primary" class="flex-1 bg-amber-600 hover:bg-amber-700" @click="confirmAction">Confirm</BaseButton>
          </div>
        </div>
      </div>

      <!-- Payment Confirmation Modal -->

     <div v-if="paymentModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
       <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
         <div class="flex items-center gap-3 mb-4">
           <div class="p-2 bg-emerald-100 text-emerald-600 rounded-full">
             <DollarSign class="w-6 h-6" />
           </div>
           <h3 class="text-xl font-bold text-slate-900">Confirm Payment</h3>
         </div>
         
         <div class="bg-slate-50 rounded-xl p-4 mb-6 text-center">
           <p class="text-slate-500 text-sm mb-1">You are paying</p>
           <p class="text-2xl font-bold text-slate-900 mb-4">
             ${{ paymentModal.transaction?.amount.toFixed(2) }}
           </p>
           <div class="flex items-center justify-center gap-3 text-slate-700">
             <span class="font-medium">{{ auth.user?.display_name || auth.user?.username }}</span>
             <ArrowRight class="w-4 h-4 text-slate-400" />
             <span class="font-medium">{{ paymentModal.transaction?.to_name || paymentModal.transaction?.to }}</span>
           </div>
         </div>
         
         <div class="flex gap-3">
           <BaseButton variant="secondary" class="flex-1" @click="paymentModal.show = false">Cancel</BaseButton>
           <BaseButton variant="primary" class="flex-1 bg-emerald-600 hover:bg-emerald-700" @click="confirmPayment">Confirm Payment</BaseButton>
         </div>
       </div>
     </div>
   </div>
 </template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>


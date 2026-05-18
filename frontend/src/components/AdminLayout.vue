<template>
  <div class="min-h-screen bg-slate-50 flex">
    <aside class="w-64 bg-slate-900 text-slate-100 p-6 flex flex-col">
      <h1 class="text-xl font-bold mb-8 text-white tracking-tight">GrocerySplit Admin</h1>
      <nav class="space-y-2 flex-grow">
        <router-link to="/admin" 
          class="block py-2.5 px-4 rounded-lg transition-colors"
          :class="{'bg-emerald-600 text-white': $route.path === '/admin', 'hover:bg-slate-800 text-slate-400': $route.path !== '/admin'}">
          Dashboard
        </router-link>
        <router-link to="/admin/users" 
          class="block py-2.5 px-4 rounded-lg transition-colors"
          :class="{'bg-emerald-600 text-white': $route.path === '/admin/users', 'hover:bg-slate-800 text-slate-400': $route.path !== '/admin/users'}">
          Users
        </router-link>
        <router-link to="/admin/groups" 
          class="block py-2.5 px-4 rounded-lg transition-colors"
          :class="{'bg-emerald-600 text-white': $route.path === '/admin/groups', 'hover:bg-slate-800 text-slate-400': $route.path !== '/admin/groups'}">
          Groups
        </router-link>
        <router-link to="/admin/lists" 
          class="block py-2.5 px-4 rounded-lg transition-colors"
          :class="{'bg-emerald-600 text-white': $route.path === '/admin/lists', 'hover:bg-slate-800 text-slate-400': $route.path !== '/admin/lists'}">
          Lists
        </router-link>
        <router-link to="/admin/audit" 
          class="block py-2.5 px-4 rounded-lg transition-colors"
          :class="{'bg-emerald-600 text-white': $route.path === '/admin/audit', 'hover:bg-slate-800 text-slate-400': $route.path !== '/admin/audit'}">
          Audit Logs
        </router-link>
      </nav>
      <button @click="handleLogout" class="block w-full py-2.5 px-4 text-left text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
        Logout
      </button>
    </aside>
    <main class="flex-1 p-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

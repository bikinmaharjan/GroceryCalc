<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import BaseButton from '../components/BaseButton.vue'
import { AlertCircle } from '@lucide/vue'

const router = useRouter()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100">
    <nav class="shadow-sm p-4 flex justify-between items-center transition-colors duration-300 bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100">
      <div class="flex items-center gap-4">
        <span class="font-bold text-xl text-emerald-600">GrocerySplit</span>
      </div>
      <button @click="handleLogout" class="text-slate-600 hover:text-red-600 flex items-center gap-2 transition-colors dark:text-slate-400 dark:hover:text-red-400">
        Logout
      </button>
    </nav>

    <main class="flex-1 flex items-center justify-center p-6">
      <div class="text-center max-w-md mx-auto">
        <div class="mb-6 inline-flex p-6 bg-amber-50 dark:bg-amber-900/30 rounded-full text-amber-600 dark:text-amber-400">
          <AlertCircle class="w-12 h-12" />
        </div>
        <h3 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">No Group Assigned</h3>
        <p class="text-slate-500 dark:text-slate-400 mb-8">
          You are not currently part of any group. Please contact your administrator to be added to a group so you can start splitting costs!
        </p>
        <div class="flex justify-center gap-3">
          <BaseButton @click="handleLogout" variant="secondary" class="px-6">
            Return to Login
          </BaseButton>
        </div>
      </div>
    </main>
  </div>
</template>

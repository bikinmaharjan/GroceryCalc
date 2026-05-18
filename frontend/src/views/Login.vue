<template>
  <div class="min-h-screen flex items-center justify-center bg-emerald-700">
    <div class="bg-white p-8 rounded-lg shadow-xl w-96">
      <h1 class="text-3xl font-bold text-emerald-800 mb-6 text-center">GrocerySplit 🛒</h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <input v-model="username" type="text" placeholder="Username" class="w-full p-2 border rounded" required />
        <input v-model="password" type="password" placeholder="Password" class="w-full p-2 border rounded" required />
        <button type="submit" class="w-full bg-emerald-600 text-white p-2 rounded hover:bg-emerald-700">Login</button>
      </form>
      <p v-if="error" class="text-red-500 mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

const handleLogin = async () => {
  error.value = ''
  try {
    const user = await auth.login(username.value, password.value)
    if (user.must_change_password) {
      router.push('/change-password')
    } else if (user.is_admin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } catch (e) {
    error.value = 'Invalid login'
  }
}
</script>

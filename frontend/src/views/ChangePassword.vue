<template>
  <div class="min-h-screen flex items-center justify-center bg-emerald-700">
    <BaseCard class="w-full max-w-md p-8">
      <h1 class="text-2xl font-bold mb-6 text-center">Reset Password</h1>
      <form @submit.prevent="handleReset" class="space-y-4">
        <input type="password" v-model="newPassword" placeholder="New Password" class="w-full p-2 border rounded" required />
        <BaseButton type="submit" class="w-full">Set Password</BaseButton>
      </form>
      <p v-if="error" class="text-red-500 mt-4 text-center">{{ error }}</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../api/axios'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

const newPassword = ref('')
const error = ref('')
const router = useRouter()

const handleReset = async () => {
    try {
        await apiClient.post('/change-password', 
            { new_password: newPassword.value }
        )
        router.push('/dashboard')
    } catch (e: any) {
        error.value = e.response?.data?.detail || 'Failed to update password'
    }
}
</script>

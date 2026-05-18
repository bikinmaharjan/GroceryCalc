import { defineStore } from 'pinia'
import apiClient from '../api/axios'

interface User { username: string; display_name?: string; is_admin: boolean; must_change_password: boolean }

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null') as User | null
  }),
  actions: {
    async login(username: string, password: string) {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      
      const response = await apiClient.post('/login', params)
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      
      this.user = { 
        username, 
        is_admin: response.data.is_admin,
        must_change_password: response.data.must_change_password 
      } 
      localStorage.setItem('user', JSON.stringify(this.user))
      return this.user
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})


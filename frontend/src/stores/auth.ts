import { defineStore } from 'pinia'
import axios from 'axios'

interface User { username: string; is_admin: boolean; must_change_password: boolean }

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
      
      const response = await axios.post('http://localhost:8080/api/login', params)
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      
      this.user = { 
        username, 
        is_admin: username === 'admin',
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


import { defineStore } from 'pinia'
import authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('mes_token') || null,
    user: JSON.parse(localStorage.getItem('mes_user') || 'null'),
    loading: false
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.role || 'VIEWER',
    isAdmin: (state) => state.user?.role === 'ADMIN',
    isManager: (state) => ['ADMIN', 'INVENTORY_MANAGER'].includes(state.user?.role),
    isOperator: (state) => ['ADMIN', 'INVENTORY_MANAGER', 'STORE_OPERATOR'].includes(state.user?.role),
    canModifyStock: (state) => ['ADMIN', 'INVENTORY_MANAGER', 'STORE_OPERATOR'].includes(state.user?.role),
    canReserveStock: (state) => ['ADMIN', 'INVENTORY_MANAGER'].includes(state.user?.role)
  },
  actions: {
    async login(usernameOrEmail, password) {
      this.loading = true
      try {
        const response = await authApi.login(usernameOrEmail, password)
        const { token, user } = response.data
        this.token = token
        this.user = user
        localStorage.setItem('mes_token', token)
        localStorage.setItem('mes_user', JSON.stringify(user))
        return user
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('mes_token')
      localStorage.removeItem('mes_user')
      window.location.href = '/login'
    }
  }
})

import { defineStore } from 'pinia'
import authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('mes_token') || null,
    refreshToken: localStorage.getItem('mes_refresh_token') || null,
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
        const { token, refresh_token, user } = response.data
        this.token = token
        this.refreshToken = refresh_token || null
        this.user = user
        localStorage.setItem('mes_token', token)
        if (refresh_token) {
          localStorage.setItem('mes_refresh_token', refresh_token)
        }
        localStorage.setItem('mes_user', JSON.stringify(user))
        return user
      } finally {
        this.loading = false
      }
    },
    async refreshSession() {
      if (!this.refreshToken) {
        throw new Error('No refresh token available')
      }
      const response = await authApi.refreshToken(this.refreshToken)
      const { token, refresh_token, user } = response.data
      this.token = token
      if (refresh_token) {
        this.refreshToken = refresh_token
        localStorage.setItem('mes_refresh_token', refresh_token)
      }
      if (user) {
        this.user = user
        localStorage.setItem('mes_user', JSON.stringify(user))
      }
      localStorage.setItem('mes_token', token)
      return token
    },
    async logout() {
      if (this.refreshToken) {
        try {
          await authApi.logout(this.refreshToken)
        } catch (e) {
          // Ignore logout error and proceed to local cleanup
        }
      }
      this.token = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('mes_token')
      localStorage.removeItem('mes_refresh_token')
      localStorage.removeItem('mes_user')
      window.location.href = '/login'
    }
  }
})


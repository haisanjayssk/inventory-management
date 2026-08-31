import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Request Interceptor: Attach JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Handle Global Errors & Auth Expiry
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const toast = useToastStore()
    const responseData = error.response?.data
    const status = error.response?.status
    const message = responseData?.message || error.message || 'An unexpected error occurred'

    if (status === 401) {
      const authStore = useAuthStore()
      if (authStore.token) {
        toast.error('Session expired. Please log in again.')
        authStore.logout()
      }
    } else if (status === 403) {
      toast.error('Forbidden: You do not have permission for this action.')
    } else {
      toast.error(message)
    }

    return Promise.reject(responseData || error)
  }
)

export default apiClient

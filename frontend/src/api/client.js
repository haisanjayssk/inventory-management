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

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response Interceptor: Handle Global Errors & Auth Expiry with Silent Refresh
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const toast = useToastStore()
    const originalRequest = error.config || {}
    const responseData = error.response?.data
    const status = error.response?.status
    const message = responseData?.message || error.message || 'An unexpected error occurred'

    // If 401 and not a login or refresh request, attempt silent refresh
    if (
      status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      const authStore = useAuthStore()

      if (authStore.refreshToken) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return apiClient(originalRequest)
            })
            .catch((err) => Promise.reject(err))
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const newToken = await authStore.refreshSession()
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return apiClient(originalRequest)
        } catch (refreshErr) {
          processQueue(refreshErr, null)
          toast.error('Session expired. Please log in again.')
          authStore.logout()
          return Promise.reject(refreshErr)
        } finally {
          isRefreshing = false
        }
      } else {
        toast.error('Session expired. Please log in again.')
        authStore.logout()
      }
    } else if (status === 403) {
      toast.error('Forbidden: You do not have permission for this action.')
    } else if (!originalRequest.url?.includes('/auth/refresh')) {
      toast.error(message)
    }

    return Promise.reject(responseData || error)
  }
)

export default apiClient

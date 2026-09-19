import apiClient from './client'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  getAll(params) {
    return apiClient.get('/items', { params })
  },
  getById(id) {
    return apiClient.get(`/items/${id}`)
  },
  create(data) {
    return apiClient.post('/items', data)
  },
  update(id, data) {
    return apiClient.put(`/items/${id}`, data)
  },
  delete(id) {
    return apiClient.delete(`/items/${id}`)
  },
  downloadTemplate(format = 'csv') {
    const authStore = useAuthStore()
    const baseURL = import.meta.env.VITE_API_URL || '/api/v1'
    return axios.get(`${baseURL}/items/import-template?format=${format}`, {
      headers: authStore.token ? { Authorization: `Bearer ${authStore.token}` } : {},
      responseType: 'blob'
    })
  },
  export(format = 'csv') {
    const authStore = useAuthStore()
    const baseURL = import.meta.env.VITE_API_URL || '/api/v1'
    return axios.get(`${baseURL}/items/export?format=${format}`, {
      headers: authStore.token ? { Authorization: `Bearer ${authStore.token}` } : {},
      responseType: 'blob'
    })
  },
  bulkImport(formData) {
    return apiClient.post('/items/bulk-import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

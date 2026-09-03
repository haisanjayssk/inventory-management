import apiClient from './client'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  getAll(params) {
    return apiClient.get('/parts', { params })
  },
  getById(id) {
    return apiClient.get(`/parts/${id}`)
  },
  create(data) {
    return apiClient.post('/parts', data)
  },
  update(id, data) {
    return apiClient.put(`/parts/${id}`, data)
  },
  delete(id) {
    return apiClient.delete(`/parts/${id}`)
  },
  downloadTemplate(format = 'csv') {
    const authStore = useAuthStore()
    const baseURL = import.meta.env.VITE_API_URL || '/api/v1'
    return axios.get(`${baseURL}/parts/import-template?format=${format}`, {
      headers: authStore.token ? { Authorization: `Bearer ${authStore.token}` } : {},
      responseType: 'blob'
    })
  },
  bulkImport(formData) {
    return apiClient.post('/parts/bulk-import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}


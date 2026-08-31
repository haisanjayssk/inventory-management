import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/transactions', { params })
  },
  getById(id) {
    return apiClient.get(`/transactions/${id}`)
  }
}

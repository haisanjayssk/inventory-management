import apiClient from './client'

export default {
  getAll() {
    return apiClient.get('/vendors')
  },
  getById(id) {
    return apiClient.get(`/vendors/${id}`)
  },
  create(data) {
    return apiClient.post('/vendors', data)
  },
  update(id, data) {
    return apiClient.put(`/vendors/${id}`, data)
  }
}

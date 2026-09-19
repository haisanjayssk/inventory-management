import apiClient from './client'

export default {
  getAll() {
    return apiClient.get('/organizations')
  },
  getById(id) {
    return apiClient.get(`/organizations/${id}`)
  },
  create(data) {
    return apiClient.post('/organizations', data)
  },
  update(id, data) {
    return apiClient.put(`/organizations/${id}`, data)
  }
}

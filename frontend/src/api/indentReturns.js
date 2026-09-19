import apiClient from './client'

export default {
  getAll(params = {}) {
    return apiClient.get('/indent-returns', { params })
  },
  getById(id) {
    return apiClient.get(`/indent-returns/${id}`)
  },
  create(data) {
    return apiClient.post('/indent-returns', data)
  },
  accept(id, data) {
    return apiClient.post(`/indent-returns/${id}/accept`, data)
  }
}

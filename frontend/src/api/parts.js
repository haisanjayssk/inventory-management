import apiClient from './client'

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
  }
}

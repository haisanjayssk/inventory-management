import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/item-types', { params })
  },
  getById(id) {
    return apiClient.get(`/item-types/${id}`)
  },
  create(data) {
    return apiClient.post('/item-types', data)
  },
  update(id, data) {
    return apiClient.put(`/item-types/${id}`, data)
  }
}

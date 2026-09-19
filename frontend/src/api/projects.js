import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/projects', { params })
  },
  getById(id) {
    return apiClient.get(`/projects/${id}`)
  },
  create(data) {
    return apiClient.post('/projects', data)
  },
  update(id, data) {
    return apiClient.put(`/projects/${id}`, data)
  },
  delete(id) {
    return apiClient.delete(`/projects/${id}`)
  }
}

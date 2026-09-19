import apiClient from './client'

export default {
  getAll(params = {}) {
    return apiClient.get('/indents', { params })
  },
  getById(id) {
    return apiClient.get(`/indents/${id}`)
  },
  create(data) {
    return apiClient.post('/indents', data)
  },
  update(id, data) {
    return apiClient.put(`/indents/${id}`, data)
  },
  submit(id) {
    return apiClient.post(`/indents/${id}/submit`)
  },
  approve(id, data = {}) {
    return apiClient.post(`/indents/${id}/approve`, data)
  },
  reject(id, data) {
    return apiClient.post(`/indents/${id}/reject`, data)
  },
  issue(id, data) {
    return apiClient.post(`/indents/${id}/issue`, data)
  },
  close(id, data = {}) {
    return apiClient.post(`/indents/${id}/close`, data)
  }
}

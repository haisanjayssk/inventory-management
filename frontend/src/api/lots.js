import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/lots', { params })
  },
  getById(id) {
    return apiClient.get(`/lots/${id}`)
  },
  create(data) {
    return apiClient.post('/lots', data)
  }
}

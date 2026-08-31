import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/locations', { params })
  },
  getById(id) {
    return apiClient.get(`/locations/${id}`)
  },
  getByCode(code) {
    return apiClient.get(`/locations/code/${code}`)
  },
  getByNfc(nfcUid) {
    return apiClient.get(`/locations/nfc/${encodeURIComponent(nfcUid)}`)
  },
  create(data) {
    return apiClient.post('/locations', data)
  },
  bulkGenerate(data) {
    return apiClient.post('/locations/bulk-generate', data)
  },
  update(id, data) {
    return apiClient.put(`/locations/${id}`, data)
  }
}

import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/cells', { params })
  },
  getById(id) {
    return apiClient.get(`/cells/${id}`)
  },
  getBySerial(serialNo) {
    return apiClient.get(`/cells/serial/${serialNo}`)
  },
  transfer(data) {
    return apiClient.post('/cells/transfer', data)
  }
}

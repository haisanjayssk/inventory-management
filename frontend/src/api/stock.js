import apiClient from './client'

export default {
  receive(data) {
    return apiClient.post('/stock/receive', data)
  },
  issue(data) {
    return apiClient.post('/stock/issue', data)
  },
  transfer(data) {
    return apiClient.post('/stock/transfer', data)
  },
  reserve(data) {
    return apiClient.post('/stock/reserve', data)
  },
  release(data) {
    return apiClient.post('/stock/release', data)
  }
}

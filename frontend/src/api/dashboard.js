import apiClient from './client'

export default {
  getMetrics() {
    return apiClient.get('/dashboard/metrics')
  }
}

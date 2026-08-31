import apiClient from './client'

export default {
  getAll(params) {
    return apiClient.get('/inventory', { params })
  },
  getByPart(partId) {
    return apiClient.get(`/inventory/part/${partId}`)
  },
  getByLocation(locationId) {
    return apiClient.get(`/inventory/location/${locationId}`)
  }
}

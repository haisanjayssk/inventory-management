import apiClient from './client'

export default {
  getStockByPart() {
    return apiClient.get('/reports/stock-by-part')
  },
  getLocationOccupancy() {
    return apiClient.get('/reports/location-occupancy')
  }
}

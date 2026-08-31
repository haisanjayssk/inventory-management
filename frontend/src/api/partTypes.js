import apiClient from './client'

export default {
  getAll() {
    return apiClient.get('/part-types')
  },
  getById(id) {
    return apiClient.get(`/part-types/${id}`)
  },
  create(data) {
    return apiClient.post('/part-types', data)
  },
  update(id, data) {
    return apiClient.put(`/part-types/${id}`, data)
  },
  addField(typeId, fieldData) {
    return apiClient.post(`/part-types/${typeId}/fields`, fieldData)
  },
  deleteField(fieldId) {
    return apiClient.delete(`/part-types/fields/${fieldId}`)
  }
}

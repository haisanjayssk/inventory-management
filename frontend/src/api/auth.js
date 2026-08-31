import apiClient from './client'

export default {
  login(username_or_email, password) {
    return apiClient.post('/auth/login', { username_or_email, password })
  },
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },
  getMe() {
    return apiClient.get('/auth/me')
  }
}

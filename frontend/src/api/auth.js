import apiClient from './client'

export default {
  login(username_or_email, password) {
    return apiClient.post('/auth/login', { username_or_email, password })
  },
  refreshToken(refresh_token) {
    return apiClient.post('/auth/refresh', { refresh_token })
  },
  logout(refresh_token) {
    return apiClient.post('/auth/logout', { refresh_token })
  },
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },

  getMe() {
    return apiClient.get('/auth/me')
  },
  getAllUsers(params) {
    return apiClient.get('/auth/users', { params })
  },
  getUser(userId) {
    return apiClient.get(`/auth/users/${userId}`)
  },
  updateUser(userId, data) {
    return apiClient.put(`/auth/users/${userId}`, data)
  },
  resetPassword(userId, newPassword) {
    return apiClient.put(`/auth/users/${userId}/password`, { new_password: newPassword })
  },
  deleteUser(userId) {
    return apiClient.delete(`/auth/users/${userId}`)
  }
}


import api from './api'

export const authService = {
  login: (credentials) => {
    const form = new URLSearchParams()
    form.append('username', credentials.email)
    form.append('password', credentials.password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  logout:       ()            => api.post('/auth/logout'),
  me:           ()            => api.get('/auth/me'),
  refreshToken: ()            => api.post('/auth/refresh'),
  forgotPassword: (email)     => api.post('/auth/forgot-password', { email }),
  resetPassword:  (payload)   => api.post('/auth/reset-password', payload)
}

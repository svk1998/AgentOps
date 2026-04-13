import api from './api'
import { useAuthStore } from '@/stores/auth'

// ── Request: attach auth token automatically ──
api.interceptors.request.use(
  (config) => {
    const auth = useAuthStore()
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response: handle common errors globally ──
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      // Token expired or invalid — log out and redirect to login
      const auth = useAuthStore()
      auth.logout()
    }

    if (status === 403) {
      console.warn('Access forbidden:', error.config?.url)
    }

    if (status >= 500) {
      console.error('Server error:', error.response?.data?.message || 'Unknown server error')
    }

    return Promise.reject(error)
  }
)

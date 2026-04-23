import api from './api'

/**
 * Users — wraps /api/v1/users (admin-only for list/create/delete/reactivate,
 * self-or-admin for get/update).
 */
export const userService = {
  list:       (params = {})   => api.get('/users', { params }),
  get:        (id)            => api.get(`/users/${id}`),
  create:     (payload)       => api.post('/users', payload),
  update:     (id, payload)   => api.patch(`/users/${id}`, payload),
  remove:     (id)            => api.delete(`/users/${id}`),
  reactivate: (id)            => api.post(`/users/${id}/reactivate`),

  // Aliases retained for backwards-compat with older views
  getAll:     (params)        => api.get('/users', { params }),
  getById:    (id)            => api.get(`/users/${id}`),
  delete:     (id)            => api.delete(`/users/${id}`),
}

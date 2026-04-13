import api from './api'

export const userService = {
  getAll:   (params)       => api.get('/users', { params }),
  getById:  (id)           => api.get(`/users/${id}`),
  create:   (payload)      => api.post('/users', payload),
  update:   (id, payload)  => api.put(`/users/${id}`, payload),
  delete:   (id)           => api.delete(`/users/${id}`),
  updateRole: (id, role)   => api.patch(`/users/${id}/role`, { role })
}

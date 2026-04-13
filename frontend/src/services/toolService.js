import api from './api'

export const toolService = {
  getAll:   (params)      => api.get('/tools', { params }),
  getById:  (id)          => api.get(`/tools/${id}`),
  create:   (payload)     => api.post('/tools', payload),
  update:   (id, payload) => api.patch(`/tools/${id}`, payload),
  delete:   (id)          => api.delete(`/tools/${id}`),
}

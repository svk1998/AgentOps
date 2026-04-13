import api from './api'

export const agentService = {
  getAll:  (params)      => api.get('/agents', { params }),
  getById: (id)          => api.get(`/agents/${id}`),
  create:  (payload)     => api.post('/agents', payload),
  update:  (id, payload) => api.patch(`/agents/${id}`, payload),
  delete:  (id)          => api.delete(`/agents/${id}`),
}

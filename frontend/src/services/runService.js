import api from './api'

export const runService = {
  getAll:   (params)      => api.get('/runs', { params }),
  getById:  (id)          => api.get(`/runs/${id}`),
  getLogs:  (id)          => api.get(`/runs/${id}/logs`),
  trigger:  (payload)     => api.post('/runs', payload),
  cancel:   (id)          => api.post(`/runs/${id}/cancel`),
}

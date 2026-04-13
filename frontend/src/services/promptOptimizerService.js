import api from './api'

export const promptOptimizerService = {
  getRuns:     (params)      => api.get('/prompt-optimizer/runs', { params }),
  getRunById:  (id)          => api.get(`/prompt-optimizer/runs/${id}`),
  createRun:   (payload)     => api.post('/prompt-optimizer/runs', payload),
  stopRun:     (id)          => api.post(`/prompt-optimizer/runs/${id}/stop`),
  deleteRun:   (id)          => api.delete(`/prompt-optimizer/runs/${id}`),
}

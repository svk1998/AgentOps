import api from './api'

/**
 * Evaluation Runs — wraps /api/v1/eval-runs
 */
export const evalRunService = {
  list:     (params = {})            => api.get('/eval-runs', { params }),
  get:      (id)                     => api.get(`/eval-runs/${id}`),
  create:   (payload)                => api.post('/eval-runs', payload),
  cancel:   (id)                     => api.post(`/eval-runs/${id}/cancel`),
  results:  (id, params = {})        => api.get(`/eval-runs/${id}/results`, { params }),
  addResult:(id, payload)            => api.post(`/eval-runs/${id}/results`, payload),
}

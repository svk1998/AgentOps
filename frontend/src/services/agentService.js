import api from './api'

/**
 * Agent Registry — wraps /api/v1/agents
 * Response: AgentOut[] or AgentOut
 */
export const agentService = {
  list:     (params = {})    => api.get('/agents', { params }),
  get:      (id)             => api.get(`/agents/${id}`),
  create:   (payload)        => api.post('/agents', payload),
  update:   (id, payload)    => api.patch(`/agents/${id}`, payload),
  remove:   (id)             => api.delete(`/agents/${id}`),
  versions: (id)             => api.get(`/agents/${id}/versions`),

  // Aliases retained for backwards-compat with older views
  getAll:   (params)         => api.get('/agents', { params }),
  getById:  (id)             => api.get(`/agents/${id}`),
  delete:   (id)             => api.delete(`/agents/${id}`),
}

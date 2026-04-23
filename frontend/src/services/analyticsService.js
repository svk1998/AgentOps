import api from './api'

/**
 * Analytics — wraps /api/v1/analytics
 */
export const analyticsService = {
  accuracyTrend:  (agentId)                   => api.get(`/analytics/agents/${agentId}/accuracy-trend`),
  fieldAccuracy:  (agentId)                   => api.get(`/analytics/agents/${agentId}/field-accuracy`),
  latency:        (agentId)                   => api.get(`/analytics/agents/${agentId}/latency`),
  regressions:    (agentId, thresholdPct = 5) => api.get(`/analytics/agents/${agentId}/regressions`, { params: { threshold_pct: thresholdPct } }),
  compare:        (agentIds)                  => api.get('/analytics/compare', { params: { agent_ids: agentIds } }),
}

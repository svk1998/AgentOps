import api from './api'

export const statsService = {
  getSummary:       ()           => api.get('/stats/summary'),
  getRunsTimeline:  (days = 7)   => api.get('/stats/runs-timeline',  { params: { days } }),
  getTokenTimeline: (days = 7)   => api.get('/stats/token-timeline', { params: { days } }),
}

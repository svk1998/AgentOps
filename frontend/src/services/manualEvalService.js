import api from './api'

/**
 * Manual / Human-in-the-loop Evaluation — wraps /api/v1/manual-eval
 */
export const manualEvalService = {
  createSession: (payload)                   => api.post('/manual-eval/sessions', payload),
  getSession:    (id)                        => api.get(`/manual-eval/sessions/${id}`),
  nextItem:      (sessionId)                 => api.get(`/manual-eval/queue/${sessionId}`),
  submitReview:  (sessionId, itemId, body)   => api.post(`/manual-eval/sessions/${sessionId}/items/${itemId}/review`, body),
}

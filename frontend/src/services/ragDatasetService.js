import api from './api'

/**
 * RAG Datasets — wraps /api/v1/rag-datasets
 */
export const ragDatasetService = {
  list:   (params = {})      => api.get('/rag-datasets', { params }),
  get:    (id)               => api.get(`/rag-datasets/${id}`),
  create: (payload)          => api.post('/rag-datasets', payload),
  sync:   (id, payload = {}) => api.post(`/rag-datasets/${id}/sync`, payload),
}

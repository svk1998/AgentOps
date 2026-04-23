import api from './api'

/**
 * Evaluation Datasets — wraps /api/v1/datasets
 */
export const datasetService = {
  list:       (params = {})       => api.get('/datasets', { params }),
  get:        (id)                => api.get(`/datasets/${id}`),
  create:     (payload)           => api.post('/datasets', payload),
  update:     (id, payload)       => api.patch(`/datasets/${id}`, payload),
  remove:     (id)                => api.delete(`/datasets/${id}`),

  // Items
  addItems:   (id, items)         => api.post(`/datasets/${id}/items`, items),
  updateItem: (id, itemId, body)  => api.patch(`/datasets/${id}/items/${itemId}`, body),
  removeItem: (id, itemId)        => api.delete(`/datasets/${id}/items/${itemId}`),

  // Bulk
  import:     (id, payload)       => api.post(`/datasets/${id}/import`, payload),
  export:     (id, format = 'json') => api.get(`/datasets/${id}/export`, { params: { format } }),

  // Versioning
  snapshot:   (id, notes)         => api.post(`/datasets/${id}/snapshot`, { notes }),
  versions:   (id)                => api.get(`/datasets/${id}/versions`),
}

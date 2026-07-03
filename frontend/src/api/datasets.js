import { apiClient } from './client'

export const datasetsApi = {
  list: () => apiClient.get('/datasets').then((r) => r.data),

  get: (id) => apiClient.get(`/datasets/${id}`).then((r) => r.data),

  preview: (id, rows = 20) =>
    apiClient.get(`/datasets/${id}/preview`, { params: { rows } }).then((r) => r.data),

  upload: (file, name, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    return apiClient
      .post('/datasets', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: onProgress
          ? (evt) => onProgress(Math.round((evt.loaded / evt.total) * 100))
          : undefined,
      })
      .then((r) => r.data)
  },

  fetchFromTwelvedata: (params) => apiClient.post('/datasets/twelvedata', params).then((r) => r.data),

  remove: (id) => apiClient.delete(`/datasets/${id}`),
}

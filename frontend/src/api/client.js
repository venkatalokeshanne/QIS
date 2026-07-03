import axios from 'axios'

// Single axios instance for the whole app. Vite's dev server proxies
// /api to the FastAPI backend (see vite.config.js), so no base URL is
// needed here — this also makes the built app work unmodified behind
// any reverse proxy that forwards /api the same way.
export const apiClient = axios.create({
  baseURL: '/api',
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || 'An unexpected error occurred.'
    const wrapped = new Error(message)
    wrapped.issues = error.response?.data?.issues
    return Promise.reject(wrapped)
  }
)

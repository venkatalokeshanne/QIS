import axios from 'axios'
import Constants from 'expo-constants'

// Single axios instance for the whole app. Unlike the web frontend
// (which uses a relative '/api' baseURL behind Vite's dev proxy /
// Vercel's rewrite), React Native has no reverse proxy to lean on, so
// this points directly at the deployed backend (see app.config.js's
// extra.apiBaseUrl).
export const apiClient = axios.create({
  baseURL: Constants.expoConfig.extra.apiBaseUrl,
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

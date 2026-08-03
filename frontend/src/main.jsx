import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import './styles/global.css'

// Modern iOS Safari and Chrome ignore the viewport meta's
// user-scalable=no for accessibility reasons, so pinch- and
// double-tap-zoom have to be blocked at the touch-event level instead.
document.addEventListener('gesturestart', (e) => e.preventDefault())
document.addEventListener(
  'touchmove',
  (e) => {
    if (e.touches.length > 1) e.preventDefault()
  },
  { passive: false }
)
let lastTouchEnd = 0
document.addEventListener(
  'touchend',
  (e) => {
    const now = Date.now()
    if (now - lastTouchEnd <= 300) e.preventDefault()
    lastTouchEnd = now
  },
  { passive: false }
)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)

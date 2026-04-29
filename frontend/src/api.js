import axios from 'axios'
import { supabase, supabaseConfigured } from './auth/supabaseClient'

// Dev: Vite proxies /api → localhost:8000
// Prod: set VITE_API_URL=https://your-backend.railway.app
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api',
})

// Attach Supabase access token to every outgoing request when configured.
api.interceptors.request.use(async (config) => {
  if (!supabaseConfigured) return config
  const { data } = await supabase.auth.getSession()
  const token = data?.session?.access_token
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
}

export const shipmentsApi = {
  getAll: (params) => api.get('/shipments/', { params }),
  getOne: (shipmentId) => api.get(`/shipments/${shipmentId}`),
}

export const carriersApi = {
  getAll: () => api.get('/carriers/'),
}

export const routesApi = {
  getAll: () => api.get('/routes/'),
}

export const deliveriesApi = {
  getAll: (params) => api.get('/deliveries/', { params }),
  getSummary: () => api.get('/deliveries/summary'),
}

export const anomaliesApi = {
  getAll: (params) => api.get('/anomalies/', { params }),
  getSummary: () => api.get('/anomalies/summary'),
}

export const predictionsApi = {
  getAll: (params) => api.get('/predictions/', { params }),
  getSummary: () => api.get('/predictions/summary'),
}

export const etaApi = {
  getAll: (params) => api.get('/eta/', { params }),
  getOne: (shipmentId) => api.get(`/eta/${shipmentId}`),
  getSummary: () => api.get('/eta/summary'),
}

export const billingApi = {
  listTiers: () => api.get('/billing/tiers'),
  getSubscription: () => api.get('/billing/subscription'),
  checkout: (tier) => api.post('/billing/checkout', { tier }),
  portal: () => api.post('/billing/portal'),
}

export const notificationsApi = {
  welcome: (email, name) => api.post('/notifications/welcome', { email, name }),
  resetPassword: (email, reset_link) => api.post('/notifications/password-reset', { email, reset_link }),
  shipmentUpdate: (email, shipment_id) => api.post('/notifications/shipment-update', { email, shipment_id }),
}

export default api

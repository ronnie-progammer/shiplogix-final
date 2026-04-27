import axios from 'axios'

// Dev: Vite proxies /api → localhost:8000
// Prod: set VITE_API_URL=https://your-backend.railway.app
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api',
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

export default api

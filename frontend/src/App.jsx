import { Routes, Route, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Shipments from './pages/Shipments'
import Carriers from './pages/Carriers'
import RoutesPage from './pages/Routes'
import Anomalies from './pages/Anomalies'
import Predictions from './pages/Predictions'
import TrackShipment from './pages/TrackShipment'
import RouteOptimizer from './pages/RouteOptimizer'
import Defense from './pages/Defense'
import Carbon from './pages/Carbon'
import Billing from './pages/Billing'
import Login from './auth/Login'
import Signup from './auth/Signup'
import ResetPassword from './auth/ResetPassword'
import RequireAuth from './auth/RequireAuth'

function PrivateLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0f1a]">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/shipments" element={<Shipments />} />
            <Route path="/carriers" element={<Carriers />} />
            <Route path="/routes" element={<RoutesPage />} />
            <Route path="/anomalies" element={<Anomalies />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/optimizer" element={<RouteOptimizer />} />
            <Route path="/defense" element={<Defense />} />
            <Route path="/carbon" element={<Carbon />} />
            <Route path="/billing" element={<Billing />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

const PUBLIC_PREFIXES = ['/track', '/login', '/signup', '/reset-password']

export default function App() {
  const { pathname } = useLocation()
  const isPublic = PUBLIC_PREFIXES.some((p) => pathname.startsWith(p))

  if (isPublic) {
    return (
      <Routes>
        <Route path="/track" element={<TrackShipment />} />
        <Route path="/track/:id" element={<TrackShipment />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/reset-password" element={<ResetPassword />} />
      </Routes>
    )
  }

  return (
    <RequireAuth>
      <PrivateLayout />
    </RequireAuth>
  )
}

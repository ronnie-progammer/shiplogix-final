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
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  const { pathname } = useLocation()
  const isPublic = pathname.startsWith('/track')

  if (isPublic) {
    return (
      <Routes>
        <Route path="/track" element={<TrackShipment />} />
        <Route path="/track/:id" element={<TrackShipment />} />
      </Routes>
    )
  }

  return <PrivateLayout />
}

import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Shipments from './pages/Shipments'
import Carriers from './pages/Carriers'
import RoutesPage from './pages/Routes'
import Anomalies from './pages/Anomalies'
import Predictions from './pages/Predictions'

export default function App() {
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
          </Routes>
        </main>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL ?? ''

const STATUS_COLOR = {
  in_transit: 'text-blue-400',
  delayed:    'text-yellow-400',
  at_risk:    'text-orange-400',
  delivered:  'text-emerald-400',
}

const RISK_COLOR = {
  High:   'bg-red-500/20 text-red-400 border-red-500/30',
  Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  Low:    'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
}

export default function TrackShipment() {
  const { id: routeId } = useParams()
  const navigate = useNavigate()
  const [query, setQuery] = useState(routeId ?? '')
  const [data, setData]   = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (routeId) fetchShipment(routeId)
  }, [routeId])

  async function fetchShipment(shipmentId) {
    if (!shipmentId.trim()) return
    setLoading(true)
    setError('')
    setData(null)
    try {
      const res = await axios.get(`${BASE}/track/${shipmentId.trim().toUpperCase()}`)
      setData(res.data)
    } catch (e) {
      setError(e.response?.status === 404 ? 'Shipment not found.' : 'Something went wrong. Try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e) {
    e.preventDefault()
    navigate(`/track/${query.trim().toUpperCase()}`, { replace: true })
    fetchShipment(query)
  }

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white flex flex-col">
      {/* Brand header */}
      <header className="bg-[#0f1923] border-b border-[#1e2a3a] px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 bg-[#10b981]/10 border border-[#10b981]/30 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-[#10b981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-semibold tracking-wide">ShipLogiz</div>
          <div className="text-[10px] text-[#10b981] tracking-widest uppercase">Track Your Shipment</div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 py-12 gap-8">
        {/* Search form */}
        <form onSubmit={handleSearch} className="w-full max-w-lg flex gap-2">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Enter shipment ID (e.g. SHP-001)"
            className="flex-1 bg-[#0f1923] border border-[#1e2a3a] rounded-lg px-4 py-2.5 text-sm
                       text-white placeholder-[#8b9ab0] focus:outline-none focus:border-[#10b981]/60"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-[#10b981] hover:bg-[#0ea472] disabled:opacity-50
                       text-black text-sm font-semibold rounded-lg transition-colors"
          >
            {loading ? 'Searching…' : 'Track'}
          </button>
        </form>

        {error && (
          <div className="w-full max-w-lg bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {data && (
          <div className="w-full max-w-lg space-y-4">
            {/* Header card */}
            <div className="bg-[#0f1923] border border-[#1e2a3a] rounded-xl p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-xs text-[#8b9ab0] uppercase tracking-widest">Shipment</div>
                  <div className="text-lg font-bold font-mono">{data.shipment_id}</div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={`text-sm font-semibold capitalize ${STATUS_COLOR[data.status] ?? 'text-gray-300'}`}>
                    {data.status.replace('_', ' ')}
                  </span>
                  {data.risk_label && (
                    <span className={`text-[10px] px-2 py-0.5 rounded border font-medium ${RISK_COLOR[data.risk_label]}`}>
                      {data.risk_label} Risk
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <InfoRow label="Carrier"  value={data.carrier} />
                <InfoRow label="Origin"   value={data.origin} />
                <InfoRow label="Destination" value={data.destination} />
                <InfoRow label="Shipped"  value={data.ship_date} />
                <InfoRow label="Est. Arrival" value={data.estimated_arrival} />
                {data.actual_arrival && (
                  <InfoRow label="Delivered" value={data.actual_arrival} />
                )}
                {data.delay_hours > 0 && (
                  <InfoRow label="Delay" value={`${data.delay_hours}h`} highlight />
                )}
              </div>
            </div>

            {/* AI ETA prediction */}
            {data.eta && data.eta.predicted_eta && (
              <div className="bg-[#0f1923] border border-[#10b981]/30 rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-xs text-[#10b981] uppercase tracking-widest">
                    AI Predicted Arrival
                  </div>
                  <span className="text-[10px] text-[#8b9ab0]">95% confidence</span>
                </div>
                <div className="text-xl font-semibold text-emerald-300">
                  {data.eta.predicted_eta}
                </div>
                <div className="text-xs text-[#8b9ab0] mt-1">
                  Window: {data.eta.predicted_eta_lower} → {data.eta.predicted_eta_upper}
                  <span className="ml-2 text-[#5d6f87]">±{data.eta.eta_confidence_hours}h</span>
                </div>
              </div>
            )}

            {/* Timeline */}
            <div className="bg-[#0f1923] border border-[#1e2a3a] rounded-xl p-5">
              <div className="text-xs text-[#8b9ab0] uppercase tracking-widest mb-4">Timeline</div>
              <ol className="relative border-l border-[#1e2a3a] space-y-5 ml-2">
                {data.timeline.map((step, i) => (
                  <li key={i} className="ml-4">
                    <span className={`absolute -left-1.5 mt-1 w-3 h-3 rounded-full border-2 transition-colors
                      ${step.done
                        ? 'bg-[#10b981] border-[#10b981]'
                        : 'bg-[#0f1923] border-[#1e2a3a]'}`}
                    />
                    <p className={`text-sm ${step.done ? 'text-white font-medium' : 'text-[#8b9ab0]'}`}>
                      {step.step}
                    </p>
                  </li>
                ))}
              </ol>
            </div>

            {data.is_anomaly && (
              <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg px-4 py-3 text-sm text-orange-400">
                This shipment has been flagged for review by our AI anomaly detection system.
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="text-center text-[10px] text-[#8b9ab0] py-4 border-t border-[#1e2a3a]">
        Powered by ShipLogiz &mdash; Supply Chain Visibility
      </footer>
    </div>
  )
}

function InfoRow({ label, value, highlight }) {
  return (
    <div>
      <div className="text-[10px] text-[#8b9ab0] uppercase tracking-wide">{label}</div>
      <div className={`text-sm font-medium mt-0.5 ${highlight ? 'text-yellow-400' : 'text-gray-200'}`}>
        {value}
      </div>
    </div>
  )
}

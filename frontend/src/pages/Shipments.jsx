import { useState, useEffect, useCallback } from 'react'
import { shipmentsApi, etaApi } from '../api'

const CARRIERS = [
  'All', 'FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics',
  'OnTrac', 'LaserShip', 'Speedy Freight', 'NationWide Carriers', 'PrimeShip',
]

function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{status.replace('_', ' ')}</span>
}

function RiskBadge({ label }) {
  if (!label) return null
  return <span className={`badge risk-${label}`}>{label}</span>
}

function formatEta(dt) {
  if (!dt) return '—'
  return dt.replace(' ', ' · ')
}

export default function Shipments() {
  const [shipments, setShipments] = useState([])
  const [etaMap, setEtaMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ status: '', carrier: '', risk_label: '' })
  const [selected, setSelected] = useState(null)
  const [selectedEta, setSelectedEta] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    const params = {}
    if (filters.status) params.status = filters.status
    if (filters.carrier && filters.carrier !== 'All') params.carrier = filters.carrier
    if (filters.risk_label) params.risk_label = filters.risk_label
    params.limit = 200
    shipmentsApi.getAll(params)
      .then((r) => { setShipments(r.data); setLoading(false) })
      .catch(() => setLoading(false))

    etaApi.getAll({ limit: 500 })
      .then((r) => {
        const map = {}
        for (const row of r.data) {
          map[row.shipment_id] = row
        }
        setEtaMap(map)
      })
      .catch(() => setEtaMap({}))
  }, [filters])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (!selected) { setSelectedEta(null); return }
    if (selected.status === 'delivered') { setSelectedEta(null); return }
    let cancelled = false
    etaApi.getOne(selected.shipment_id)
      .then((r) => { if (!cancelled) setSelectedEta(r.data) })
      .catch(() => { if (!cancelled) setSelectedEta(null) })
    return () => { cancelled = true }
  }, [selected])

  const setFilter = (key, val) => setFilters((f) => ({ ...f, [key]: val }))

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-white">Shipments</h1>
          <p className="text-xs text-[#8b9ab0] mt-0.5">{shipments.length} records</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-3 flex flex-wrap gap-3 items-center">
        <select className="select text-xs" value={filters.status} onChange={(e) => setFilter('status', e.target.value)}>
          <option value="">All Statuses</option>
          <option value="in_transit">In Transit</option>
          <option value="delayed">Delayed</option>
          <option value="at_risk">At Risk</option>
          <option value="delivered">Delivered</option>
        </select>
        <select className="select text-xs" value={filters.carrier} onChange={(e) => setFilter('carrier', e.target.value)}>
          {CARRIERS.map((c) => <option key={c} value={c === 'All' ? '' : c}>{c}</option>)}
        </select>
        <select className="select text-xs" value={filters.risk_label} onChange={(e) => setFilter('risk_label', e.target.value)}>
          <option value="">All Risk Levels</option>
          <option value="High">High Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="Low">Low Risk</option>
        </select>
        <button className="btn-secondary text-xs" onClick={() => setFilters({ status: '', carrier: '', risk_label: '' })}>
          Clear
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Table */}
        <div className={`card ${selected ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          {loading ? (
            <div className="p-8 text-center text-[#8b9ab0] text-sm">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
                    <th className="text-left px-4 py-2">ID</th>
                    <th className="text-left px-4 py-2 hidden lg:table-cell">Route</th>
                    <th className="text-left px-4 py-2">Carrier</th>
                    <th className="text-left px-4 py-2">Status</th>
                    <th className="text-right px-4 py-2">Delay (h)</th>
                    <th className="text-left px-4 py-2">Risk</th>
                    <th className="text-left px-4 py-2 hidden xl:table-cell">Est. Arrival</th>
                    <th className="text-left px-4 py-2 hidden xl:table-cell">Predicted ETA</th>
                  </tr>
                </thead>
                <tbody>
                  {shipments.map((s) => {
                    const eta = etaMap[s.shipment_id]
                    return (
                      <tr
                        key={s.id}
                        className={`table-row ${selected?.id === s.id ? 'bg-[#111b2a]' : ''}`}
                        onClick={() => setSelected(selected?.id === s.id ? null : s)}
                      >
                        <td className="px-4 py-2.5 font-mono text-xs text-gray-300">{s.shipment_id}</td>
                        <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden lg:table-cell truncate max-w-[180px]">
                          {s.origin.split(',')[0]} → {s.destination.split(',')[0]}
                        </td>
                        <td className="px-4 py-2.5 text-[#8b9ab0] text-xs">{s.carrier}</td>
                        <td className="px-4 py-2.5"><StatusBadge status={s.status} /></td>
                        <td className={`px-4 py-2.5 text-right text-xs ${s.delay_hours > 0 ? 'text-amber-400' : 'text-[#8b9ab0]'}`}>
                          {s.delay_hours}
                        </td>
                        <td className="px-4 py-2.5"><RiskBadge label={s.risk_label} /></td>
                        <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden xl:table-cell">{s.estimated_arrival}</td>
                        <td className="px-4 py-2.5 text-xs hidden xl:table-cell">
                          {s.status === 'delivered'
                            ? <span className="text-[#8b9ab0]">—</span>
                            : eta?.predicted_eta
                              ? (
                                <span className="text-emerald-300">
                                  {formatEta(eta.predicted_eta)}
                                  <span className="text-[#5d6f87] ml-1">±{eta.eta_confidence_hours}h</span>
                                </span>
                              )
                              : <span className="text-[#5d6f87]">predicting…</span>}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              {shipments.length === 0 && (
                <div className="p-8 text-center text-[#8b9ab0] text-sm">No shipments match the current filters.</div>
              )}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="card p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">{selected.shipment_id}</h3>
              <button onClick={() => setSelected(null)} className="text-[#8b9ab0] hover:text-white text-xs">✕</button>
            </div>
            <div className="space-y-2 text-xs">
              {[
                ['Origin', selected.origin],
                ['Destination', selected.destination],
                ['Carrier', selected.carrier],
                ['Status', null],
                ['Ship Date', selected.ship_date],
                ['Est. Arrival', selected.estimated_arrival],
                ['Actual Arrival', selected.actual_arrival || '—'],
                ['Delay', `${selected.delay_hours}h`],
                ['Transit Days', selected.transit_days],
                ['Weather Region', selected.weather_region],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between">
                  <span className="text-[#8b9ab0]">{label}</span>
                  {label === 'Status'
                    ? <StatusBadge status={selected.status} />
                    : <span className="text-gray-300 text-right max-w-[60%] truncate">{value}</span>
                  }
                </div>
              ))}
            </div>
            <div className="pt-2 border-t border-[#1e2a3a] space-y-2 text-xs">
              <div className="text-[#8b9ab0] font-semibold uppercase tracking-wide text-[10px]">AI Insights</div>
              <div className="flex justify-between">
                <span className="text-[#8b9ab0]">Delay Risk Score</span>
                <span className="text-white">{selected.delay_risk_score != null ? (selected.delay_risk_score * 100).toFixed(1) + '%' : '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#8b9ab0]">Risk Label</span>
                <RiskBadge label={selected.risk_label} />
              </div>
              <div className="flex justify-between">
                <span className="text-[#8b9ab0]">Anomaly Flag</span>
                <span className={selected.is_anomaly ? 'text-red-400' : 'text-emerald-400'}>
                  {selected.is_anomaly ? 'Flagged' : 'Normal'}
                </span>
              </div>
            </div>

            {selected.status !== 'delivered' && (
              <div className="pt-2 border-t border-[#1e2a3a] space-y-2 text-xs">
                <div className="text-[#8b9ab0] font-semibold uppercase tracking-wide text-[10px]">
                  ETA Prediction
                </div>
                {selectedEta ? (
                  <>
                    <div className="flex justify-between">
                      <span className="text-[#8b9ab0]">Predicted Arrival</span>
                      <span className="text-emerald-300">{formatEta(selectedEta.predicted_eta)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#8b9ab0]">95% CI Lower</span>
                      <span className="text-gray-300">{formatEta(selectedEta.predicted_eta_lower)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#8b9ab0]">95% CI Upper</span>
                      <span className="text-gray-300">{formatEta(selectedEta.predicted_eta_upper)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#8b9ab0]">Confidence Band</span>
                      <span className="text-gray-300">±{selectedEta.eta_confidence_hours}h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#8b9ab0]">Model</span>
                      <span className={selectedEta.model_ready ? 'text-emerald-400' : 'text-amber-400'}>
                        {selectedEta.model_ready ? 'RandomForest · ready' : 'fallback'}
                      </span>
                    </div>
                  </>
                ) : (
                  <div className="text-[#5d6f87]">Loading prediction…</div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

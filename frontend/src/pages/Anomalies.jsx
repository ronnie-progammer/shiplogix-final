import { useState, useEffect } from 'react'
import { anomaliesApi } from '../api'

function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{status.replace('_', ' ')}</span>
}

function RiskBadge({ label }) {
  if (!label) return null
  return <span className={`badge risk-${label}`}>{label}</span>
}

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    Promise.all([
      anomaliesApi.getAll({ limit: 200 }),
      anomaliesApi.getSummary(),
    ]).then(([listRes, sumRes]) => {
      setAnomalies(listRes.data)
      setSummary(sumRes.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-[#8b9ab0]">Running anomaly detection...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-white">Anomaly Detection</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">IsolationForest flags statistically unusual shipment patterns</p>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Total Anomalies</div>
            <div className="text-3xl font-bold text-red-400">{summary.total_anomalies}</div>
          </div>
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Anomaly Rate</div>
            <div className="text-3xl font-bold text-amber-400">{summary.anomaly_rate}%</div>
          </div>
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Model</div>
            <div className="text-sm font-semibold text-[#10b981] mt-1">IsolationForest</div>
            <div className="text-[10px] text-[#8b9ab0]">contamination=0.08</div>
          </div>
        </div>
      )}

      {/* By carrier breakdown */}
      {summary?.by_carrier?.length > 0 && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Anomalies by Carrier</h3>
          <div className="space-y-2">
            {summary.by_carrier.slice(0, 6).map((c) => {
              const max = summary.by_carrier[0].count
              return (
                <div key={c.carrier} className="flex items-center gap-3 text-xs">
                  <span className="text-[#8b9ab0] w-36 truncate">{c.carrier}</span>
                  <div className="flex-1 bg-[#162032] rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-red-500/70"
                      style={{ width: `${(c.count / max) * 100}%` }}
                    />
                  </div>
                  <span className="text-red-400 w-6 text-right">{c.count}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Anomaly table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className={`card ${selected ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          <div className="px-4 py-3 border-b border-[#1e2a3a] flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Flagged Shipments</h3>
            <span className="text-xs text-red-400 bg-red-900/20 border border-red-700/30 px-2 py-0.5 rounded">
              {anomalies.length} anomalies
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
                  <th className="text-left px-4 py-2">Shipment</th>
                  <th className="text-left px-4 py-2 hidden md:table-cell">Carrier</th>
                  <th className="text-left px-4 py-2">Status</th>
                  <th className="text-right px-4 py-2">Delay (h)</th>
                  <th className="text-left px-4 py-2">Risk</th>
                  <th className="text-left px-4 py-2 hidden lg:table-cell">Route</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.map((a) => (
                  <tr
                    key={a.id}
                    className={`table-row ${selected?.id === a.id ? 'bg-[#111b2a]' : ''}`}
                    onClick={() => setSelected(selected?.id === a.id ? null : a)}
                  >
                    <td className="px-4 py-2.5 font-mono text-xs text-gray-300">{a.shipment_id}</td>
                    <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden md:table-cell">{a.carrier}</td>
                    <td className="px-4 py-2.5"><StatusBadge status={a.status} /></td>
                    <td className="px-4 py-2.5 text-right text-amber-400 text-xs font-semibold">{a.delay_hours}</td>
                    <td className="px-4 py-2.5"><RiskBadge label={a.risk_label} /></td>
                    <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden lg:table-cell truncate max-w-[160px]">
                      {a.origin?.split(',')[0]} → {a.destination?.split(',')[0]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-white">{selected.shipment_id}</span>
              <button onClick={() => setSelected(null)} className="text-[#8b9ab0] hover:text-white text-xs">✕</button>
            </div>
            <div className="px-2 py-1.5 bg-red-900/20 border border-red-700/30 rounded text-xs text-red-400">
              Flagged as anomaly by IsolationForest
            </div>
            <div className="space-y-2 text-xs">
              {[
                ['Origin', selected.origin],
                ['Destination', selected.destination],
                ['Carrier', selected.carrier],
                ['Delay', `${selected.delay_hours}h`],
                ['Transit Days', selected.transit_days],
                ['Weather Region', selected.weather_region],
                ['Risk Score', selected.delay_risk_score != null ? (selected.delay_risk_score * 100).toFixed(1) + '%' : '—'],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between">
                  <span className="text-[#8b9ab0]">{label}</span>
                  <span className="text-gray-300">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  ScatterChart, Scatter, ZAxis,
} from 'recharts'
import { predictionsApi } from '../api'

const RISK_COLORS = { High: '#ef4444', Medium: '#f59e0b', Low: '#10b981' }

function RiskBar({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color = pct >= 65 ? '#ef4444' : pct >= 35 ? '#f59e0b' : '#10b981'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-[#162032] rounded-full h-1.5">
        <div className="h-1.5 rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="text-xs w-8 text-right" style={{ color }}>{pct}%</span>
    </div>
  )
}

export default function Predictions() {
  const [predictions, setPredictions] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    Promise.all([
      predictionsApi.getAll({ limit: 200 }),
      predictionsApi.getSummary(),
    ]).then(([listRes, sumRes]) => {
      setPredictions(listRes.data)
      setSummary(sumRes.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filtered = filter
    ? predictions.filter((p) => p.risk_label === filter)
    : predictions

  if (loading) return <div className="flex items-center justify-center h-64 text-[#8b9ab0]">Scoring shipments...</div>

  const distData = summary
    ? [
        { label: 'High', count: summary.high_risk, pct: summary.high_pct },
        { label: 'Medium', count: summary.medium_risk, pct: summary.medium_pct },
        { label: 'Low', count: summary.low_risk, pct: summary.low_pct },
      ]
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-white">Delay Predictions</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">RandomForest model — scored on carrier, route, transit days, and seasonality</p>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Scored</div>
            <div className="text-3xl font-bold text-white">{summary.total_scored}</div>
          </div>
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">High Risk</div>
            <div className="text-3xl font-bold text-red-400">{summary.high_risk}</div>
            <div className="text-xs text-[#8b9ab0] mt-1">{summary.high_pct}% of fleet</div>
          </div>
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Medium Risk</div>
            <div className="text-3xl font-bold text-amber-400">{summary.medium_risk}</div>
            <div className="text-xs text-[#8b9ab0] mt-1">{summary.medium_pct}%</div>
          </div>
          <div className="card p-4">
            <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">Avg Risk Score</div>
            <div className="text-3xl font-bold text-[#10b981]">{(summary.avg_delay_risk_score * 100).toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Distribution chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={distData}>
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#8b9ab0' }} />
              <YAxis tick={{ fontSize: 10, fill: '#8b9ab0' }} />
              <Tooltip
                contentStyle={{ background: '#0f1923', border: '1px solid #1e2a3a', borderRadius: 6, fontSize: 12 }}
                formatter={(v, name) => [v, 'Shipments']}
              />
              <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                {distData.map((d, i) => <Cell key={i} fill={RISK_COLORS[d.label]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Model Details</h3>
          <div className="space-y-2 text-xs">
            {[
              ['Algorithm', 'RandomForestClassifier'],
              ['Estimators', '100'],
              ['Features', 'carrier, origin, dest, weather, transit days, month'],
              ['Target', 'delay > 4 hours'],
              ['Class Weight', 'balanced'],
              ['High Risk Threshold', '≥ 65%'],
              ['Medium Risk Threshold', '35% – 65%'],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="text-[#8b9ab0]">{k}</span>
                <span className="text-gray-300 text-right max-w-[55%] truncate">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Predictions table */}
      <div className="card">
        <div className="px-4 py-3 border-b border-[#1e2a3a] flex items-center gap-3 flex-wrap">
          <h3 className="text-sm font-semibold text-white flex-1">Shipment Risk Scores</h3>
          {['', 'High', 'Medium', 'Low'].map((r) => (
            <button
              key={r}
              onClick={() => setFilter(r)}
              className={`text-xs px-3 py-1 rounded border transition-colors ${
                filter === r
                  ? 'bg-[#10b981]/10 border-[#10b981]/30 text-[#10b981]'
                  : 'border-[#1e2a3a] text-[#8b9ab0] hover:text-gray-200'
              }`}
            >
              {r || 'All'}
            </button>
          ))}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
                <th className="text-left px-4 py-2">Shipment</th>
                <th className="text-left px-4 py-2 hidden md:table-cell">Carrier</th>
                <th className="text-left px-4 py-2 hidden lg:table-cell">Route</th>
                <th className="text-left px-4 py-2">Status</th>
                <th className="text-left px-4 py-2">Risk</th>
                <th className="px-4 py-2 w-48">Delay Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={p.id} className="table-row">
                  <td className="px-4 py-2.5 font-mono text-xs text-gray-300">{p.shipment_id}</td>
                  <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden md:table-cell">{p.carrier}</td>
                  <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden lg:table-cell truncate max-w-[160px]">
                    {p.origin?.split(',')[0]} → {p.destination?.split(',')[0]}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`badge badge-${p.status}`}>{p.status.replace('_', ' ')}</span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`badge risk-${p.risk_label}`}>{p.risk_label}</span>
                  </td>
                  <td className="px-4 py-2.5">
                    <RiskBar score={p.delay_risk_score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="p-8 text-center text-[#8b9ab0] text-sm">No predictions for selected filter.</div>
          )}
        </div>
      </div>
    </div>
  )
}

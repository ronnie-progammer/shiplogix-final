import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { dashboardApi } from '../api'

const STATUS_COLORS = {
  delivered: '#10b981',
  in_transit: '#3b82f6',
  delayed: '#ef4444',
  at_risk: '#f59e0b',
}

const RISK_COLORS = { High: '#ef4444', Medium: '#f59e0b', Low: '#10b981' }

function StatCard({ label, value, color, sub }) {
  return (
    <div className="card p-4">
      <div className="text-xs text-[#8b9ab0] uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-3xl font-bold ${color}`}>{value ?? '—'}</div>
      {sub && <div className="text-xs text-[#8b9ab0] mt-1">{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    dashboardApi.getStats()
      .then((r) => { setStats(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-[#8b9ab0]">Loading dashboard...</div>
  if (!stats) return <div className="text-red-400 p-4">Failed to load. Is the backend running? <code>cd backend && uvicorn main:app --reload</code></div>

  const statusPieData = (stats.status_breakdown || []).map((d) => ({
    name: d.status.replace('_', ' '),
    value: d.count,
    color: STATUS_COLORS[d.status] || '#8b9ab0',
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-white">Operations Overview</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">Real-time supply chain visibility</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <div className="col-span-2 sm:col-span-2">
          <StatCard label="Total Shipments" value={stats.total_shipments} color="text-white" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="In Transit" value={stats.in_transit} color="text-blue-400" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="Delayed" value={stats.delayed} color="text-red-400" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="At Risk" value={stats.at_risk} color="text-amber-400" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="Delivered" value={stats.delivered} color="text-emerald-400" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="On-Time Rate" value={`${stats.on_time_rate}%`} color="text-emerald-400" />
        </div>
        <div className="col-span-1 sm:col-span-1">
          <StatCard label="Anomalies" value={stats.anomaly_count} color="text-red-400" />
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Shipment volume trend */}
        <div className="card p-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-white mb-4">Shipment Volume — Last 14 Days</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={stats.shipments_by_day}>
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#8b9ab0' }} tickFormatter={(v) => v.slice(5)} />
              <YAxis tick={{ fontSize: 10, fill: '#8b9ab0' }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: '#0f1923', border: '1px solid #1e2a3a', borderRadius: 6, fontSize: 12 }}
                labelStyle={{ color: '#8b9ab0' }}
                itemStyle={{ color: '#10b981' }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status breakdown pie */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-4">Status Breakdown</h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={statusPieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={68}
                label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                labelLine={false}
                fontSize={9}
              >
                {statusPieData.map((d, i) => <Cell key={i} fill={d.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#0f1923', border: '1px solid #1e2a3a', borderRadius: 6, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2 justify-center">
            {statusPieData.map((d) => (
              <span key={d.name} className="flex items-center gap-1 text-[10px] text-[#8b9ab0]">
                <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                {d.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Risk dist + carrier summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Risk distribution */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-white mb-4">AI Delay Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={stats.risk_distribution} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 10, fill: '#8b9ab0' }} />
              <YAxis dataKey="label" type="category" tick={{ fontSize: 11, fill: '#8b9ab0' }} width={50} />
              <Tooltip
                contentStyle={{ background: '#0f1923', border: '1px solid #1e2a3a', borderRadius: 6, fontSize: 12 }}
                itemStyle={{ color: '#10b981' }}
              />
              <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                {(stats.risk_distribution || []).map((d, i) => (
                  <Cell key={i} fill={RISK_COLORS[d.label] || '#8b9ab0'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Carrier summary */}
        <div className="card">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#1e2a3a]">
            <h3 className="text-sm font-semibold text-white">Carrier Performance</h3>
            <button onClick={() => navigate('/carriers')} className="text-xs text-[#10b981] hover:underline">View all</button>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
                <th className="text-left px-4 py-2">Carrier</th>
                <th className="text-right px-4 py-2">Shipments</th>
                <th className="text-right px-4 py-2">On-Time</th>
              </tr>
            </thead>
            <tbody>
              {(stats.carrier_summary || []).map((c) => (
                <tr key={c.carrier} className="table-row">
                  <td className="px-4 py-2 text-gray-300 text-xs">{c.carrier}</td>
                  <td className="px-4 py-2 text-right text-[#8b9ab0] text-xs">{c.total}</td>
                  <td className="px-4 py-2 text-right text-xs">
                    <span className={c.on_time_rate >= 85 ? 'text-emerald-400' : c.on_time_rate >= 70 ? 'text-amber-400' : 'text-red-400'}>
                      {c.on_time_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent anomalies */}
      {(stats.recent_anomalies || []).length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#1e2a3a]">
            <h3 className="text-sm font-semibold text-white">Recent Anomalies</h3>
            <button onClick={() => navigate('/anomalies')} className="text-xs text-[#10b981] hover:underline">View all</button>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
                <th className="text-left px-4 py-2">Shipment</th>
                <th className="text-left px-4 py-2 hidden md:table-cell">Route</th>
                <th className="text-left px-4 py-2">Carrier</th>
                <th className="text-left px-4 py-2">Delay</th>
                <th className="text-left px-4 py-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_anomalies.map((a) => (
                <tr key={a.id} className="table-row" onClick={() => navigate('/anomalies')}>
                  <td className="px-4 py-2.5 text-gray-300 font-mono text-xs">{a.shipment_id}</td>
                  <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden md:table-cell truncate max-w-xs">
                    {a.origin} → {a.destination}
                  </td>
                  <td className="px-4 py-2.5 text-[#8b9ab0] text-xs">{a.carrier}</td>
                  <td className="px-4 py-2.5 text-amber-400 text-xs">{a.delay_hours}h</td>
                  <td className="px-4 py-2.5">
                    <span className={`badge risk-${a.risk_label}`}>{a.risk_label}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

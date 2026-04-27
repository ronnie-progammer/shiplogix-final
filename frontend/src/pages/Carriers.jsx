import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { carriersApi } from '../api'

function OnTimeBar({ rate }) {
  const color = rate >= 85 ? '#10b981' : rate >= 70 ? '#f59e0b' : '#ef4444'
  return (
    <div className="w-full bg-[#162032] rounded-full h-1.5 mt-1">
      <div className="h-1.5 rounded-full transition-all" style={{ width: `${rate}%`, background: color }} />
    </div>
  )
}

export default function Carriers() {
  const [carriers, setCarriers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carriersApi.getAll()
      .then((r) => { setCarriers(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-[#8b9ab0]">Loading carriers...</div>

  const chartData = [...carriers]
    .sort((a, b) => b.on_time_rate - a.on_time_rate)
    .map((c) => ({ name: c.carrier.replace(' ', '\n'), rate: c.on_time_rate }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-white">Carrier Scorecards</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">{carriers.length} carriers ranked by on-time performance</p>
      </div>

      {/* On-time rate chart */}
      <div className="card p-4">
        <h3 className="text-sm font-semibold text-white mb-4">On-Time Rate by Carrier</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#8b9ab0' }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#8b9ab0' }} unit="%" />
            <Tooltip
              contentStyle={{ background: '#0f1923', border: '1px solid #1e2a3a', borderRadius: 6, fontSize: 12 }}
              formatter={(v) => [`${v}%`, 'On-Time Rate']}
            />
            <Bar dataKey="rate" radius={[3, 3, 0, 0]}>
              {chartData.map((d, i) => (
                <Cell key={i} fill={d.rate >= 85 ? '#10b981' : d.rate >= 70 ? '#f59e0b' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Carrier grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {carriers.map((c) => (
          <div key={c.carrier} className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-white">{c.carrier}</span>
              <span className={`text-lg font-bold ${c.on_time_rate >= 85 ? 'text-emerald-400' : c.on_time_rate >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
                {c.on_time_rate}%
              </span>
            </div>
            <OnTimeBar rate={c.on_time_rate} />
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <div className="text-[#8b9ab0]">Total</div>
                <div className="text-white font-semibold">{c.total_shipments}</div>
              </div>
              <div>
                <div className="text-[#8b9ab0]">Delivered</div>
                <div className="text-white font-semibold">{c.delivered_count}</div>
              </div>
              <div>
                <div className="text-[#8b9ab0]">In Transit</div>
                <div className="text-blue-400 font-semibold">{c.in_transit_count}</div>
              </div>
              <div>
                <div className="text-[#8b9ab0]">Delayed</div>
                <div className="text-red-400 font-semibold">{c.delayed_count}</div>
              </div>
              <div>
                <div className="text-[#8b9ab0]">Avg Delay</div>
                <div className={`font-semibold ${c.avg_delay_hours > 8 ? 'text-red-400' : c.avg_delay_hours > 4 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {c.avg_delay_hours}h
                </div>
              </div>
              <div>
                <div className="text-[#8b9ab0]">Anomalies</div>
                <div className={`font-semibold ${c.anomaly_count > 0 ? 'text-red-400' : 'text-[#8b9ab0]'}`}>{c.anomaly_count}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

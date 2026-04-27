import { useState, useEffect } from 'react'
import { routesApi } from '../api'

export default function Routes() {
  const [routes, setRoutes] = useState([])
  const [loading, setLoading] = useState(true)
  const [sort, setSort] = useState('total')

  useEffect(() => {
    routesApi.getAll()
      .then((r) => { setRoutes(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-[#8b9ab0]">Loading routes...</div>

  const sorted = [...routes].sort((a, b) => {
    if (sort === 'total') return b.total_shipments - a.total_shipments
    if (sort === 'on_time') return b.on_time_rate - a.on_time_rate
    if (sort === 'delay') return b.avg_delay_hours - a.avg_delay_hours
    return 0
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-lg font-semibold text-white">Routes</h1>
          <p className="text-xs text-[#8b9ab0] mt-0.5">{routes.length} active routes</p>
        </div>
        <div className="flex gap-2">
          {[
            { key: 'total', label: 'By Volume' },
            { key: 'on_time', label: 'By On-Time' },
            { key: 'delay', label: 'By Delay' },
          ].map((opt) => (
            <button
              key={opt.key}
              onClick={() => setSort(opt.key)}
              className={`text-xs px-3 py-1.5 rounded-md border transition-colors ${
                sort === opt.key
                  ? 'bg-[#10b981]/10 border-[#10b981]/30 text-[#10b981]'
                  : 'border-[#1e2a3a] text-[#8b9ab0] hover:text-gray-200 hover:bg-[#162032]'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[10px] uppercase text-[#8b9ab0] border-b border-[#162032]">
              <th className="text-left px-4 py-3">Origin</th>
              <th className="text-left px-4 py-3">Destination</th>
              <th className="text-right px-4 py-3">Shipments</th>
              <th className="text-right px-4 py-3">Delivered</th>
              <th className="text-right px-4 py-3">On-Time</th>
              <th className="text-right px-4 py-3">Avg Delay</th>
              <th className="text-left px-4 py-3 hidden lg:table-cell">Top Carrier</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => (
              <tr key={i} className="table-row">
                <td className="px-4 py-2.5 text-gray-300 text-xs">{r.origin}</td>
                <td className="px-4 py-2.5 text-gray-300 text-xs">{r.destination}</td>
                <td className="px-4 py-2.5 text-right text-white text-xs font-semibold">{r.total_shipments}</td>
                <td className="px-4 py-2.5 text-right text-[#8b9ab0] text-xs">{r.delivered_count}</td>
                <td className="px-4 py-2.5 text-right text-xs">
                  <span className={r.on_time_rate >= 80 ? 'text-emerald-400' : r.on_time_rate >= 60 ? 'text-amber-400' : 'text-red-400'}>
                    {r.on_time_rate}%
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right text-xs">
                  <span className={r.avg_delay_hours > 8 ? 'text-red-400' : r.avg_delay_hours > 4 ? 'text-amber-400' : 'text-emerald-400'}>
                    {r.avg_delay_hours}h
                  </span>
                </td>
                <td className="px-4 py-2.5 text-[#8b9ab0] text-xs hidden lg:table-cell">{r.most_used_carrier}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

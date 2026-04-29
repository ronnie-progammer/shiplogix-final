import { useEffect, useState } from 'react'
import { billingApi } from '../api'

export default function Billing() {
  const [tiers, setTiers] = useState([])
  const [subscription, setSubscription] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(null)

  useEffect(() => {
    billingApi.listTiers().then((r) => setTiers(r.data.tiers)).catch(() => {})
    billingApi.getSubscription().then((r) => setSubscription(r.data)).catch(() => {})
  }, [])

  async function upgrade(tier) {
    setBusy(tier)
    setError('')
    try {
      const r = await billingApi.checkout(tier)
      window.location.href = r.data.url
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? 'Checkout failed')
    } finally {
      setBusy(null)
    }
  }

  async function openPortal() {
    setBusy('portal')
    setError('')
    try {
      const r = await billingApi.portal()
      window.location.href = r.data.url
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? 'Portal failed')
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-white">Billing & Plans</h1>
        <p className="text-xs text-[#8b9ab0] mt-0.5">
          {subscription
            ? <>Current plan: <span className="text-[#10b981] font-semibold uppercase">{subscription.tier}</span> · {subscription.source === 'mock' ? 'mock mode' : 'live'}</>
            : 'Loading subscription…'}
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-md px-3 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {tiers.map((t) => {
          const isCurrent = subscription?.tier === t.id
          return (
            <div
              key={t.id}
              className={`card p-4 space-y-3 ${isCurrent ? 'border-[#10b981]/40' : ''}`}
            >
              <div>
                <div className="text-xs text-[#8b9ab0] uppercase">{t.id}</div>
                <div className="text-2xl font-semibold text-white mt-1">
                  ${t.price_usd}<span className="text-sm text-[#8b9ab0]">/mo</span>
                </div>
                <div className="text-xs text-[#8b9ab0] mt-1">
                  {t.shipments_per_month.toLocaleString()} shipments / mo
                </div>
              </div>
              <ul className="space-y-1 text-xs text-gray-300">
                {t.features.map((f) => (
                  <li key={f}>· {f}</li>
                ))}
              </ul>
              {t.id === 'free' ? (
                <div className="text-xs text-[#8b9ab0] italic">Default tier</div>
              ) : isCurrent ? (
                <button
                  onClick={openPortal}
                  disabled={busy === 'portal'}
                  className="btn-secondary w-full text-xs disabled:opacity-50"
                >
                  {busy === 'portal' ? 'Opening…' : 'Manage subscription'}
                </button>
              ) : (
                <button
                  onClick={() => upgrade(t.id)}
                  disabled={busy === t.id}
                  className="btn-primary w-full text-xs disabled:opacity-50"
                >
                  {busy === t.id ? 'Redirecting…' : 'Upgrade'}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

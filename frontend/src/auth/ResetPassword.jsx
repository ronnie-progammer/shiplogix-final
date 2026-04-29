import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from './AuthContext'
import AuthShell from './AuthShell'

export default function ResetPassword() {
  const { sendPasswordReset, supabaseConfigured } = useAuth()
  const [email, setEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await sendPasswordReset(email)
      setDone(true)
    } catch (err) {
      setError(err.message ?? 'Could not send reset email')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Reset password"
      subtitle="We’ll send you a link to choose a new one"
      footer={<Link to="/login" className="text-[#10b981] hover:underline">Back to sign in</Link>}
    >
      {!supabaseConfigured && (
        <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-md px-3 py-2 text-xs text-amber-300">
          Supabase isn’t configured. Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code>.
        </div>
      )}
      {done ? (
        <div className="text-sm text-emerald-300">
          If an account exists for <strong>{email}</strong>, a reset link is on its way.
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs text-[#8b9ab0] mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              placeholder="you@company.com"
            />
          </div>
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-md px-3 py-2 text-xs text-red-300">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={submitting || !supabaseConfigured}
            className="btn-primary w-full disabled:opacity-50"
          >
            {submitting ? 'Sending…' : 'Send reset link'}
          </button>
        </form>
      )}
    </AuthShell>
  )
}

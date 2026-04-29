import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import AuthShell from './AuthShell'

export default function Signup() {
  const { signUp, supabaseConfigured } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const result = await signUp(email, password)
      if (result?.session) {
        navigate('/', { replace: true })
      } else {
        setDone(true)
      }
    } catch (err) {
      setError(err.message ?? 'Signup failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Create account"
      subtitle="Start monitoring shipments in minutes"
      footer={<>Already have one? <Link to="/login" className="text-[#10b981] hover:underline">Sign in</Link></>}
    >
      {!supabaseConfigured && (
        <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-md px-3 py-2 text-xs text-amber-300">
          Supabase isn’t configured. Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code>.
        </div>
      )}
      {done ? (
        <div className="text-sm text-emerald-300">
          Check your inbox to confirm <strong>{email}</strong>.
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
          <div>
            <label className="block text-xs text-[#8b9ab0] mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full"
              placeholder="At least 8 characters"
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
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
      )}
    </AuthShell>
  )
}

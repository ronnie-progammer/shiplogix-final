import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import AuthShell from './AuthShell'

export default function Login() {
  const { signIn, supabaseConfigured } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = location.state?.from?.pathname ?? '/'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await signIn(email, password)
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err.message ?? 'Sign in failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Sign in"
      subtitle="Use your ShipLogix account to access the dashboard"
      footer={<>New here? <Link to="/signup" className="text-[#10b981] hover:underline">Create an account</Link></>}
    >
      {!supabaseConfigured && (
        <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-md px-3 py-2 text-xs text-amber-300">
          Supabase isn’t configured. Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code>.
        </div>
      )}
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
          <div className="flex justify-between items-baseline">
            <label className="block text-xs text-[#8b9ab0] mb-1">Password</label>
            <Link to="/reset-password" className="text-[10px] text-[#8b9ab0] hover:text-[#10b981]">Forgot?</Link>
          </div>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input w-full"
            placeholder="••••••••"
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
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </AuthShell>
  )
}
